import os
import hmac
import numpy as np
import pandas as pd
from datetime import datetime
import streamlit as st
from sqlalchemy import create_engine

from dotenv import load_dotenv
from streamlit.logger import get_logger

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

def stream_data():
    engine = create_engine(f"postgresql://postgres:DsRdPPJtetGDiMFypvHpUJUKAwEXfoSG@junction.proxy.rlwy.net:19704/PHOMA")
    df = pd.read_sql(f""" SELECT 
            "timestamp","duration", "InoculationTime", 
            "CTR_PV [mMol/h]", 
            "DO_Out [%%]", "DO_PV [%%DO]", "DO_SP [%%DO]", 
            "F_Out [sL/h]", "F_PV [sL/h]", "F_SP [sL/h]", "FA_PV [mL/h]", "FA_SP [mL/h]", "FAir_PV [sL/h]", "FAir_SP [sL/h]", 
            "FB_PV [mL/h]", "FB_SP [mL/h]", "FCO2_PV [sL/h]", "FCO2_SP [sL/h]", "FN2_PV [sL/h]", "FN2_SP [sL/h]", "FO2_PV [sL/h]", 
            "FO2_SP [sL/h]", "N_PV [rpm]", "N_SP [rpm]", "OTR_PV [mMol/h]", 
            "pH_Out [%%]", "pH_PV [pH]", "pH_SP [pH]", 
            "RQ_PV []", 
            "T_Out [%%]", "T_PV [°C]", "T_SP [°C]", 
            "VA_PV [mL]", "VB_PV [mL]", 
            "XCO2_Out [%%]", "XCO2_PV [%%]", "XCO2_SP [%%]", "XO2_Out [%%]", "XO2_PV [%%]", "XO2_SP [%%]", 
            "vessel"
    FROM "STREAM_dasgip" """, con=engine)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df



st.write("# stream data")
df = stream_data()

st.markdown(f"""
    <p>rows of data:<br/> {len(df.index)} </p>
    <p>min() timestamp:<br/> {df['timestamp'].min()} </p>
    <p>max() timestamp:<br/> {df['timestamp'].max()} </p>
    <p>unique() vessels (aka. batches):<br/> {df['vessel'].unique()} </p>
""", unsafe_allow_html=True)

st.write(f"data columns")
st.write(df.columns)

uploaded_file = st.file_uploader("upload the dasgip manual export CSV")
batch_name = st.text_input("enter batch name",)
all_data_dfs = []
if (uploaded_file is not None) and (batch_name is not None):

    dataframe = pd.read_excel(uploaded_file, #sheet_name=sheet_name,
    usecols='A:BG',
    names=['timestamp','duration','InoculationTime','BalA_MPV [g]','CTR_PV [mMol/h]','DO_Out [%]','DO_PV [%DO]','DO_SP [%DO]',
    'ExtIOA_ExtIOAIn','ExtIOA_ExtIOAOut','ExtIOB_ExtIOBIn','ExtIOB_ExtIOBOut','ExtIOC_ExtIOCIn','ExtIOC_ExtIOCOut',
    'F_Out [sL/h]','F_PV [sL/h]','F_SP [sL/h]','FA_PV [mL/h]','FA_SP [mL/h]',
    'FAir_PV [sL/h]','FAir_SP [sL/h]','FB_PV [mL/h]','FB_SP [mL/h]',
    'FCO2_PV [sL/h]', 'FCO2_SP [sL/h]', 'FN2_PV [sL/h]', 'FN2_SP [sL/h]', 'FO2_PV [sL/h]', 'FO2_SP [sL/h]',
    'InternalA_InternalA', 'InternalB_InternalB','InternalC_InternalC','InternalD_InternalD',
    'N_PV [rpm]','N_SP [rpm]','N_TStirPV [mNm]','OfflineA_OfflineA','OfflineB_OfflineB','OfflineC_OfflineC','OfflineD_OfflineD',
    'OTR_PV [mMol/h]','pH_Out [%]','pH_PV [pH]','pH_SP [pH]','RQ_PV []',
    'T_Out [%]','T_PV [°C]','T_SP [°C]','V_VPV [mL]','VA_PV [mL]','VB_PV [mL]','VCT_PV [mMol]','VOT_PV [mMol]',
    'XCO2_Out [%]','XCO2_PV [%]','XCO2_SP [%]','XO2_Out [%]','XO2_PV [%]','XO2_SP [%]',
    ])
    dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
    dataframe['duration'] = dataframe['duration'] / np.timedelta64(1, 'h')
    dataframe['InoculationTime'] = dataframe['InoculationTime'] / np.timedelta64(1, 'h')
    dataframe['vessel'] = batch_name
    all_data_dfs.append(dataframe)

    df = pd.concat(all_data_dfs, ignore_index=True)
    print(df.info())
    df.to_csv("full_dasgip.csv", index=False)
    print(f"upload start: {datetime.now()}")
    df = df.sort_values('timestamp')
    #engine = create_engine(f"postgresql://postgres:DsRdPPJtetGDiMFypvHpUJUKAwEXfoSG@junction.proxy.rlwy.net:19704/PHOMA")
    #df.to_sql(f"STREAM_dasgip", con=engine, index=False, if_exists='replace')
    st.write(df.head(3))
st.divider()

