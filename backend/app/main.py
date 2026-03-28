from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import configure_logging
from app.api.v1 import drivers, search, admin, auth, companies, shortlists, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    yield


app = FastAPI(
    title="F1 Recruiting Backend",
    description="AI-powered F1 driver recruiting platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Phase 1 routers
app.include_router(drivers.router, prefix=f"{settings.api_v1_prefix}/drivers", tags=["drivers"])
app.include_router(search.router, prefix=f"{settings.api_v1_prefix}/search", tags=["search"])
app.include_router(admin.router, prefix=f"{settings.api_v1_prefix}/admin", tags=["admin"])

# Phase 2 routers
app.include_router(auth.router, prefix=f"{settings.api_v1_prefix}/auth", tags=["auth"])
app.include_router(companies.router, prefix=f"{settings.api_v1_prefix}/companies", tags=["companies"])
app.include_router(shortlists.router, prefix=f"{settings.api_v1_prefix}/shortlists", tags=["shortlists"])

# Phase 3 routers
app.include_router(chat.router, prefix=f"{settings.api_v1_prefix}/chat", tags=["chat"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "environment": settings.environment}
