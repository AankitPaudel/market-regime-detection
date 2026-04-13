from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import predict as predict_router
from app.routers import retrain as retrain_router
from app.pipeline.predict import load_models
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Market Regime API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-vercel-app.vercel.app",  # update after deploy
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    load_models()


app.include_router(predict_router.router, prefix="/api", tags=["Predictions"])
app.include_router(retrain_router.router, prefix="/api", tags=["Retrain"])


@app.get("/")
def root():
    return {"message": "Market Regime Detection API v2.0 — by Ankit Paudel"}
