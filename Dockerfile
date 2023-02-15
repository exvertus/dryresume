FROM python:3.11-slim

WORKDIR /usr/dryresume

COPY ./dist /usr/dryresume/dist

RUN pip install ./dist/dryresume-0.1.0-py3-none-any.whl
ENTRYPOINT [ "python", "-m", "dryresume.resume" ]
