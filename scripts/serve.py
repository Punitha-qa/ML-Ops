"""Container entrypoint. Cloud Run supplies PORT, defaulting here to 8080."""
import os
import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "labs/2_model_deployment"))

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
