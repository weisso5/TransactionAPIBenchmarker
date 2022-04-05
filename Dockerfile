FROM python:3.8.9
#RUN apk update \
#    apk add \
#    build-base \
#    postgresql \
#    postgresql-dev \
#    libpq \
#    libpq-dev \
#    python3-dev \
#    gcc \
#    libffi-dev \
#
#RUN apk add linux-headers
RUN python -m pip install --upgrade pip
WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]