from enum import Enum
from typing import Type, Dict, Any, Union, TYPE_CHECKING
from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from src.domain.question.entities.question import Question, MultipleChoiceQuestion, DescriptionQuestion, ShortAnswerQuestion

class QuestionType(str, Enum):
    """문제 유형을 정의하는 열거형"""
    RANDOM = "random"
    SHORT_ANSWER = "short_answer"
    DESCRIPTION = "description"
    MULTIPLE_CHOICE = "multiple_choice"

    @classmethod
    def get_question_class(cls, question_type: str) -> Type["Question"]:
        """문제 유형에 해당하는 Question 클래스를 반환합니다."""
        from src.domain.question.entities.question import Question, MultipleChoiceQuestion, DescriptionQuestion, ShortAnswerQuestion
        
        type_map = {
            cls.SHORT_ANSWER: ShortAnswerQuestion,
            cls.DESCRIPTION: DescriptionQuestion,
            cls.MULTIPLE_CHOICE: MultipleChoiceQuestion
        }
        return type_map.get(question_type, Question)

class QuestionTypeConfig(BaseModel):
    """문제 유형별 설정을 정의하는 모델"""
    type: QuestionType = Field(..., description="문제 유형")
    difficulty: str = Field(..., description="난이도")
    number_of_answers: int = Field(..., gt=0, description="생성할 답변 수")

    @classmethod
    def create_question(
        cls,
        question_type: str,
        question_text: str,
        **kwargs
    ) -> "Question":
        """문제 유형에 맞는 Question 객체를 생성합니다."""
        from src.domain.question.entities.question import MultipleChoiceQuestion, DescriptionQuestion, ShortAnswerQuestion
        
        if question_type == QuestionType.MULTIPLE_CHOICE:
            return MultipleChoiceQuestion(
                question=question_text,
                choices=kwargs.get("choices", []),
                correct_answer=kwargs.get("correct_answer", "")
            )
        elif question_type == QuestionType.SHORT_ANSWER:
            return ShortAnswerQuestion(question=question_text)
        else:  # DESCRIPTION
            return DescriptionQuestion(question=question_text) 