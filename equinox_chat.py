import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.title("사용 가능한 Groq 모델 목록")

models = client.models.list()
for m in models.data:
    st.write(m.id)
