import os
import time
import random

from dotenv import load_dotenv
from google import genai
from google.genai import types


# -------------------------------------------------
# ENVIRONMENT
# -------------------------------------------------

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

EMBEDDING_MODEL = "gemini-embedding-001"
EMBEDDING_DIMENSION = 768


if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Please check your .env file."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# -------------------------------------------------
# RETRY SETTINGS
# -------------------------------------------------

MAX_RETRIES = 6

INITIAL_WAIT_TIME = 5


# -------------------------------------------------
# RETRY FUNCTION
# -------------------------------------------------

def run_with_retry(function):

    for attempt in range(MAX_RETRIES):

        try:

            return function()

        except Exception as error:

            error_text = str(error).lower()

            retryable_error = (
                "429" in error_text
                or "resource_exhausted" in error_text
                or "rate limit" in error_text
                or "503" in error_text
                or "unavailable" in error_text
            )

            if not retryable_error:
                raise


            if attempt == MAX_RETRIES - 1:
                print(
                    "\nMaximum retry attempts reached."
                )
                raise


            wait_time = (
                INITIAL_WAIT_TIME
                * (2 ** attempt)
            )

            # Small random delay prevents repeated
            # requests at exactly the same interval.

            wait_time += random.uniform(0, 2)


            print(
                f"\nAPI temporarily unavailable "
                f"or rate limited."
            )

            print(
                f"Retry {attempt + 1}/"
                f"{MAX_RETRIES - 1}"
            )

            print(
                f"Waiting {wait_time:.1f} seconds..."
            )


            time.sleep(wait_time)


# -------------------------------------------------
# SINGLE DOCUMENT EMBEDDING
# -------------------------------------------------

def embed_document(text):

    def request():

        return client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSION
            )
        )


    response = run_with_retry(
        request
    )


    return response.embeddings[0].values


# -------------------------------------------------
# BATCH DOCUMENT EMBEDDINGS
# -------------------------------------------------

def embed_documents(texts):

    if not texts:
        return []


    def request():

        return client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texts,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_DOCUMENT",
                output_dimensionality=EMBEDDING_DIMENSION
            )
        )


    response = run_with_retry(
        request
    )


    return [
        embedding.values
        for embedding in response.embeddings
    ]


# -------------------------------------------------
# QUERY EMBEDDING
# -------------------------------------------------

def embed_query(text):

    def request():

        return client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=text,
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                output_dimensionality=EMBEDDING_DIMENSION
            )
        )


    response = run_with_retry(
        request
    )


    return response.embeddings[0].values