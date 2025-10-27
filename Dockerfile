FROM python:3.13.7


RUN apt-get update \
     && apt-get install -y --no-install-recommends \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --upgrade pip -r requirements.txt

COPY ./recipebot ./recipebot

CMD ["python", "-m", "recipebot.main"]
