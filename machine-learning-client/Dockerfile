FROM python:3.10-slim

WORKDIR /app

RUN pip install pipenv

COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy

COPY . .

EXPOSE 5001

CMD ["python", "app.py"]
