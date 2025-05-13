from typing import Dict, List, Optional
from .openai_client import get_openai_client
from .guide_loader import GuideLoader, SecurityDomain
import json

class QuestionGenerator:
    def __init__(self):
        self.client = get_openai_client()
        
    def generate_question(self, domain: SecurityDomain, difficulty: str = "중") -> Dict:
        """선택된 도메인과 난이도에 따라 문제를 생성합니다."""
        # 가이드 로드
        guide_items = GuideLoader.load_guide(domain)
        
        # 프롬프트 구성
        system_prompt = self._create_system_prompt(domain)
        user_prompt = self._create_user_prompt(guide_items, difficulty)
        
        # API 호출
        response = self.client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        
        # 응답 파싱 및 반환
        try:
            question_data = response.choices[0].message.content
            return self._parse_question_response(question_data)
        except Exception as e:
            raise ValueError(f"문제 생성 중 오류 발생: {str(e)}")
    
    def _create_system_prompt(self, domain: SecurityDomain) -> str:
        """도메인에 맞는 시스템 프롬프트를 생성합니다."""
        domain_descriptions = {
            SecurityDomain.GENERAL: "금융보안 일반지식",
            SecurityDomain.NETWORK: "네트워크 보안",
            SecurityDomain.SYSTEM: "시스템 보안",
            SecurityDomain.APPLICATION: "어플리케이션 보안"
        }
        
        return f"""당신은 {domain_descriptions[domain]} 분야의 전문가입니다.
주어진 출제기준과 난이도에 맞춰 객관식 문제를 생성해주세요.
답변은 다음 JSON 형식으로 작성해주세요:
{{
    "question": "문제 내용",
    "choices": ["보기1", "보기2", "보기3", "보기4"],
    "answer": 정답번호(1-4),
    "explanation": "해설"
}}"""

    def _create_user_prompt(self, guide_items: List[Dict], difficulty: str) -> str:
        """문제 생성을 위한 사용자 프롬프트를 생성합니다."""
        return f"""다음 출제기준에 따라 {difficulty}난이도의 객관식 문제를 1개 생성해주세요:

출제기준:
{self._format_guide_items(guide_items)}

요구사항:
1. 문제는 실무적이고 현실적인 상황을 반영해야 합니다.
2. 보기는 4개여야 하며, 모두 그럴듯해야 합니다.
3. 정답은 명확해야 합니다.
4. 해설은 왜 그 답이 정답인지 명확히 설명해야 합니다."""

    def _format_guide_items(self, guide_items: List[Dict]) -> str:
        """가이드 항목들을 문자열로 포맷팅합니다."""
        formatted = []
        for item in guide_items:
            formatted.append(f"- {item['main_category']} > {item['sub_category']} > {item['detail_category']}")
        return "\n".join(formatted)

    def _parse_question_response(self, response: str) -> Dict:
        """API 응답을 파싱하여 문제 데이터를 반환합니다."""
        try:
            # 응답에서 JSON 부분만 추출
            json_str = response.strip()
            if "```json" in json_str:
                json_str = json_str.split("```json")[1].split("```")[0]
            elif "```" in json_str:
                json_str = json_str.split("```")[1].split("```")[0]
                
            question_data = json.loads(json_str)
            
            # 필수 필드 검증
            required_fields = ["question", "choices", "answer", "explanation"]
            for field in required_fields:
                if field not in question_data:
                    raise ValueError(f"필수 필드 누락: {field}")
                    
            return question_data
            
        except Exception as e:
            raise ValueError(f"응답 파싱 중 오류 발생: {str(e)}") 