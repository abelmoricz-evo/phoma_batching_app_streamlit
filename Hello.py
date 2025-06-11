import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)

def run():
    st.write("# welcome to Phoma Data 👋")
    st.divider()

    st.write("### batching")
    st.page_link("pages/stream data.py", label="stream data", icon="🏠")
    st.page_link("pages/offline data.py", label="offline data", icon="🏠")
    st.divider()

    st.write("### data after batching")
    st.markdown(f""" 
        Grafana: <a href="https://grafanapro-production.up.railway.app/dashboards/f/eeo0zlihtybk0e/phoma">dahsboards</a></li> 
        
        :violet-badge[user] evologic :violet-badge[password] 43oMa0-At19z0-75Kn$#7b 
        <br />
    """, unsafe_allow_html=True)


    st.write("##### get (READ ONLY) access to batched data")
    st.markdown(""" :violet-badge[host] junction.proxy.rlwy.net :violet-badge[port] 19704 """, unsafe_allow_html=True)
    st.markdown(""" :violet-badge[user] phoma :violet-badge[password] WD80WD80  """, unsafe_allow_html=True)
    st.markdown(""" :violet-badge[database] PHOMA """, unsafe_allow_html=True)
    st.divider()

    st.write("### Data Flow Tool scope")
    st.image("data world map.jpg", caption="data world map (draw.io)")




if __name__ == "__main__":
    run()