# =============================================================
# ~/bigdata202/fastapi//Streamlit/practice3_풀이.py
#
#  Streamlit 라이브러리 기초 연습문제 풀이 / 실행 할 때 터미널 streamlit run [파일명] 
# ===========================================================
import streamlit as st

st.title('간단 설문 & 만족도 조사')

# 1. 이름 입력(text_input)
name = st.text_input('이름을 입력하세요')

# 2. 관심분야 선택(multiselect)
interests = st.multiselect('관심있는 분야를 선택하세요',
                            ['AI', '빅데이터', '웹개발', '클라우드', '보안'])

# 3. 만족도 입력(slider)
satisfaction = st.slider('이번 수업 만족도를 선택하세요. (0~10)',
                            min_value=0, max_value=10, value=5)

st.divider()

# 4. 제출 버튼 (button) - 버튼을 누르면 결과가 보이도록 처리
submitted = st.button('제출하기')

if submitted:
    # 이름과 관심 분야가 모두 채워졌을때만 완료 처리
    if name and interests:
        st.success('제출이 완료되었습니다. 참여해주셔서 감사합니다.')
        
        st.write(f'**응답자:** {name}')
        st.write(f'**관심 분야:** {interests}')
        st.write(f'**만족도:** {satisfaction} / 10')

    else:
        st.error('이름과 관심분야를 모두 입력/선택해주세요')