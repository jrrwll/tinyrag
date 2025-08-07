if [[ "${MODE}" == "worker" ]]; then
    exec python -m app.tasks.worker
elif [[ "${MODE}" == "scheduler" ]]; then
    exec python -m app.tasks.scheduler
else
    if [[ "${DEBUG}" == "true" ]]; then
        exec granian --interface asgi app:app \
            --host "${BIND_ADDRESS:-0.0.0.0}" \
            --port "${BIND_PORT:-8000}" \
            --access-log --log-level debug
    else
        # --host ${GRANIAN_HOST:-127.0.0.1} --port ${GRANIAN_PORT:8000}
        # --workers ${GRANIAN_WORKERS:-1}
        # --backlog ${GRANIAN_BACKLOG:-1024}
        # --log-level ${GRANIAN_LOG_LEVEL:-info}
        exec granian --interface asgi app:app \
            --host "${GRANIAN_HOST:-0.0.0.0}" \
            --port ${GRANIAN_PORT:8000} \
            --env-files ${GRANIAN_ENV_FILES:-.env}
    fi
fi
