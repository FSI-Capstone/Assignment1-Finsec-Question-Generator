import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils.openai_client import get_openai_client
from utils.prompt_builder import build_prompt

def generate_questions(settings):
    """설정값을 바탕으로 문제를 생성합니다."""
    client = get_openai_client()
    
    # 프롬프트 생성
    prompt = build_prompt(settings)
    
    # 가이드 파일 로드 오류 체크
    if prompt.startswith("Error:"):
        return [(prompt, "")]
    
    # OpenAI API를 통해 문제 생성
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 전문적인 금융보안 문제 출제자입니다. 문제와 해답을 명확히 구분하여 출제해주세요."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    # 응답을 파싱하여 문제와 해답 리스트 반환
    return parse_response(response.choices[0].message.content)

def parse_response(content):
    """API 응답을 파싱하여 문제와 해답 리스트로 변환합니다."""
    questions_and_answers = []
    
    # 문제 단위로 분리
    raw_questions = [q.strip() for q in content.split("\n\n---\n\n") if q.strip()]
    
    for raw_question in raw_questions:
        # 문제와 해답 분리
        parts = raw_question.split("\n\n[해답]\n")
        
        if len(parts) == 2:
            question = parts[0].strip()
            answer = parts[1].strip()
            questions_and_answers.append((question, answer))
    
    return questions_and_answers 