import time

from google import genai
from google.genai import types

from app.config import settings
from app.models import ComicOutline


def get_client():
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key to the .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
) -> ComicOutline:

    prompt = f"""
You are a professional comic story planner.

Create a coherent five-panel comic outline.

USER STORY:
{story_prompt}

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

Requirements:

1. Create exactly 5 panels.
2. The story must have a clear beginning, middle and ending.
3. Keep the main character visually consistent.
4. Keep the setting consistent.
5. Each panel should move the story forward.
6. Give every panel a short title.
7. Give every panel a scene description.
8. Give every panel an image-generation prompt.
9. Do not put dialogue inside image_prompt.
10. Image prompts should describe characters, environment,
    composition, lighting and art style.
11. Do not request text, captions, speech bubbles or watermarks
    inside generated images.

Return only the structured response.
"""

    client = get_client()

    config = types.GenerateContentConfig(
        max_output_tokens=2500,
        response_mime_type="application/json",
        response_schema=ComicOutline,
    )

    # Retry temporary Gemini 503/429 errors.
    max_attempts = 3

    for attempt in range(max_attempts):
        try:
            response = client.models.generate_content(
                model=settings.gemini_flash_model,
                contents=prompt,
                config=config,
            )

            if not response.parsed:
                raise RuntimeError(
                    "Gemini did not return a valid comic outline."
                )

            return response.parsed

        except Exception as exc:
            error_text = str(exc)

            temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text
                or "high demand" in error_text.lower()
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            )

            if not temporary_error:
                raise

            if attempt == max_attempts - 1:
                raise RuntimeError(
                    "Gemini is temporarily unavailable because the "
                    "model is experiencing high demand. "
                    "Please wait a little and try again."
                ) from exc

            # Wait 2 seconds, then 4 seconds before retrying.
            wait_seconds = 2 ** (attempt + 1)
            time.sleep(wait_seconds)

    raise RuntimeError("Unable to generate the comic outline.")