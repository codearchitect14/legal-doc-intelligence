from fastapi import FastAPI

from app.api.analysis import router as analysis_router
from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.documents import router as documents_router
from app.api.draft import router as draft_router
from app.core.logging_config import RequestLoggingMiddleware, configure_logging

configure_logging()

app = FastAPI(title="Legal Doc Intelligence API")
app.add_middleware(RequestLoggingMiddleware)

app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(documents_router)
app.include_router(analysis_router)
app.include_router(draft_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
