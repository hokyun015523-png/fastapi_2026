'''
langchain_pratice/00_check_setup.py
-------------------------------------------
설치 확인 + Gemini API key 연결 확인 테스트

이 파일의 목적
- .env에 넣어둔 GOOGLE_API_KEY가 제대로 읽히는지 확인
- GEMINI모델에 실제로 요청을 보내고, 응답을 받아오는지 확인
- 여기서 에러가 나면 이후 모든 실습이 진행 불가 / 통과 해야함
'''
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY') 

if not api_key: # api_key가 None이거나 없다면 (키 인식 실패) -> 강제로 멈춘다.
    raise SystemExit('GOOGLE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요')

# 키가 확인된 다음, 패키지 불러온다
from langchain_google_genai import ChatGoogleGenerativeAI

# Gemini 모델을 사용할 수 있게 감싸주는 객체를 생성 - 무료 티어가 있고, 이미지(비전) 입력도 지원하는 
# 가벼운 모델 설정 --> 2.5 flash
llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash')

# 실제로 모델에게 질문을 보내고, 응답이 올 때 까지 기다린다.
response = llm.invoke('한 문장으로 자기소개 해줘.')

print('연결 성공. 모델 응답:')
# print(response.content) # 실제 답변 텍스트는 content안에 있다.
print(response.content[0]['text'])