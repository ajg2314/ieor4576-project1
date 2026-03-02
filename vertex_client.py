import os
from google import genai

def get_client() -> genai.Client:
    project = os.environ["GOOGLE_CLOUD_PROJECT"]
    location = os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1")
    # Vertex AI client
    return genai.Client(vertexai=True, project=project, location=location)

def generate_answer(prompt: str) -> str:
    model = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
    client = get_client()
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
    )
    # resp.text is the simplest way to get the output string
    return (resp.text or "").strip()