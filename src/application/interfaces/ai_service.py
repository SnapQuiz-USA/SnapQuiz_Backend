from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any
from fastapi import UploadFile
from src.domain.question.entities.question import (
    Question, MultipleChoiceQuestion, ShortAnswerQuestion, DescriptionQuestion,
    AnswerVerificationResult
)
from src.domain.question.value_objects.question_type import QuestionType

class AIService(ABC):
    """AI 서비스 인터페이스"""
    
    @abstractmethod
    async def generate_questions(
        self,
        prompt: str
    ) -> List[Union[MultipleChoiceQuestion, ShortAnswerQuestion, DescriptionQuestion]]:
        """이미지를 기반으로 문제를 생성합니다."""
        pass

    @abstractmethod
    async def verify_answer(
        self,
        question: str,
        answer: str,
        question_type: QuestionType
    ) -> AnswerVerificationResult:
        """답변을 검증합니다."""
        pass

    @abstractmethod
    async def answer_user_question(
        self,
        subject: str,
        question: str
    ) -> Dict[str, str]:
        """사용자 질문에 답변합니다."""
        pass 