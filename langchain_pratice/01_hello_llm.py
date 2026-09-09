'''
langchain_pratice/01_hello_llm.py
--------------------------------------------
가장 단순한 호출 - 프롬프트 템플릿 없이 문자열 하나로 바로 질문

이 파일의 목적
- Lanchain을 통해 모델을 직접 부르면 어떤 모습인지 확인
- .invoke() --> 질문을 보내고 응답을 받는다.
'''
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY') 

if not api_key: # api_key가 None이거나 없다면 (키 인식 실패) -> 강제로 멈춘다.
    raise SystemExit('GOOGLE_API_KEY가 설정되지 않았습니다. .env 파일을 확인하세요')
    
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model='gemini-3.6-flash')

response = llm.invoke('외계인은 진짜 존재할까? 예, 아니요로 대답해줘')
result = response.content[0]['text']
print(result)