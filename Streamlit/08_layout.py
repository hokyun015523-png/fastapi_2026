# =============================================================
# ~/bigdata202/fastapi//Streamlit/08_layout.py
#
#  Streamlit 라이브러리 기초 실습 / 실행 방법: streamlit run 파일이름
#
#  - 레이아웃
# ===========================================================

# 1. 라이브러리 불러오기
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from PIL import Image


# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 2. 메인페이지
st.title('This is main page')

# 3. sidebar
with st.sidebar:
    st.title('This is sidebar')
    side_option = st.multiselect(
        label='your selection is',
        options=['Car', 'Airplane', 'Train', 'Ship', 'Bicycle'],
        placeholder='select transportation'
    )

# 4. 이미지 세로 나열 --> 이미지가 하나씩 보인다.
img1 = Image.open('roma.PNG')
img2 = Image.open('roma3.PNG')
img3 = Image.open('asroma.PNG')

st.header('아우구스투스')
st.image(img1, width=400, caption='초대 로마의 황제 아우구스투스 동상')

st.header('콜로세움')
st.image(img2, width=400, caption='여름의 콜로세움')

# 5. 컬럼 레이아웃(세로 단이 2개)
col1, col2 = st.columns(2) # 비율을 다르게 하고싶으면 [] 후 1, 1 이런식으로 작성하면 됨 2라고 적으면 동일하게 정해짐
with col1:
    st.header('아우구스투스')
    st.image(img1, width=300, caption='아우구스투스 동상')

with col2:
    st.header('AS로마')
    st.image(img3, width=300, caption='AS로마의 로고')

st.divider()

# . 탭 레이아웃
tab1, tab2 = st.tabs(['실습1', '실습2'])

# 판다스로 csv불러와서 데이터프레임 생성
df = pd.read_csv('2026-07-16T07-16_export.csv')

with tab1: # 실습1 관련된 페이지
    st.table(df.head())

with tab2: # 실습2 관련된 페이지
    fig, ax = plt.subplots()
    sns.countplot(data=df, ax=ax)
    st.pyplot(fig)
