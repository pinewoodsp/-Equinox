import streamlit as st
from groq import Groq

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

st.set_page_config(page_title="EQUINOX", page_icon="⚔️", layout="wide")

def inject_css(char_color: str):
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Noto Sans KR', sans-serif;
        background-color: #0A0A0F;
        color: #E8E8F0;
    }}
    .stApp {{
        background-color: #0A0A0F;
        background-image:
            radial-gradient(ellipse at 20% 20%, #12121E 0%, #0A0A0F 60%),
            repeating-linear-gradient(0deg, transparent, transparent 40px, #ffffff06 40px, #ffffff06 41px),
            repeating-linear-gradient(90deg, transparent, transparent 40px, #ffffff06 40px, #ffffff06 41px);
    }}
    </style>
    """, unsafe_allow_html=True)

inject_css("#C9A84C")
st.title("2단계 테스트")
st.write("CSS 적용 후에도 보이면 정상")
