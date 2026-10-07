# The only public entry point: MediTrack at /, the Discharge Copilot at /copilot/ (same origin for the embedded tab).
FROM caddy:2-alpine
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
EXPOSE 80
ENTRYPOINT ["/entrypoint.sh"]
