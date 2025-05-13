from utils.guide_parser import get_guide_content
from utils.constants import QUESTION_TYPE_DESCRIPTIONS

def build_prompt(settings):
    """설정값을 바탕으로 프롬프트를 생성합니다."""
    domain = settings['domain']
    guide_content = get_guide_content(domain)
    question_type = settings['question_type']
    question_type_desc = QUESTION_TYPE_DESCRIPTIONS[question_type]
    
    # 가이드 파일 로드 오류 체크
    if guide_content.startswith("Error:"):
        return guide_content
    
    prompt = f"""
다음 조건에 맞는 금융보안 문제를 생성해주세요:

1. 문제 유형: {question_type}
   - 유형 설명: {question_type_desc}
2. 도메인: {domain}
3. 난이도: {settings['difficulty']}
4. 문제 수: {settings['num_questions']}개
5. 출력 형식: {settings['output_format']}

선택한 도메인({domain})의 출제기준은 다음과 같습니다. 아래 내용을 참고하여 문제를 생성해주세요:
{guide_content}

각 문제는 5지선다로 다음 형식을 정확히 따라주세요:

[문제 형식]
- 출제 기준: [주요항목] > [세부항목] > [세세항목] 형식으로 표시
- 문제 번호와 내용 (반드시 위에서 설명한 문제 유형의 특성을 정확히 반영해야 함)
- 보기 

[해답]
- 정답
- 해설 (문제 유형의 특성에 맞춰 상세히 설명)

문제와 해답은 "[해답]" 구분자로 구분하고, 각 문제는 "---" 구분자로 구분해주세요.
문제들은 서로 중복되지 않아야 하며, 명확하고 정확한 내용을 담고 있어야 합니다.
각 문제마다 위의 출제 기준 중에서 하나를 선택하여 반드시 명시해주세요.
특히, 선택한 문제 유형의 특성을 정확히 반영하여 문제를 출제해주세요.
"""
    return prompt