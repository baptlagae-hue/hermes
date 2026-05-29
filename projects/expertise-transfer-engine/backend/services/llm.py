import os
import json
from openai import OpenAI

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
MODEL = os.getenv("LLM_MODEL", "deepseek-chat")

_client = None


def get_client():
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
    return _client


def generate_questions(transcript: str, answered_context: str = "", round_num: int = 1) -> list[dict]:
    client = get_client()
    base_prompt = (
        "You are an expert interviewer whose job is to extract deep domain expertise from a specialist. "
        "The user has described their work and expertise in a voice recording. "
        "Your goal is to ask targeted questions that uncover:\n"
        "- Their specific domain model (entities, relationships, key concepts)\n"
        "- Their unique business rules and methodologies\n"
        "- Edge cases and exceptions they handle instinctively\n"
        "- Metrics and analytics they consider critical\n"
        "- The tools, data sources, and processes they use\n"
        "- Pain points and friction in their current workflow\n\n"
        "Generate no more than 3 precise, specific questions per round. "
        "Each question should be a single sentence, focused on ONE specific gap in understanding. "
        "Do NOT ask generic questions — they should sound like they come from someone who truly wants to capture their unique expertise.\n\n"
        "Return as JSON array: [{\"id\": \"q1\", \"text\": \"...\", \"category\": \"domain_model|business_rules|edge_cases|metrics|tools|pain_points\"}, ...]"
    )

    messages = [
        {"role": "system", "content": base_prompt},
        {"role": "user", "content": f"Here is the expert's initial recording transcript:\n\n{transcript}"}
    ]

    if answered_context:
        messages.append({"role": "user", "content": f"So far answered:\n{answered_context}\n\nGenerate follow-up questions to go deeper."})

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.7,
        response_format={"type": "json_object"}
    )

    content = resp.choices[0].message.content
    data = json.loads(content)
    if isinstance(data, dict) and "questions" in data:
        return data["questions"]
    return data if isinstance(data, list) else []


def generate_spec(transcript: str, qa_pairs: list[dict]) -> str:
    client = get_client()
    prompt = (
        "You are a senior product designer and technical architect. "
        "Based on the following interview with a domain expert, produce a comprehensive "
        "technical specification document in markdown. The spec must feel authored by "
        "someone with deep domain knowledge — not generic AI output.\n\n"
        "Include these sections:\n"
        "1. **Domain Overview** — what the expert does, their core expertise\n"
        "2. **Domain Model** — entities, relationships, business rules (as a Mermaid class diagram if possible)\n"
        "3. **Technical Architecture** — recommended stack, system design outline\n"
        "4. **User Stories & Feature Roadmap** — what the application should do, in priority order\n"
        "5. **Data Model** — key tables/collections and their schema\n"
        "6. **Analytics & Metrics** — KPIs the expert considers critical (this is their specialty!)\n"
        "7. **Edge Cases & Constraints** — limitations, exceptions, tricky parts\n"
        "8. **Implementation Roadmap** — MVP → v2 → beyond\n\n"
        "Write in English. Be specific and concrete. Reference the expert's own terminology and methods."
    )

    interview_text = f"## Initial Recording\n{transcript}\n\n## Q&A\n"
    for qa in qa_pairs:
        interview_text += f"\n**Q:** {qa['question']}\n**A:** {qa['answer']}\n"

    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": interview_text}
    ]

    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0.5,
        max_tokens=4096
    )

    return resp.choices[0].message.content
