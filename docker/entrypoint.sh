if [[ "${DEBUG}" == "true" ]]; then
    exec uvicorn app.main:app \
        --host "${BIND_ADDRESS:-0.0.0.0}" \
        --port "${BIND_PORT:-5000}" \
        --log-level debug
else
    exec gunicorn \
        --bind "${BIND_ADDRESS:-0.0.0.0}:${BIND_PORT:-5000}" \
        --workers ${SERVER_WORKERS:-1} \
        --worker-class ${SERVER_WORKER_CLASS:-gevent} \
        --worker-connections ${SERVER_WORKER_CONNECTIONS:-10} \
        --timeout ${GUNICORN_TIMEOUT:-200} \
        app.main:app
fi
