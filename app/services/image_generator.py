from pathlib import Path
from threading import Lock
from datetime import datetime
import textwrap

from PIL import Image, ImageDraw, ImageFont

from app.config import settings
from app.utils.files import safe_filename


_pipeline = None

_pipeline_lock = Lock()


def create_placeholder(
    prompt: str,
    output_path: Path
) -> Path:

    width = settings.image_width

    height = settings.image_height

    image = Image.new(
        "RGB",
        (width, height),
        (245, 238, 220)
    )

    draw = ImageDraw.Draw(image)

    # Outer comic border

    draw.rectangle(
        (
            8,
            8,
            width - 8,
            height - 8
        ),
        outline=(20, 20, 20),
        width=8
    )

    # Inner frame

    draw.rectangle(
        (
            35,
            35,
            width - 35,
            height - 155
        ),
        outline=(40, 40, 40),
        width=4
    )

    try:

        font = ImageFont.truetype(
            "arial.ttf",
            24
        )

        small_font = ImageFont.truetype(
            "arial.ttf",
            16
        )

    except Exception:

        font = ImageFont.load_default()

        small_font = ImageFont.load_default()

    draw.text(
        (55, 55),
        "ComicCraft",
        fill=(10, 10, 10),
        font=font
    )

    wrapped = textwrap.fill(
        prompt,
        width=55
    )

    draw.multiline_text(
        (50, height - 135),
        wrapped,
        fill=(10, 10, 10),
        font=small_font,
        spacing=5
    )

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    image.save(
        output_path,
        "PNG"
    )

    return output_path


def get_pipeline():

    global _pipeline

    if _pipeline is not None:

        return _pipeline

    with _pipeline_lock:

        if _pipeline is not None:

            return _pipeline

        import torch

        from diffusers import StableDiffusionPipeline

        if torch.cuda.is_available():

            dtype = torch.float16

        else:

            dtype = torch.float32

        kwargs = {
            "torch_dtype": dtype,
            "use_safetensors": True
        }

        if settings.hf_api_key:

            kwargs["token"] = settings.hf_api_key

        _pipeline = (
            StableDiffusionPipeline
            .from_pretrained(
                settings.image_model_id,
                **kwargs
            )
        )

        if torch.cuda.is_available():

            _pipeline = _pipeline.to("cuda")

        else:

            _pipeline = _pipeline.to("cpu")

        return _pipeline


def generate_image(
    image_prompt: str,
    panel_number: int,
    character_name: str = "Hero"
) -> Path:

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S_%f"
    )

    filename = (
        f"panel_{panel_number}_"
        f"{safe_filename(character_name)}_"
        f"{timestamp}.png"
    )

    output_path = (
        settings.panels_dir /
        filename
    )

    # Easy testing mode

    if not settings.enable_local_diffusion:

        return create_placeholder(
            image_prompt,
            output_path
        )

    try:

        pipe = get_pipeline()

        prompt = (
            f"{image_prompt}, "
            f"high quality comic illustration, "
            f"cinematic lighting, "
            f"clear composition, "
            f"expressive characters"
        )

        negative_prompt = (
            "text, words, letters, subtitles, "
            "watermark, logo, blurry, distorted, "
            "extra limbs, malformed hands"
        )

        result = pipe(

            prompt=prompt,

            negative_prompt=negative_prompt,

            width=settings.image_width,

            height=settings.image_height,

            num_inference_steps=settings.image_steps,

            guidance_scale=settings.image_guidance
        )

        result.images[0].save(
            output_path
        )

        return output_path

    except Exception as error:

        # Keep application working if
        # Stable Diffusion fails.

        fallback_prompt = (
            f"Image generation fallback.\n"
            f"Reason: {type(error).__name__}\n\n"
            f"{image_prompt}"
        )

        return create_placeholder(
            fallback_prompt,
            output_path
        )