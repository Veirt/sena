FROM python:3.12-alpine

WORKDIR /app
COPY ./requirements.lock .

# https://github.com/mitsuhiko/rye/discussions/239
RUN sed '/-e/d' requirements.lock > requirements.txt && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH "/app/src"
CMD ["python", "-m", "the_fool"]
