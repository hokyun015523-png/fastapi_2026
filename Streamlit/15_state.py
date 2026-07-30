# =================================================================================
# ~/bigdata202/fastapi//Streamlit/15_state.py
#  Streamlit 라이브러리 기초 실습 / 실행 방법: streamlit run 파일이름
#  - sesstion stats
# d위젯을 조작할 때마다 파이썬 변수가 초기화 되는 문제를 해결한다.
#    st.sesstion_state로 재실행 사잉의 값을 유지할 수 있었다
# - 콜백 함수와 함께 사용할 수 있다.
# =================================================================================
import streamlit as st

st.title('카운터 (문제 상황)')

# t.session_state : 브라우저 탭(세션) 하나에 묶여서 재실행 되어도 값이 사라지지 않는 딕셔너리 형태의 특수 저장소
if 'count' not in st.session_state:
    st.session_state.count = 0

if st.button('+1'):
    st.session_state.count += 1

st.write(f'현재카운터 : {st.session_state.count}')