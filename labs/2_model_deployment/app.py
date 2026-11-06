"""Program 2: load once at startup, then serve predictions and a webpage."""
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator

from sms_mlops.common import DEFAULT_MODEL, load_artifact


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Fail startup clearly if the model is missing or incompatible.
    path = Path(os.environ.get("MODEL_PATH", str(DEFAULT_MODEL)))
    app.state.model, app.state.metadata = load_artifact(path)
    yield
    del app.state.model


app = FastAPI(title="SMS Spam Filter", version="1.0.0", lifespan=lifespan)


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(min_length=1, max_length=2000, strict=True)

    @field_validator("message")
    @classmethod
    def require_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must contain text")
        return value.strip()


class PredictionResponse(BaseModel):
    label: str
    model_version: str


@app.get("/", include_in_schema=False)
def webpage():
    return FileResponse(Path(__file__).with_name("index.html"))


@app.get("/health")
def health():
    return {"status": "ready", "model_version": app.state.metadata["model_version"]}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    label = app.state.model.predict([request.message])[0]
    # Do not log SMS contents. This demo also does not store user messages.
    return PredictionResponse(label=str(label), model_version=app.state.metadata["model_version"])
