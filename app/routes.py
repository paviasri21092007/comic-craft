from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    FileResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from app.config import settings

from app.models import (
    PromptRequest,
    TestImageRequest
)

from app.services.gemini_flash import (
    generate_outline
)

from app.services.gemini_pro import (
    generate_story
)

from app.services.image_generator import (
    generate_image
)

from app.services.layout_builder import (
    build_comic_layout
)

from app.services.exporters import (
    save_pdf
)

from app.utils.files import (
    public_static_path
)


router = APIRouter()


templates = Jinja2Templates(
    directory=str(
        settings.templates_dir
    )
)


def generate_comic(data: PromptRequest):

    # STEP 1
    # Generate five-panel outline

    outline = generate_outline(

        data.story_prompt,

        data.character_name,

        data.setting,

        data.tone,

        data.art_style
    )

    # STEP 2
    # Generate complete story

    story = generate_story(

        outline,

        data.character_name,

        data.setting,

        data.tone,

        data.art_style
    )

    # STEP 3
    # Generate images

    image_paths = []

    for panel in story.panels:

        image_path = generate_image(

            panel.image_prompt,

            panel.panel_number,

            data.character_name
        )

        image_paths.append(
            image_path
        )

    # STEP 4
    # Build layout

    layout = build_comic_layout(

        story,

        image_paths
    )

    # STEP 5
    # Export PDF

    pdf_path = save_pdf(
        layout
    )

    return (
        layout,
        pdf_path,
        outline,
        story
    )


@router.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(

        request=request,

        name="index.html",

        context={
            "title":
                settings.app_name
        }
    )


@router.post(
    "/generate",
    response_class=HTMLResponse
)
async def generate(

    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...)
):

    data = PromptRequest(

        story_prompt=story_prompt,

        character_name=character_name,

        setting=setting,

        tone=tone,

        art_style=art_style
    )

    try:

        (
            layout,
            pdf_path,
            outline,
            story
        ) = generate_comic(data)

        serializable_layout = []

        for panel in layout:

            panel_copy = dict(
                panel
            )

            panel_copy["image_path"] = (
                public_static_path(
                    panel["image_path"],
                    settings.static_dir
                )
            )

            serializable_layout.append(
                panel_copy
            )

        pdf_url = public_static_path(
            pdf_path,
            settings.static_dir
        )

        return templates.TemplateResponse(

            request=request,

            name="comic_preview.html",

            context={

                "title":
                    "Comic Preview",

                "layout":
                    serializable_layout,

                "pdf_url":
                    pdf_url,

                "story_input":
                    data,

                "outline":
                    outline,

                "story":
                    story
            }
        )

    except Exception as error:

        return templates.TemplateResponse(

            request=request,

            name="error.html",

            context={

                "title":
                    "Generation Error",

                "error":
                    str(error)
            },

            status_code=500
        )


@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    data: PromptRequest
):

    try:

        (
            layout,
            pdf_path,
            outline,
            story
        ) = generate_comic(data)

        response_layout = []

        for panel in layout:

            panel_copy = dict(
                panel
            )

            panel_copy["image_path"] = (
                public_static_path(
                    panel["image_path"],
                    settings.static_dir
                )
            )

            response_layout.append(
                panel_copy
            )

        return {

            "success":
                True,

            "panels":
                response_layout,

            "pdf_path":
                public_static_path(
                    pdf_path,
                    settings.static_dir
                ),

            "outline":
                outline.model_dump(),

            "story":
                story.model_dump()
        }

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


@router.post(
    "/test-image"
)
async def test_image(
    data: TestImageRequest
):

    try:

        path = generate_image(

            data.prompt,

            panel_number=0,

            character_name="test"
        )

        return {

            "success":
                True,

            "image_path":
                public_static_path(
                    path,
                    settings.static_dir
                )
        }

    except Exception as error:

        raise HTTPException(

            status_code=500,

            detail=str(error)
        )


@router.get(
    "/download/{filename}"
)
async def download(
    filename: str
):

    safe_name = Path(
        filename
    ).name

    target = (
        settings.exports_dir /
        safe_name
    ).resolve()

    exports_root = (
        settings.exports_dir
        .resolve()
    )

    if (
        exports_root not in target.parents
        or not target.exists()
    ):

        raise HTTPException(
            status_code=404,
            detail="PDF not found."
        )

    return FileResponse(

        path=str(target),

        media_type="application/pdf",

        filename=target.name
    )


@router.get(
    "/export-success",
    response_class=HTMLResponse
)
async def export_success(

    request: Request,

    pdf: str = ""
):

    return templates.TemplateResponse(

        request=request,

        name="export_success.html",

        context={

            "title":
                "Export Successful",

            "pdf_url":
                pdf
        }
    )