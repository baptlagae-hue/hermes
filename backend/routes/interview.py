from fastapi import APIRouter, HTTPException
from models.schema import (
    QuestionRequest, QuestionsResponse, Question,
    AnswerRequest, AnswerResponse,
)

router = APIRouter(prefix="/api")

# Reuse the same _sessions dict from voice.py
# In a real app this would be a proper session store
from routes.voice import _sessions


@router.post("/questions", response_model=QuestionsResponse)
async def get_questions(req: QuestionRequest):
    from services.llm import generate_questions

    session = _sessions.get(req.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    transcript = session["transcript"]
    answered = session["answers_context"]
    round_num = len(session["qa_pairs"]) // 3 + 1

    questions = generate_questions(transcript, answered, round_num)

    session["current_questions"] = questions

    return QuestionsResponse(
        questions=[Question(**q) for q in questions],
        total_rounds=10,
        current_round=round_num,
    )


@router.post("/answer", response_model=AnswerResponse)
async def submit_answer(req: AnswerRequest):
    from services.llm import generate_questions

    session = _sessions.get(req.session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    # Find which question was answered
    current_qs = session.get("current_questions", [])
    answered_q = next((q for q in current_qs if q["id"] == req.question_id), None)

    if not answered_q:
        raise HTTPException(400, f"Question {req.question_id} not found in current round")

    # Store the Q&A pair
    session["qa_pairs"].append({
        "question": answered_q["text"],
        "answer": req.answer,
    })
    session["answers_context"] += f"\nQ: {answered_q['text']}\nA: {req.answer}\n"

    round_num = len(session["qa_pairs"]) // 3 + 1

    # Check if we've done enough rounds
    if len(session["qa_pairs"]) >= 15 or round_num > 10:
        return AnswerResponse(all_answered=True, current_round=round_num)

    # Generate next round of questions
    remaining_qs = [q for q in current_qs if q["id"] != req.question_id]

    if remaining_qs:
        next_q = remaining_qs[0]
        session["remaining"] = remaining_qs[1:]
        return AnswerResponse(
            next_question=Question(**next_q),
            all_answered=False,
            current_round=round_num,
        )

    # All questions in this round answered — get new ones
    transcript = session["transcript"]
    answered = session["answers_context"]
    new_questions = generate_questions(transcript, answered, round_num)

    if not new_questions:
        return AnswerResponse(all_answered=True, current_round=round_num)

    session["current_questions"] = new_questions
    return AnswerResponse(
        next_question=Question(**new_questions[0]),
        all_answered=False,
        current_round=round_num,
    )
