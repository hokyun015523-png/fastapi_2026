'''
home_library_v1 / streamlit_app.py
-----------------------------------
1단계 전용 - ISBN 조회
'''
import requests
import streamlit as st

API = 'http://127.0.0.1:8000'

st.title('우리집 책장 (개발 중)')

st.header('1단계: ISBN으로 바로 조회해보기')
st.caption('사진 없이 ISBN 숫자만 넣어서, 서지정보 API가 잘 연결됐는지 먼저 확인합니다.')

isbn_input = st.text_input('ISBN 입력 (예: 9791139721973)')

if st.button('조회하기'):
    if not isbn_input:
        st.warning('ISBN을 입력해주세요!')
    else:
        r = requests.get(f'{API}/books/lookup', params={'isbn': isbn_input})

        if r.ok:
            data = r.json()
            st.success(f'**{data["title"]}**')
            st.write(f'저자: {data["author"] or "정보 없음"}')
            st.write(f'출판사: {data["publisher"] or "정보 없음"}')
        else:
            st.error(f'조회 실패 ({r.status_code}): 등록된 정보가 없거나 잘못된 ISBN입니다.')

st.divider()

st.subheader('등록된 책')
for book in requests.get(f'{API}/books').json():
    st.write(f'{book["title"]} ({book["recognition_status"]})')