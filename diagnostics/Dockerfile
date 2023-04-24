FROM python:3.9.5-slim-buster AS base

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# create non-root user
RUN groupadd -r runtime && \
    useradd -r -g runtime runtime

# use runtime users home directory as workdir
WORKDIR /home/runtime

# install minimal requirements
COPY ./requirements.txt /home/runtime/requirements.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# copy python package and chown to runtime user
COPY --chown=runtime:runtime ./tasks.py /home/runtime/tasks.py

# production image runs with non-root runtime user
FROM base as prod

USER runtime