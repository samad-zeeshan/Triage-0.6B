# CPU image for the Triage service. The GGUF is fetched at build time from the release.
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY triage triage
COPY service service
COPY configs configs
COPY eval/results eval/results
RUN pip install --no-cache-dir --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu ".[service]" \
 && python -m triage.export fetch q6_k
ENV TRIAGE_THREADS=2
EXPOSE 8000
CMD ["uvicorn", "service.app:app", "--host", "0.0.0.0", "--port", "8000"]
