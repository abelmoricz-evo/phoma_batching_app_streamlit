import os
import hmac
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

session_state = st.session_state

load_dotenv()


def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], os.environ.get("STREAMLIT_PASSWORD", "")):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True
    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


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
    st.write(df[['timestamp', 'Sample name', 'batch_name', 'Macrocidins_Tot', 'Pre-A', 'Factor A', 'Factor Z', 'Post-Z', ]])

    st.markdown(f"""
        <p>min() timestamp:<br/> {df['timestamp'].min()} </p>
        <p>max() timestamp:<br/> {df['timestamp'].max()} </p>
        <p>batch names:<br/> {df['batch_name'].unique()} </p>
    """, unsafe_allow_html=True)

    if st.button("batch this offline data with available stream data"):
        st.write("thank you data is uploaded: ")
        st.badge("successfully", icon=":material/check:", color="green")