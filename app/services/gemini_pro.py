from google import genai
from google.genai import types

from app.config import settings
from app.models import ComicOutline, ComicStory


def get_client():

    if not settings.gemini_api_key:

        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Please add your Gemini API key to the .env file."
        )

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def generate_story(
    outline: ComicOutline,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str
) -> ComicStory:

    outline_json = outline.model_dump_json(
        indent=2
    )

    prompt = f"""
You are a professional comic book writer.

Expand the following five-panel outline into a complete
comic script.

MAIN CHARACTER:
{character_name}

SETTING:
{setting}

TONE:
{tone}

ART STYLE:
{art_style}

OUTLINE:
{outline_json}

Requirements:

1. Preserve exactly 5 panels.
2. Keep the same characters throughout.
3. Keep the environment visually consistent.
4. Every panel needs:
   - panel_number
   - title
   - scene_description
   - caption
   - narration
   - dialogue
   - image_prompt

5. Narration must be concise.
6. Dialogue should sound natural.
7. The story should have a clear ending.
8. image_prompt should describe only visual information.
9. Do not put words, letters, subtitles, logos,
   speech bubbles or watermarks inside image_prompt.
10. Keep the content suitable for a general audience.

Return only the structured response.
"""

    client = get_client()

    response = client.models.generate_content(

        model=settings.gemini_pro_model,

        contents=prompt,

        config=types.GenerateContentConfig(

            temperature=0.95,

            max_output_tokens=5000,

            response_mime_type="application/json",

            response_schema=ComicStory
        )
    )

    if not response.parsed:

        raise RuntimeError(
            "Gemini did not return a valid comic story."
        )

    return response.parsed