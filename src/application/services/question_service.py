from typing import List, Union
from src.application.interfaces.ai_service import AIService
from src.domain.question.entities.question import (
    Question, MultipleChoiceQuestion, ShortAnswerQuestion, DescriptionQuestion,
    AnswerVerificationResult, AnswerAboutUserQuestion
)
from src.domain.question.value_objects.question_type import QuestionType
from src.interfaces.api.schemas.question_schemas import QuestionCreateDTO
from src.utils.faiss import retrieve_top_k_documents

class QuestionService:
    """문제 생성 서비스"""

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    async def generate_question(
        self,
        textbook_text: str,
        question_create_dto: QuestionCreateDTO
    ) -> List[Union[MultipleChoiceQuestion, ShortAnswerQuestion, DescriptionQuestion]]:
        """교과서 이미지를 바탕으로 문제 생성"""
        try:
            rag_data = retrieve_top_k_documents(textbook_text)
            prompt = self._create_prompt_questions(question_create_dto, rag_data)
            return await self.ai_service.generate_questions(prompt)
        except Exception as e:
            raise ValueError(f"문제 생성 실패: {e}")

    async def verify_answer(
        self,
        question: str,
        answer: str,
        question_type: QuestionType
    ) -> AnswerVerificationResult:
        """답안 검증"""
        try:
            result = await self.ai_service.verify_answer(question, answer, question_type)
            return result
        except Exception as e:
            raise ValueError(f"답변 검증 실패: {str(e)}")

    async def answer_user_question(
        self,
        data: AnswerAboutUserQuestion
    ) -> dict:
        """사용자 질문에 대한 답변 생성"""
        try:
            return await self.ai_service.answer_user_question(
                data.subject,
                data.question
            )
        except Exception as e:
            raise ValueError(f"답변 생성 실패: {str(e)}")

    def _create_prompt_questions(
        self,
        dto: QuestionCreateDTO,
        rag_data = List[str]
    ) -> str:
        """문제 생성용 프롬프트"""
        return f"""
다음은 교과서의 내용입니다. 이 내용을 바탕으로 아래 조건에 맞는 문제들을 JSON 배열 형태로 생성해 주세요.

- 과목: {dto.subject}
- 난이도: {dto.difficulty}
- 생성할 문제 수: {dto.number_of_questions}
- 문제 유형: {dto.question_type.value}
- 참고할 데이터 : {rag_data}

출력 형식은 다음과 같습니다. **JSON 배열만 출력하고, 다른 텍스트는 포함하지 마세요.**
글자 꾸미는 마크업 요소 없애.
- 과목이 수학인 경우, 수식은 LaTeX 형식으로 작성하고 `$`로 감싸 주세요.
- `"type"`이 `"multiple_choice"`일 경우에만 `"choices"`와 `"correct_answer"` 항목을 포함해 주세요.
- `"short_answer"` 또는 `"description"` 유형일 경우 `"choices"`와 `"correct_answer"`는 작성하지 마세요.

예시 형식:
[
  {{
    "type": "multiple_choice" | "short_answer" | "description",
    "question": "문제 내용",
    "choices": ["선택지1", "선택지2", "선택지3", "선택지4"],  // multiple_choice일 때만 포함
    "correct_answer": "정답"  // multiple_choice일 때만 포함
  }},
  ...
]
""" 