from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from src.domain.question.value_objects.question_type import QuestionType

class Question(BaseModel):
    """문제의 기본 클래스"""
    model_config = ConfigDict(extra='forbid')
    
    question: str
    type: QuestionType

class MultipleChoiceQuestion(Question):
    """객관식 문제"""
    choices: List[str] = Field(..., min_items=2, description="선택지 목록")
    correct_answer: str = Field(..., description="정답")
    type: QuestionType = Field(default=QuestionType.MULTIPLE_CHOICE)

class ShortAnswerQuestion(Question):
    """단답형 문제"""
    type: QuestionType = Field(default=QuestionType.SHORT_ANSWER)

class DescriptionQuestion(Question):
    """서술형 문제"""
    type: QuestionType = Field(default=QuestionType.DESCRIPTION)

class AnswerVerificationResult(BaseModel):
    """답변 검증 결과"""
    correct: bool = Field(..., description="답변이 정답인지 여부")
    feedback: str = Field(None, description="모범 답안")

class AnswerAboutUserQuestion(BaseModel):
    """사용자 질문"""
    subject: str = Field(..., description="과목")
    question: str = Field(..., description="사용자가 질문한 내용") 