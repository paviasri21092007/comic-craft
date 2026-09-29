from fastapi import FastAPI

from fastapi.staticfiles import (
    StaticFiles
)

from app.config import settings

from app.routes import router


app = FastAPI(

    title="ComicCraft API",

    description=(
        "AI Comic Story Creator "
        "using Gemini and Diffusers"
    ),

    version="1.0.0"
)


app.mount(

    "/static",

    StaticFiles(
        directory=str(
            settings.static_dir
        )
    ),

    name="static"
)


app.include_router(
    router
)


@app.get("/health")
async def health():

    return {

        "status":
            "ok",

        "app":
            settings.app_name,

        "gemini_configured":
            bool(
                settings.gemini_api_key
            ),

        "local_diffusion_enabled":
            settings.enable_local_diffusion
    }