# Discharge Copilot POC (Streamlit). Sandbox image: the AI core + de-identified data only, no MediTrack code.
FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY copilot_core copilot_core
COPY poc poc
EXPOSE 8501
CMD ["streamlit", "run", "poc/app.py", "--server.port", "8501", "--server.address", "0.0.0.0", \
     "--server.headless", "true", "--browser.gatherUsageStats", "false"]
