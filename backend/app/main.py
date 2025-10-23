from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import scan_router

app = FastAPI(
    title="EquiScan API",
    description="Accessibility Compliance Scanner – WCAG audit tool",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0", "project": "EquiScan"}
