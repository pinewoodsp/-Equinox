def inject_css(char_color: str):
    st.markdown(f"""
    <style>
    .stApp {{
        background-color: #0A0A0F;
    }}
    </style>
    """, unsafe_allow_html=True)

inject_css("#C9A84C")
st.title("2단계 테스트")
st.write("CSS 적용 후에도 보이면 정상")
