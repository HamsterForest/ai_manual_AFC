import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# 로컬 테스트를 위해 .env 파일 로드
load_dotenv()

# Streamlit Secrets 또는 .env에서 키 불러오기
try:
    encryption_key_base64 = st.secrets.get("ENCRYPTION_KEY") or os.getenv("ENCRYPTION_KEY")
    gemini_api_key = st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    correct_password = st.secrets.get("PASSWORD") or os.getenv("PASSWORD")

    if not all([encryption_key_base64, gemini_api_key, correct_password]):
        st.error("필요한 모든 환경 변수가 설정되지 않았습니다. Secrets 또는 .env 파일을 확인해 주세요.")
        st.stop()
    
    encryption_key = base64.b64decode(encryption_key_base64)

except Exception as e:
    st.error(f"키 설정 또는 비밀번호 불러오기 중 오류 발생: {e}")
    st.stop()

# 파일 복호화 함수
@st.cache_data
def decrypt_file_content(file_path, key):
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        nonce = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt(ciphertext)
        
        return unpad(decrypted_data, AES.block_size).decode('utf-8')

    except Exception as e:
        st.error(f"오류: 데이터 복호화에 실패했습니다: {e}")
        return None

# 비밀번호 입력 UI
st.title("🔐 AFC 장애 정보 어시스턴트")
password = st.text_input("비밀번호를 입력하세요:", type="password")

if password == correct_password:
    st.success("로그인 성공!")
    
    # Gemini API 구성 및 모델 초기화
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
    def get_answer_from_gemini(query, context):
        try:
            # 프롬프트를 명확하게 재구성합니다.
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

    # 파일 복호화
    with st.spinner("보안 데이터 불러오는 중..."):
        afc_data = decrypt_file_content("afc_data.txt.encrypted", encryption_key)
    
    if afc_data is None:
        st.stop()

    # 사용자 입력 받기
    user_query = st.text_input("질문: ")

    if user_query:
        with st.spinner("답변을 생성하는 중입니다..."):
            answer = get_answer_from_gemini(user_query, afc_data)
            st.subheader("🤖 답변")
            st.write(answer)
            
else:
    if password:
        st.error("비밀번호가 틀렸습니다.")