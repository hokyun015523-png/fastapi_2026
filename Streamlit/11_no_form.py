# =============================================================
# ~/bigdata202/fastapi//Streamlit/11_no_form.py
#  Streamlit 라이브러리 기초 실습 / 실행 방법: streamlit run 파일이름
#  - 폼 제출 시 입력값을 검증하고 처리/ 왜 폼이 필요한가 문제상황 살펴보기(폼이 없는 경우)
#    이름을 한 글자식 입력할때 마다 화면 전체가 계속 재실행됨.
#    위젯이 3~4개 밖에 없다면 크게 문제되지 않지만, 
#    위젯이 많아지거나 뒤쪽에 무거운연산(DB저장, API호출)이 있으면 
#    매 글자 입력할 때마다 그 연산이 반복 실행되어 비효율적이다.
#    이때 해결하는 위젯이 st.form이다.
# ===========================================================
import streamlit as st

st.title('회원가입 (문제상황)')

name = st.text_input('이름')
email = st.text_input('이메일')
age = st.number_input ('나이', min_value=0, max_value=120)

st.divider()
st.write(f'입력한 이름: {name}')