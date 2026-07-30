# =================================================================================
# ~/bigdata202/fastapi//Streamlit/13_form2.py
#  Streamlit 라이브러리 기초 실습 / 실행 방법: streamlit run 파일이름
#  - 폼 위젯 :  입력값 검증
# =================================================================================
import streamlit as st

st.title('회원가입(검증포함)')

# 'signup_form': 폼 이름은 폼을 구분하는 고유 이름(key), 폼이 여러개면 서로 다른 이름을 주어야 한다.
with st.form('signup_form_v2'):
    name = st.text_input('이름')
    email =st.text_input('이메일')
    age = st.number_input('나이', min_value=0, max_value=120, value=20) # 기본값 20
    agree = st.checkbox('이용약관에 동의합니다.')

    # 일반 버튼 위젯이 아니고 폼 안에서만 쓸수 있는 버튼 위젯을 사용해야한다.
    submmited = st.form_submit_button('가입하기')

# 버튼을 클릭 한다. -> 폼 제출 시점의 최종값을 그대로 가지고 있다. (with 블록 밖에서 해도 됨)
if submmited:
    if not name:
        st.error('이름을 입력해주세요.') 
    elif '@' not in email:
        st.error('올바른 이메일 형식이 아닙니다.')
    elif not agree:
        st.error('이용약관에 동의해야 가입할 수 있습니다.')
    else:
        st.success(f'{name}님, 가입이 완료되었습니다. (이메일: {email}, 나이: {age})')