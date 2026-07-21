# =============================================================
# ~/bigdata202/fastapi//Streamlit/practice1.py
#
#  Streamlit 라이브러리 기초 연습문제 / 실행 할 때 터미널 streamlit run [파일명] 
#
# ===========================================================
import streamlit as st
import pandas as pd

# 1. 나만의 자기소개 카드
st.title('나만의 자기소개 카드')
st.divider()

string1 = st.text_input(
    '이름을 입력하세요',
    placeholder='예)홍길동',
    max_chars=25
)

# 경력 숫자 슬라이더
score = st.slider('경력연차를 선택하세요', 0, 70, 1)

# 관심있는 기술 선택
skill = st.multiselect(
    "관심있는 기술을 모두 선택하세요:",
    ['Python', 'SQL', 'Streamlit', 'FastAPI', '머신러닝']
)
correct = {'Python', 'SQL', 'Streamlit', 'FastAPI', '머신러닝'}

st.divider()

if string1:
    st.write(f'**이름**:{string1}')
    st.write(f'**경력연차** : {score}년')

if set(skill) == correct:
    st.write('**관심 기술**: Python, SQL, Streamlit, FastAPI, 머신러닝')