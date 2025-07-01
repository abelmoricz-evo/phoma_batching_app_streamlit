import os
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
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


def get_batch_names():
    engine = create_engine(f"postgresql://postgres:DsRdPPJtetGDiMFypvHpUJUKAwEXfoSG@junction.proxy.rlwy.net:19704/PHOMA")
    return pd.read_sql(f""" select * from information_schema.tables where table_schema = 'batches' """, con=engine)


if __name__ == "__main__":
    st.header("condensed data", divider=True)
    engine = create_engine(f"postgresql://postgres:DsRdPPJtetGDiMFypvHpUJUKAwEXfoSG@junction.proxy.rlwy.net:19704/PHOMA")

    df = get_batch_names()
    st.dataframe(df)

    if st.button("condense batches"):
        st.write("condensing batches...")
        dfs = []
        for table_name in df['table_name']:
            ddf = pd.read_sql(f""" SELECT * FROM "batches"."{table_name}" """, engine)
            ddf['batch_name'] = table_name
            dfs.append(ddf)
        all_batches = pd.concat(dfs, axis=0)
        st.dataframe(all_batches)
        # st.write(all_batches.columns)

        # st.write(all_batches['Macrocidins_Tot  (mg/mL)'].unique())
        for column in ['Macrocidins_Tot  (mg/mL)', 'Pre-A (mg/mL)','Factor A  (mg/mL)','Factor Z  (mg/mL)','Post-Z  (mg/mL)']:
            all_batches[column] = all_batches[column].astype('float')
        st.write(all_batches.dtypes)
        condensed_df = all_batches.groupby('batch_name', as_index=True).agg({
            'Macrocidins_Tot  (mg/mL)': ['max', 'mean'],
            #'Pre-A  (mg/mL)': ['max', 'mean'],
            'Factor A  (mg/mL)': ['max', 'mean'],
            'Factor Z  (mg/mL)': ['max', 'mean'],
            'Post-Z  (mg/mL)': ['max', 'mean'],
            'DO_PV [%DO]': 'mean',
            'pH_PV [pH]': 'mean',
            'T_PV [°C]': 'mean',
        })
        st.write(condensed_df.dtypes)
        condensed_df.columns = [' '.join(col).strip() for col in condensed_df.columns.values]
        st.dataframe(condensed_df)
        st.badge("successfully", icon=":material/check:", color="green")

        st.write("uploading to db...")
        condensed_df = pd.DataFrame(condensed_df)
        condensed_df.to_sql(f"2025_batches", schema='condensed', con=engine, if_exists='replace')
        st.badge("successfully", icon=":material/check:", color="green")
