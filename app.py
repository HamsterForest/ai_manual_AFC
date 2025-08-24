import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env 파일에서 환경 변수 불러오기
load_dotenv()

# Google Gemini API 키 설정
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Gemini 1.5 Pro 모델 초기화
# gemini-pro 대신 현재 사용 가능한 최신 모델로 변경
model = genai.GenerativeModel('gemini-1.5-pro-latest')

def get_answer_from_gemini(query, context):
    """
    사용자의 질문과 텍스트 데이터를 기반으로 Gemini AI가 답변을 생성
    """
    try:
        prompt = f"""
        당신은 AFC(Automatic Fare Collection) 설비 장애에 대한 정보를 제공하는 AI 어시스턴트입니다.
        아래 제공된 정보만을 바탕으로 사용자의 질문에 답변하세요.
        만약 제공된 정보에 없는 내용이라면, "해당 정보는 저의 지식 베이스에 포함되어 있지 않습니다." 라고 답변하세요.

        ---
        제공된 정보:
        {context}
        ---

        사용자 질문:
        {query}
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"죄송합니다. 오류가 발생했습니다: {e}"

# 스트림릿 웹 앱 인터페이스 구성
st.set_page_config(
    page_title="AFC 장애 정보 어시스턴트",
    page_icon="🚉"
)

st.title("🚉 AFC 장애 정보 어시스턴트")
st.markdown("""
이 앱은 철도 역무자동화 설비(AFC) 장애에 대한 기본적인 정보와 조치법을 알려주는 AI 어시스턴트입니다.
궁금한 점을 질문해 주세요.
""")

# 텍스트 데이터 파일 읽기
try:
    with open("afc_data.txt", "r", encoding="utf-8") as f:
        afc_data = f.read()
except FileNotFoundError:
    st.error("`afc_data.txt` 파일을 찾을 수 없습니다. 파일을 생성해 주세요.")
    st.stop()

# 사용자 입력 받기
user_query = st.text_input("질문: ")

if user_query:
    with st.spinner("답변을 생성하는 중입니다..."):
        # Gemini AI 호출
        answer = get_answer_from_gemini(user_query, afc_data)
        st.subheader("🤖 답변")
        st.write(answer)