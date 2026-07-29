# =============================================================
# ~/bigdata202/fastapi//Streamlit/10_yes_cache.py
#  Streamlit 라이브러리 기초 실습 / 실행 방법: streamlit run 파일이름
#  - 캐시가 있는 경우
# ===========================================================
import streamlit as st
import pandas as pd
import time

@st.cache_data
def load_subway_data():
    time.sleep(2) # 일부러 넣은거임 시간이 걸리려서 잠시 쉬게 한다.
    return pd.read_csv('subway_long.csv', index_col=False)

st.title('캐싱 적용해보기')

station = st.selectbox('역을 선택하세요', ['동대구역', '반월당역', '범어역'])

# 역을 바꿀때 마다 매번 2초씩 다시 로딩
df = load_subway_data()
st.write(f'{station} 데이터 로딩 완료')
st.dataframe(df.head())