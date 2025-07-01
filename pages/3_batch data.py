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
    engine = create_engine(f"postgresql://phoma:WD80WD80@junction.proxy.rlwy.net:19704/PHOMA")
    return pd.read_sql(f""" SELECT distinct vessel FROM "STREAM_dasgip" """, con=engine)



def get_batch_stream_data(batch_name):
    engine = create_engine(f"postgresql://phoma:WD80WD80@junction.proxy.rlwy.net:19704/PHOMA")
    return pd.read_sql(f""" SELECT * FROM "STREAM_dasgip" WHERE vessel = '{batch_name}' """, con=engine)


def get_batch_offline_data(batch_name):
    engine = create_engine(f"postgresql://phoma:WD80WD80@junction.proxy.rlwy.net:19704/PHOMA")
    return pd.read_sql(f""" SELECT * FROM "OFFLINE" WHERE batch_name = '{batch_name}' """, con=engine)

def display_columns(stream_batch_df, offline_batch_df):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"STREAM data rows: {len(stream_batch_df.index)}")
        st.write(f"STREAM min: {stream_batch_df['timestamp'].min()}")
        st.write(f"STREAM max: {stream_batch_df['timestamp'].max()}")
        st.dataframe(stream_batch_df)
    with col2:
        st.write(f"OFFLINE data rows: {len(offline_batch_df.index)}")
        st.write(f"OFFLINE min: {offline_batch_df['timestamp'].min()}")
        st.write(f"OFFLINE max: {offline_batch_df['timestamp'].max()}")
        st.dataframe(offline_batch_df)

if __name__ == "__main__":
    st.header("batch data", divider=True)

    batch_names = get_batch_names()
    batch = st.selectbox("select offline batch name", list(batch_names['vessel']))

    if st.button("find stream data for this batch"):
        st.write(f"thank you for selecting: {batch}")
        stream_batch_df = get_batch_stream_data(batch)
        offline_batch_df = get_batch_offline_data(batch)
        st.session_state.stream_batch_df = stream_batch_df
        st.session_state.offline_batch_df = offline_batch_df

        display_columns(stream_batch_df, offline_batch_df)

    if st.button("batch this data now (creating a new table in schema 'batches' "):
        stream_batch_df = st.session_state.stream_batch_df
        stream_batch_df['timestamp'] = stream_batch_df['timestamp'].dt.round('min')
        offline_batch_df = st.session_state.offline_batch_df
        offline_batch_df['timestamp'] = offline_batch_df['timestamp'].dt.round('min')

        display_columns(stream_batch_df, offline_batch_df)

        st.write("merging data...")

        df = pd.merge(stream_batch_df, offline_batch_df, left_on=['vessel', 'timestamp'], right_on=['batch_name', 'timestamp'], how='outer', suffixes=('_STREAM', '_OFFLINE'))
        st.badge("successfully", icon=":material/check:", color="green")
        df.sort_values('timestamp', inplace=True)
        df['duration [ days ]'] = (df['timestamp'] - df['timestamp'].min()).dt.seconds / 60 / 60 / 24
        df['duration [ seconds ]'] = (df['timestamp'] - df['timestamp'].min()).dt.seconds
        st.dataframe(df)


        st.write("uploading to db...")
        engine = create_engine(f"postgresql://postgres:DsRdPPJtetGDiMFypvHpUJUKAwEXfoSG@junction.proxy.rlwy.net:19704/PHOMA")
        df.to_sql(f"{batch}",con=engine, schema='batches', if_exists='replace',)
        st.badge("successfully", icon=":material/check:", color="green")

        st.write("plotting all numeric columns...")
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        num_columns = df.select_dtypes(include=numerics).columns
        fig = px.scatter(df, x='timestamp',y=num_columns)
        st.plotly_chart(fig)

