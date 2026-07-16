# =============================================================
# ~/bigdata202/fastapi//Streamlit/04_dataframe.py
#
#  Streamlit 라이브러리 기초 실습
#
#  - 판다스 데이터프레임 활용
# ===========================================================
import streamlit as st
import pandas as pd

df_menu = pd.DataFrame({
    "메뉴명": ['아메리카노', '카페라떼', '카푸치노', '말차라떼'],
    "가격": [4500, 5000, 5500, 6000]
})

# 테이블
st.table(df_menu)

st.write('---')

# 데이터프레임
st.dataframe(df_menu)

st.write('---')

st.dataframe(df_menu, height=300, width=600)
st.dataframe(df_menu, height=200, width='stretch') # 전체 너비
st.dataframe(df_menu, height=300, width='content') # 원본 크기