FROM python:3.12-slim
WORKDIR /app
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 WORKSHOP_ROOT=/app PORT=8080
COPY pyproject.toml requirements.txt constraints.txt ./
COPY src ./src
RUN pip install --no-cache-dir -c constraints.txt .
COPY data ./data
COPY labs ./labs
COPY scripts/serve.py ./scripts/serve.py
# Fit inside the image so training and serving use the same environment.
RUN python labs/1_model_packaging/train.py
USER 10001
EXPOSE 8080
CMD ["python", "scripts/serve.py"]
