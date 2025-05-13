from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..utils.question_generator import QuestionGenerator
from ..utils.guide_loader import SecurityDomain

router = APIRouter()
question_generator = QuestionGenerator()

class QuestionRequest(BaseModel):
    domain: str
    difficulty: str = "중"

class QuestionResponse(BaseModel):
    question: str
    choices: List[str]
    answer: int
    explanation: str

@router.get("/domains")
async def get_domains():
    """사용 가능한 도메인 목록을 반환합니다."""
    return {"domains": [domain.value for domain in SecurityDomain]}

@router.post("/generate", response_model=QuestionResponse)
async def generate_question(request: QuestionRequest):
    """선택된 도메인과 난이도에 따라 문제를 생성합니다."""
    try:
        # 도메인 유효성 검사
        try:
            domain = SecurityDomain(request.domain)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"유효하지 않은 도메인입니다. 가능한 도메인: {[d.value for d in SecurityDomain]}"
            )
            
        # 난이도 유효성 검사
        if request.difficulty not in ["상", "중", "하"]:
            raise HTTPException(
                status_code=400,
                detail="난이도는 '상', '중', '하' 중 하나여야 합니다."
            )
            
        # 문제 생성
        question_data = question_generator.generate_question(
            domain=domain,
            difficulty=request.difficulty
        )
        
        return QuestionResponse(**question_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 