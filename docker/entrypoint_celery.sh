if [[ "${MODE}" == "worker" ]]; then
    if [ "${CELERY_AUTO_SCALE,,}" = "true" ]; then
        # Get the number of available CPU cores
        AVAILABLE_CORES=$(nproc)
        MAX_WORKERS=${CELERY_MAX_WORKERS:-$AVAILABLE_CORES}
        MIN_WORKERS=${CELERY_MIN_WORKERS:-1}
        CONCURRENCY_OPTION="--autoscale=${MAX_WORKERS},${MIN_WORKERS}"
    else
        CONCURRENCY_OPTION="-c ${CELERY_WORKERS:-1}"
    fi

    exec celery -A app.celery worker \
            -P ${CELERY_WORKER_CLASS:-gevent} $CONCURRENCY_OPTION \
            --max-tasks-per-child ${MAX_TASK_PRE_CHILD:-50} \
            --loglevel ${LOG_LEVEL:-INFO} \
            -Q ${CELERY_QUEUES:-dataset,mail,ops_trace,app_deletion}
elif [[ "${MODE}" == "beat" ]]; then
    exec celery -A app.celery beat --loglevel ${LOG_LEVEL:-INFO}
elif [[ "${MODE}" == "flower" ]]; then
    exec celery -A app.celery flower --loglevel ${LOG_LEVEL:-INFO}
else
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
fi
