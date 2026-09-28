import os

from openai import OpenAI


OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
USE_STUB_LLM = os.getenv("USE_STUB_LLM", "true").lower() == "true"


def stub_triage(symptoms: str, age: int) -> dict:
    text = symptoms.lower()

    emergency_keywords = [
        "difficulty breathing",
        "unconscious",
        "severe bleeding",
        "chest pain",
    ]

    urgent_keywords = [
        "high fever",
        "persistent vomiting",
        "severe pain",
    ]

    if any(keyword in text for keyword in emergency_keywords):
        urgency = "emergency"
        advice = (
            "Seek urgent medical attention immediately. "
            "This demo does not replace clinical assessment."
        )

    elif any(keyword in text for keyword in urgent_keywords):
        urgency = "urgent"
        advice = (
            "Arrange clinical review as soon as possible. "
            "This demo does not replace clinical assessment."
        )

    else:
        urgency = "routine"
        advice = (
            "Monitor symptoms and seek clinical review if symptoms worsen "
            "or do not improve."
        )

    return {
        "urgency": urgency,
        "advice": advice,
        "model_used": "stub-triage-v1",
    }


def assess_symptoms(symptoms: str, age: int) -> dict:
    if USE_STUB_LLM:
        return stub_triage(symptoms, age)

    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"]
    )

    system_message = (
        "You are an AfyaPlus triage support assistant. "
        "Return a concise urgency classification and safe next-step advice. "
        "Allowed urgency values: routine, urgent, emergency. "
        "Do not diagnose disease."
    )

    user_prompt = f"""
Patient age: {age}

Symptoms:
{symptoms}

Respond exactly in this format:

URGENCY: <routine|urgent|emergency>
ADVICE: <short safe next-step advice>
"""

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": system_message,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        temperature=0,
        max_tokens=150,
    )

    text = response.choices[0].message.content.strip()

    urgency = "routine"
    advice = text

    for line in text.splitlines():
        if line.upper().startswith("URGENCY:"):
            urgency = line.split(":", 1)[1].strip().lower()

        elif line.upper().startswith("ADVICE:"):
            advice = line.split(":", 1)[1].strip()

    return {
        "urgency": urgency,
        "advice": advice,
        "model_used": OPENAI_MODEL,
    }
