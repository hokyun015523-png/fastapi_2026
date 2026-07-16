# =============================================================
# ~/bigdata202/fastapi/Streamlit/03_image.py
#
#  Streamlit 라이브러리 기초 실습
#
#  - image 삽입
# ===========================================================
import streamlit as st
from PIL import Image

image = Image.open('roma.png')
image2 = Image.open('asroma.png')

# 1. 기본 이미지 출력 (소문자 변수명 매칭)
st.image(image, caption='아우구스투스')
st.image(image2, caption='AS로마')

# 2. 너비 조절 출력 (width 옵션)
st.image(image, caption='너비를 100으로 수정', width=100)
st.image(image2, caption='너비를 200으로 수정', width=200)

# 3. 픽셀 사이즈 직접 리사이즈 후 출력
small_image = image.resize((200, 200))  # 작은 사이즈 조정

st.image(small_image, caption='작아진 이미지')