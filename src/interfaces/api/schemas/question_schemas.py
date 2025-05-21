from pydantic import BaseModel, Field
from src.domain.question.value_objects.question_type import QuestionType

class QuestionCreateDTO(BaseModel):
    """문제 생성을 위한 데이터 전송 객체"""
    subject: str = Field(..., min_length=1, description="과목명")
    question_type: QuestionType = Field(..., description="문제 유형")
    difficulty: str = Field(..., description="난이도")
    number_of_questions: int = Field(..., gt=0, description="생성할 답변 수")

class AnswerVerificationDTO(BaseModel):
    """답변 검증에 필요한 데이터"""
    question: str
    answer: str
    question_type: QuestionType 