# CityCare app image: MediTrack, the Discharge Copilot service and the reset job.
# One image; the container's role is chosen at runtime with APP_ROLE (meditrack | copilot | reset).

FROM node:22-slim AS ui
WORKDIR /src
COPY legacy_meditrack/ui/package*.json legacy_meditrack/ui/
COPY copilot/ui/package*.json copilot/ui/
RUN cd legacy_meditrack/ui && npm ci --silent && cd ../../copilot/ui && npm ci --silent
COPY legacy_meditrack/ui legacy_meditrack/ui
COPY copilot/ui copilot/ui
RUN cd legacy_meditrack/ui && npm run build && cd ../../copilot/ui && npm run build

FROM python:3.13-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY legacy_meditrack legacy_meditrack
COPY copilot copilot
COPY copilot_core copilot_core
COPY scripts scripts
COPY --from=ui /src/legacy_meditrack/ui/dist legacy_meditrack/ui/dist
COPY --from=ui /src/copilot/ui/dist copilot/ui/dist
# file shares are mounted here (local: bind mounts, Azure: Azure Files)
ENV MEDITRACK_DOCS_DIR=/mnt/documents MEDITRACK_HOTFOLDER=/mnt/import_hotfolder COPILOT_DATA_DIR=/tmp/copilot
EXPOSE 8001 8002
ENTRYPOINT ["python", "-m", "scripts.serve"]
