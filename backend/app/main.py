from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.cases import router as cases_router
from app.api.documents import router as documents_router

app = FastAPI(title="Legal Doc Intelligence API")

app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(documents_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
