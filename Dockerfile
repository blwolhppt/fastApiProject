FROM python:3.9

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DATABASE_URL="sqlite:///./db.db"
ENV PORT=8000

EXPOSE ${PORT}

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:${PORT}", "main:app"]