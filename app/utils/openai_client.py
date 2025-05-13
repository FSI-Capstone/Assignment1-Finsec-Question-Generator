import os
from openai import OpenAI
from dotenv import load_dotenv

def get_openai_client():
    """OpenAI 클라이언트를 초기화하고 반환합니다."""
    load_dotenv()
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요.")
    
    return OpenAI(api_key=api_key) 