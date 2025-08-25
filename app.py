import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# .env 파일에서 환경 변수 불러오기 (로컬 테스트용)
load_dotenv()

# Streamlit Secrets 또는 .env에서 키 불러오기
try:
    # 암호화 키
    encryption_key_base64 = st.secrets["ENCRYPTION_KEY"] if "ENCRYPTION_KEY" in st.secrets else os.getenv("ENCRYPTION_KEY")
    if not encryption_key_base64:
        st.error("암호화 키(ENCRYPTION_KEY)가 설정되지 않았습니다. Secrets 또는 .env 파일을 확인해 주세요.")
        st.stop()
    encryption_key = base64.b64decode(encryption_key_base64)
    
    # Gemini API 키
    gemini_api_key = st.secrets["GOOGLE_API_KEY"] if "GOOGLE_API_KEY" in st.secrets else os.getenv("GOOGLE_API_KEY")
    if not gemini_api_key:
        st.error("Gemini API 키(GOOGLE_API_KEY)가 설정되지 않았습니다. Secrets 또는 .env 파일을 확인해 주세요.")
        st.stop()

    # 비밀번호
    correct_password = st.secrets["secrets"]["password"]

except Exception as e:
    st.error(f"키 설정 또는 비밀번호 불러오기 중 오류 발생: {e}")
    st.stop()

# 파일 복호화 함수
def decrypt_file_content(file_path, key):
    """암호화된 파일을 읽어 복호화하고 내용을 반환하는 함수"""
    try:
        with open(file_path, "rb") as f:
            data = f.read()

        nonce = data[:16]
        ciphertext = data[16:]
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted_data = cipher.decrypt(ciphertext)
        
        return unpad(decrypted_data, AES.block_size).decode('utf-8')

    except FileNotFoundError:
        st.error(f"오류: 암호화된 파일을 찾을 수 없습니다: {file_path}")
        return None
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
        """사용자의 질문과 복호화된 데이터를 기반으로 Gemini AI가 답변 생성"""
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