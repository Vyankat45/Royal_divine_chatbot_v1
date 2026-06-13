from fastapi import APIRouter
from pydantic import BaseModel

from app.rag_service import ask_question

router = APIRouter()


class QuestionRequest(BaseModel):
    question: str


@router.post("/ask")
def ask(request: QuestionRequest):

    answer = ask_question(request.question)

    return {
        "answer": answer
    }