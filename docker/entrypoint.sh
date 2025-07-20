if [[ "${MODE}" == "worker" ]]; then
    exec python -m app
else
    if [[ "${DEBUG}" == "true" ]]; then
        exec granian --interface asgi app:app \
            --host "${BIND_ADDRESS:-0.0.0.0}" \
            --port "${BIND_PORT:-8000}" \
            --access-log --log-level debug
    else
        access_log_opt="--access-log"
        if [[ "${GRANIAN_LOG_ACCESS_ENABLED}" == "disabled" ]]; then
            access_log_opt="--no-access-log"
        fi

        # --host ${GRANIAN_HOST:-127.0.0.1} --port ${GRANIAN_PORT:8000}
        # --workers ${GRANIAN_WORKERS:-1}
        # --backlog ${GRANIAN_BACKLOG:-1024}
        # --log-level ${GRANIAN_LOG_LEVEL:-info}
        exec granian --interface asgi app:app \
            --host "${GRANIAN_HOST:-0.0.0.0}" \
            --env-files ${GRANIAN_ENV_FILES:-.env} \
            $access_log_opt
    fi
fi
