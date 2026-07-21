# ========================================================================
# ~/bigdata2026/fastapi/Streamlit/practice1.py
#   
#   Streamlit 연습문제 1 - 나만의 자기소개 카드
# ========================================================================

import streamlit as st

st.title('나만의 자기소개 카드')

# 1. 이름 입력 (text_input 위젯)
name = st.text_input(
    '이름을 입력하세요',
    placeholder='예) 김코딩'
)

# 2. 경력 연차 입력 (slider 위젯)
years = st.slider(
    '경력 연차를 선택하세요',
    min_value=0,
    max_value=20,
    value=0
)

# 3. 관심 기술 스택 선택 (multiselect)
skills = st.multiselect(
    '관심있는 기술을 모두 선택하세요',
    ['Python', 'SQL', 'Streamlit', 'FastAPI', '머신러닝']
)

st.divider()

# 4. 이름을 입력했을때만 카드 출력
if name:
    # 세로를 1:3 비율로 나눈다 (columns 위젯)
    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown(f'''
        <div style="width:60px;height:60px;border-radius:50%;
                    background-color:#e6f1fb;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    font-weight:bold">{name[0]}</div>                    
                    ''',
                    unsafe_allow_html=True)

    with col2:
        st.write(f'**이름:** {name}')
        st.write(f'**경력 연차:** {years}년')

        if skills: # ', '.join(skills) --> python, SQL, html, 
            st.write('**관심 기술:**', ', '.join(skills))
        else:
            st.write('**관심 기술:** 선택된 항목 없음')

else:
    st.info('이름을 입력하면 카드가 생성됩니다.')