FROM python:3.8

# install supervisor
RUN apt update
RUN apt install -y supervisor && rm -rf /var/lib/apt/lists/*

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# enviroment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /app/

RUN pip install poetry

COPY pyproject.toml pyproject.toml

RUN poetry config virtualenvs.create false

RUN poetry install

COPY . .

CMD ["supervisord", "-c","supervisord.conf"]
