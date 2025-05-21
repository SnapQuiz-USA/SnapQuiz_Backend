import os
import json
import re
from typing import Dict, List, Union, Any
import google.generativeai as genai
from src.application.interfaces.ai_service import AIService
from src.domain.question.entities.question import (
    Question, MultipleChoiceQuestion, ShortAnswerQuestion, DescriptionQuestion,
    AnswerVerificationResult
)
from src.domain.question.value_objects.question_type import QuestionType

class GeminiClient(AIService):
    """Gemini AI 클라이언트 구현"""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyBB5QlpSxbmtKd78isQlMkoOOnrDoZH518")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-1.5-flash")


    def extract_json_from_text(self, text: str):
        """JSON 문자열을 추출하고 파싱합니다."""
        # ```json 또는 ``` 제거
        text = re.sub(r"```(?:json)?", "", text).replace("```", "").strip()

        # JSON 객체 추출
        json_match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if not json_match:
            raise ValueError("JSON 형태를 찾을 수 없습니다.")

        json_str = json_match.group(1)

        try:
            # json_str = re.sub(r'\\', r"\\\\",  json_str)
            result = json.loads(json_str)
        except json.JSONDecodeError as e:
            print("JSONDecodeError:", e)
            print("원시 문자열:", repr(json_str))
            raise ValueError("JSON 파싱 실패")

        # 후처리 (줄바꿈 복원 등)
        for key in ("feedback", "answer"):
            if key in result:
                result[key] = result[key].replace("\\n", "\n")

        print(result)
        return result
    async def generate_questions(
        self,
        image_content: bytes,
        prompt: str
    ) -> List[Union[MultipleChoiceQuestion, ShortAnswerQuestion, DescriptionQuestion]]:
        """이미지를 기반으로 문제를 생성합니다."""
        try:
            response = await self.model.generate_content_async(
                contents=[{
                    "parts": [
                        {"mime_type": "image/jpeg", "data": image_content},
                        {"text": prompt}
                    ]
                }]
            )

            response_text = response.text
            questions_data = self.extract_json_from_text(response_text)

            questions = []
            for q in questions_data:
                q_type = q["type"]
                q_text = q["question"]

                if q_type == QuestionType.MULTIPLE_CHOICE:
                    question = MultipleChoiceQuestion(
                        question=q_text,
                        choices=q.get("choices", []),
                        correct_answer=q.get("correct_answer")
                    )
                elif q_type == QuestionType.SHORT_ANSWER:
                    question = ShortAnswerQuestion(question=q_text)
                elif q_type == QuestionType.DESCRIPTION:
                    question = DescriptionQuestion(question=q_text)
                else:
                    continue

                questions.append(question)

            return questions

        except Exception as e:
            raise ValueError(f"문제 생성 실패: {e}")

    async def verify_answer(
        self,
        question: str,
        answer: str,
        question_type: QuestionType
    ) -> AnswerVerificationResult:
        """답변을 검증합니다."""
        try:
            if question_type == QuestionType.MULTIPLE_CHOICE:
                raise ValueError("객관식 문제는 verify_answer 메서드를 사용할 수 없습니다.")

            prompt = self._create_prompt_answers(question, answer, question_type)
            response = await self.model.generate_content_async(prompt)
            response_text = response.text

            try:
                result = self.extract_json_from_text(response_text)

                return AnswerVerificationResult(
                    correct=bool(result.get("correct", False)),
                    feedback=result.get("feedback")
                )
            except json.JSONDecodeError:
                return AnswerVerificationResult(
                    correct=False,
                    feedback=response_text
                )
        except Exception as e:
            raise ValueError(f"답변 검증 실패: {str(e)}")

    async def answer_user_question(
        self,
        subject: str,
        question: str
    ) -> Dict[str, str]:
        """사용자 질문에 답변합니다."""
        try:
            prompt = self._create_prompt_user_question(subject, question)
            response = await self.model.generate_content_async(prompt)
            response_text = response.text

            try:
                result = self.extract_json_from_text(response_text)
                return {
                    "answer": result.get("answer", "")
                }
            except json.JSONDecodeError:
                return {
                    "answer": response_text
                }
        except Exception as e:
            raise ValueError(f"답변 생성 실패: {str(e)}")

    def _create_prompt_answers(self, question: str, answer: str, question_type: QuestionType) -> str:
        """답안 검증용 프롬프트를 생성합니다."""
        return f"""
문제 유형: {question_type.value}
문제: {question}
사용자 답변: {answer}
만약 수학이라면 feedback은 LaTeX형식으로 작성, 수식은 $로 감싸주세요.
- JSON 형식에 포함되는 문자열에서 백슬래시(\\)가 포함될 경우 반드시 (\)으로 이스케이프 해주세요.
- 특히 LaTeX 명령어(예: frac, dots 등)는 JSON 파싱 오류를 방지하기 위해 반드시 이스케이프된 상태로 작성해야 합니다.
정답 여부를 판단하고 다음 형식으로 응답하세요:
{{
  "correct": true/false,
  "feedback": ""
}}
"""

    def _create_prompt_user_question(self, subject: str, question: str) -> str:
        """사용자 질문용 프롬프트를 생성합니다."""
        return f"""
과목: {subject}
사용자 질문: {question}

위 질문에 대해 전문가처럼 자세히 답변해주세요.
만약 subject가 수학이라면 LaTeX형식으로 작성, 수식은 $로 감싸주세요.
- JSON 형식에 포함되는 문자열에서 백슬래시(\\)가 포함될 경우 반드시 두 번(\\\\)으로 이스케이프 해주세요.
- 특히 LaTeX 명령어(예: \frac, \\dots 등)는 JSON 파싱 오류를 방지하기 위해 반드시 이스케이프된 상태로 작성해야 합니다.
답변은 다음 형식으로 제공해주세요:
{{
    "answer": "답변 내용. 줄바꿈할 때는 반드시 그 뒤에 띄어쓰기를 해주세요.",
}}
""" 