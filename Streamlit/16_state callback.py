# =================================================================================
# ~/bigdata202/fastapi//Streamlit/16_state callback.py.py
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

def increment():
    """콜백 함수 : 위젯 클릭시 화면이 다시 그려지기 전에 직전에 자동으로 호출되는 함수"""

    st.session_state.count += 1

def decrement():
    st.session_state.count  -= 1

def reset():
    #콜백 안에서는 조건문 없이 바로 대입하면 된다.(버튼이 눌러졌을때만 실행되므로)
    st.session_state.count = 0

col1, col2, col3 = st.columns(3) # 동일한 너비로 3칸
with col1:
    st.button('+ 증가', on_click=increment) # 함수 이름만 전달 (클릭 했을때만 실행되겠금 설정)

with col2:
    st.button('- 감소', on_click=decrement)

with col3:
    st.button('리셋', on_click=reset)

# st.metric: 카드형태로 보여준느 위젯

st.metric('현재 값', st.session_state.count)