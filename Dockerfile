FROM python:3.11.4-alpine3.18

WORKDIR /code

# Supercronic to run cron jobs
ENV SUPERCRONIC_URL=https://github.com/aptible/supercronic/releases/download/v0.2.25/supercronic-linux-amd64 \
    SUPERCRONIC=supercronic-linux-amd64 \
    SUPERCRONIC_SHA1SUM=642f4f5a2b67f3400b5ea71ff24f18c0a7d77d49

RUN apk --no-cache add curl
RUN curl -fsSLO "$SUPERCRONIC_URL" \
    && echo "${SUPERCRONIC_SHA1SUM}  ${SUPERCRONIC}" | sha1sum -c - \
    && chmod +x "$SUPERCRONIC" \
    && mv "$SUPERCRONIC" "/usr/local/bin/${SUPERCRONIC}" \
    && ln -s "/usr/local/bin/${SUPERCRONIC}" /usr/local/bin/supercronic

# Poetry for dependency management
RUN pip install "poetry==1.4.2"
RUN poetry config virtualenvs.create false

# Set environment variables
ENV PYTHONPATH=${PYTHONPATH}:${PWD}

# Copy only requirements to cache them in docker layer
COPY poetry.lock pyproject.toml /code/

# Project initialization
RUN poetry install --no-dev --no-interaction --no-ansi

# Creating folders, and files for a project
COPY . /code

# Set cron job
RUN echo "@daily scrapy crawl alphastreet" > crontab
RUN TZ=Asia/Kolkata supercronic crontab &

# Update the database
RUN scrapy crawl alphastreet

# Run the webserver
CMD ["uvicorn", "api.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]
