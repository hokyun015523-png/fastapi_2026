# =============================================================
# ~/bigdata202/fastapi//Streamlit/05_interactive.py
#
#  Streamlit 라이브러리 기초 실습
#
#  - 입력 위젯 (체크박스, 라디오 버튼, 단일 선택 박스)
# ===========================================================
import streamlit as st

st.title('간단한 퀴즈')

# 1. 체크박스
agree = st.checkbox('Q1. 파이썬은 프로그래밍 언어이다.(맞으면 체크)')

if agree:
    st.write(' 정답입니다')

st.write('---')

# 2. 라디오버튼 -> 하나만 선택 가능
person = st.radio('Q2. 당신의 성별은?', ['남자', '여자'])

if person == '남자':
    st.write('당신은 남자입니다.')
else:
    st.write('당신은 여자입니다.')

st.write('---')
st. divider()

# 3. 단일 선택 박스
transport = st.selectbox( 'Q3. 가장 빠른 교통수단은?', 
                        ["기차", "자동차", "비행기", "배"])

if transport == '비행기':
    st.write('정답! 비행기가 가장 빠릅니다')
else:
    st.write('땡! 틀렸습니다! 비행기가 가장 빨라요')

st.divider()