import os
import hmac
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from utils import check_password
from sqlalchemy import create_engine

session_state = st.session_state

load_dotenv()

if not int(float(os.environ['DEBUG'])):
    if not check_password():
        st.stop()

st.write(f"# offline data upload")

uploaded_file = st.file_uploader("upload the PM_Interactive_Template.xlsm file with the 'DataMatrix' sheet filled out")
if uploaded_file is not None:
    dataframe = pd.read_excel(uploaded_file, sheet_name="DataMatrix")
    st.write(f"raw data in the excel sheet:")
    st.write(dataframe)

    st.write(f"needed data after python data cleaning:")
    df = dataframe.copy(deep=True)
    df.columns = dataframe.iloc[0]
    df = df[1:]
    df['batch_name'] = df['Sample name'].str.rsplit('_').str[0:4]
    df['batch_name'] = ['_'.join(map(str, l)) for l in df['batch_name']]
    df['batch_name'] = df['batch_name'].str.rsplit('_').str[1:4]
    df['batch_name'] = ['_'.join(map(str, l)) for l in df['batch_name']]
    df = df.rename(columns={'Time Stamp': 'timestamp'})
    df = df[['timestamp', 'Sample name', 'batch_name',
        'Macrocidins_Tot  (mg/mL)', 'Pre-A (mg/mL)', 'Factor A  (mg/mL)', 'Factor Z  (mg/mL)', 'Post-Z  (mg/mL)',
        'Fructose (g/L)', 'Sucrose (g/L)', 'Glucose (g/L)', 'Glycerol (g/L)', 'CFU/mL harvest', 'CFU/Reactor volume (CFU/L)', 'Inoculated CFU', 'Inoculation viability (CFU/spore)', 'Treatment'
    ]]
    st.write(df)

    st.markdown(f"""
        <p>min() timestamp:<br/> {df['timestamp'].min()} </p>
        <p>max() timestamp:<br/> {df['timestamp'].max()} </p>
        <p>batch names:<br/> {df['batch_name'].unique()} </p>
    """, unsafe_allow_html=True)

    if st.button("batch this offline data with available stream data"):
        engine = create_engine(f"postgresql://postgres:DsRdPPJtetGDiMFypvHpUJUKAwEXfoSG@junction.proxy.rlwy.net:19704/PHOMA")
        df.to_sql(f"OFFLINE", con=engine, index=False, if_exists='append')
        st.write("thank you data is uploaded: ")
        st.badge("successfully", icon=":material/check:", color="green")
