import os
import hmac
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from utils import check_password
from sqlalchemy import create_engine
from streamlit.logger import get_logger

session_state = st.session_state

load_dotenv()

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

col1, col2 = st.columns(2)
with col1:
    st.code(f"""
        rows of data:{len(df.index)}
        min() timestamp: {df['timestamp'].min()}
        max() timestamp: {df['timestamp'].max()}
        unique() vessels (aka. batches): {df['vessel'].unique()}
    """, language="python", line_numbers=True, wrap_lines=True, )

with col2:
    st.write(f"data columns")
    st.write(df.columns)

# PM2.2_25_1 - 4

uploaded_file = st.file_uploader("upload the dasgip manual export CSV")
batch_name = st.text_input("enter batch name", )
all_data_dfs = []

if st.button("batch it"):
    if (uploaded_file is not None) and (batch_name is not None):
        st.code("processing data...")
        dataframe = pd.read_excel(uploaded_file,  sheet_name='Data1',
            usecols='A:BG',
            names=['timestamp', 'duration', 'InoculationTime', 'BalA_MPV [g]', 'CTR_PV [mMol/h]', 'DO_Out [%]', 'DO_PV [%DO]', 'DO_SP [%DO]',
                'ExtIOA_ExtIOAIn', 'ExtIOA_ExtIOAOut', 'ExtIOB_ExtIOBIn', 'ExtIOB_ExtIOBOut', 'ExtIOC_ExtIOCIn', 'ExtIOC_ExtIOCOut',
                'F_Out [sL/h]', 'F_PV [sL/h]', 'F_SP [sL/h]', 'FA_PV [mL/h]', 'FA_SP [mL/h]',
                'FAir_PV [sL/h]', 'FAir_SP [sL/h]', 'FB_PV [mL/h]', 'FB_SP [mL/h]',
                'FCO2_PV [sL/h]', 'FCO2_SP [sL/h]', 'FN2_PV [sL/h]', 'FN2_SP [sL/h]', 'FO2_PV [sL/h]', 'FO2_SP [sL/h]',
                'InternalA_InternalA', 'InternalB_InternalB', 'InternalC_InternalC', 'InternalD_InternalD',
                'N_PV [rpm]', 'N_SP [rpm]', 'N_TStirPV [mNm]', 'OfflineA_OfflineA', 'OfflineB_OfflineB', 'OfflineC_OfflineC', 'OfflineD_OfflineD',
                'OTR_PV [mMol/h]', 'pH_Out [%]', 'pH_PV [pH]', 'pH_SP [pH]', 'RQ_PV []',
                'T_Out [%]', 'T_PV [°C]', 'T_SP [°C]', 'V_VPV [mL]', 'VA_PV [mL]', 'VB_PV [mL]', 'VCT_PV [mMol]', 'VOT_PV [mMol]',
                'XCO2_Out [%]', 'XCO2_PV [%]', 'XCO2_SP [%]', 'XO2_Out [%]', 'XO2_PV [%]', 'XO2_SP [%]',
            ])
        dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
        dataframe['duration'] = dataframe['duration'] / np.timedelta64(1, 'h')
        dataframe['InoculationTime'] = dataframe['InoculationTime'] / np.timedelta64(1, 'h')
        dataframe['vessel'] = batch_name
        all_data_dfs.append(dataframe)

        df = pd.concat(all_data_dfs, ignore_index=True)
        df.to_csv("full_dasgip.csv", index=False)
        df = df.sort_values('timestamp')
        engine = create_engine(f"postgresql://postgres:DsRdPPJtetGDiMFypvHpUJUKAwEXfoSG@junction.proxy.rlwy.net:19704/PHOMA")
        df.to_sql(f"STREAM_dasgip", con=engine, index=False, if_exists='append')
        st.write(df.head(3))
