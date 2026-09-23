import os

from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()


API_KEY = os.getenv("LLM_API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL")
MODEL_NAME = os.getenv("LLM_MODEL")


if not API_KEY:
    raise ValueError(
        "LLM_API_KEY is missing. Please check your environment variables."
    )

if not BASE_URL:
    raise ValueError(
        "LLM_BASE_URL is missing. Please check your environment variables."
    )

if not MODEL_NAME:
    raise ValueError(
        "LLM_MODEL is missing. Please check your environment variables."
    )


client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


def generate_answer(question, context):

    response = client.chat.completions.create(
        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are an SSC examination support assistant. "
                    "Answer only from the SSC FAQ context provided to you. "
                    "Do not use outside knowledge to answer SSC-specific questions. "
                    "If the answer is not present in the context, clearly say that "
                    "the information is not available in the provided SSC FAQs. "
                    "Do not invent dates, eligibility criteria, fees, vacancies, "
                    "age limits, or examination rules. "
                    "Keep the answer clear and easy for applicants to understand."
                )
            },
            {
                "role": "user",
                "content": f"""
SSC FAQ CONTEXT:

{context}


APPLICANT QUESTION:

{question}
"""
            }
        ],

        temperature=0
    )

    return response.choices[0].message.content