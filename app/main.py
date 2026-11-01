from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.api.routes import router
from app.core.config import BASE_DIR, get_settings
from app.core.logging import configure_logging
from app.services.audit import init_db

configure_logging()
init_db()

app = FastAPI(title=get_settings().app_name)
app.include_router(router)


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(BASE_DIR / "templates" / "index.html")
