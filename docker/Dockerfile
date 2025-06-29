# base image
FROM python:3.12-slim-bookworm AS base

WORKDIR /opt/tinyrag

ENV UV_VERSION=0.7.15

RUN pip install --no-cache-dir uv==${UV_VERSION} -i https://mirrors.ustc.edu.cn/pypi/simple

FROM base AS packages

# if you located in China, you can use aliyun mirror to speed up
RUN sed -i 's@deb.debian.org@mirrors.aliyun.com@g' /etc/apt/sources.list.d/debian.sources

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ libc-dev libffi-dev libgmp-dev libmpfr-dev libmpc-dev

COPY pyproject.toml uv.lock ./
RUN uv sync --locked

FROM base AS production

ENV ENVIRONMENT=production
ENV TZ=UTC

EXPOSE 5000

# Copy Python environment and packages
ENV VIRTUAL_ENV=/opt/tinyrag/.venv
COPY --from=packages ${VIRTUAL_ENV} ${VIRTUAL_ENV}
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}"

# Copy source code
COPY . /opt/tinyrag/

COPY docker/entrypoint.sh /entrypoint.sh
COPY .env.example /opt/tinyrag/.env

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
