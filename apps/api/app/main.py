from fastapi import FastAPI

from app.api.routes import admin, health, products, search, sources, submissions
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name, version="0.1.0")

app.include_router(health.router)
app.include_router(products.router)
app.include_router(search.router)
app.include_router(sources.router)
app.include_router(submissions.router)
app.include_router(admin.router)

