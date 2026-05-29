from pydantic import BaseModel
from typing import Optional, List


class RecordingResponse(BaseModel):
    session_id: str
    transcript: str


class Question(BaseModel):
    id: str
    text: str
    category: str  # e.g. "domain_model", "business_rules", "edge_cases"


class QuestionRequest(BaseModel):
    session_id: str


class QuestionsResponse(BaseModel):
    questions: List[Question]
    total_rounds: int
    current_round: int


class AnswerRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class AnswerResponse(BaseModel):
    next_question: Optional[Question] = None
    all_answered: bool = False
    current_round: int


class SpecSection(BaseModel):
    title: str
    content: str


class SpecResponse(BaseModel):
    session_id: str
    sections: List[SpecSection]
    raw_markdown: str
