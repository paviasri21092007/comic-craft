from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


class Settings:
    app_name = "ComicCraft"

    base_dir = BASE_DIR

    templates_dir = BASE_DIR / "templates"

    static_dir = BASE_DIR / "static"

    panels_dir = static_dir / "panels"

    exports_dir = static_dir / "exports"

    # Gemini
    gemini_api_key = os.getenv("GEMINI_API_KEY", "")

    gemini_flash_model = os.getenv(
        "GEMINI_FLASH_MODEL",
        "gemini-2.5-flash"
    )

    gemini_pro_model = os.getenv(
        "GEMINI_PRO_MODEL",
        "gemini-2.5-pro"
    )

    # Hugging Face
    hf_api_key = os.getenv("HF_API_KEY", "")

    # Image generation
    image_model_id = os.getenv(
        "IMAGE_MODEL_ID",
        "stable-diffusion-v1-5/stable-diffusion-v1-5"
    )

    enable_local_diffusion = (
        os.getenv(
            "ENABLE_LOCAL_DIFFUSION",
            "false"
        ).lower()
        in {"true", "1", "yes", "on"}
    )

    image_width = int(
        os.getenv("IMAGE_WIDTH", "512")
    )

    image_height = int(
        os.getenv("IMAGE_HEIGHT", "512")
    )

    image_steps = int(
        os.getenv("IMAGE_STEPS", "20")
    )

    image_guidance = float(
        os.getenv("IMAGE_GUIDANCE", "7.5")
    )

    host = os.getenv(
        "HOST",
        "127.0.0.1"
    )

    port = int(
        os.getenv(
            "PORT",
            "8000"
        )
    )


settings = Settings()


settings.static_dir.mkdir(
    parents=True,
    exist_ok=True
)

settings.panels_dir.mkdir(
    parents=True,
    exist_ok=True
)

settings.exports_dir.mkdir(
    parents=True,
    exist_ok=True
)