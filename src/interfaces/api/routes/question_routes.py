import json
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Form
from typing import List, Union
from src.application.services.question_service import QuestionService
from src.domain.question.entities.question import (
    MultipleChoiceQuestion, DescriptionQuestion, ShortAnswerQuestion,
    AnswerVerificationResult, AnswerAboutUserQuestion
)
from src.infrastructure.ai.gemini_client import GeminiClient
from src.interfaces.api.schemas.question_schemas import QuestionCreateDTO, AnswerVerificationDTO

router = APIRouter(prefix="/questions", tags=["questions"])

async def get_question_service() -> QuestionService:
    """의존성 주입을 위한 QuestionService 생성 함수"""
    ai_service = GeminiClient()
    return QuestionService(ai_service)

@router.post("/generate", response_model=List[Union[ShortAnswerQuestion, DescriptionQuestion, MultipleChoiceQuestion]])
async def generate_questions(
    textbook_image: UploadFile,
    data: str = Form(...),
    question_service: QuestionService = Depends(get_question_service)
) -> List[Union[ShortAnswerQuestion, DescriptionQuestion, MultipleChoiceQuestion]]:
    """교과서 이미지를 기반으로 문제를 생성합니다."""
    try:
        data_dict = json.loads(data)
        question_create_dto = QuestionCreateDTO(
            subject=data_dict["subject"],
            difficulty=data_dict["difficulty"],
            number_of_questions=data_dict["number_of_questions"],
            question_type=data_dict["question_type"],
        )
    
        return await question_service.generate_question(textbook_image, question_create_dto)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing required field: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify", response_model=AnswerVerificationResult)
async def verify_answer(
    data: AnswerVerificationDTO,
    question_service: QuestionService = Depends(get_question_service)
) -> AnswerVerificationResult:
    """단답형/서술형 문제의 답변을 검증합니다."""
    try:
        return await question_service.verify_answer(
            data.question,
            data.answer,
            data.question_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/answers/generate", response_model=dict)
async def ask_question(
    data: AnswerAboutUserQuestion,
    question_service: QuestionService = Depends(get_question_service)
) -> dict:
    """사용자의 질문에 대한 답변을 생성합니다."""
    try:
        return await question_service.answer_user_question(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 