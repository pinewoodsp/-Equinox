import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="EQUINOX", page_icon="⚔️", layout="wide")

st.title("1단계 테스트")
st.write("여기까지 보이면 정상")
