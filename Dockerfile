FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /pod

COPY ./requirements.txt /pod/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /pod/requirements.txt

# COPY ./src /pod

# COPY ./static /pod/static

# CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]