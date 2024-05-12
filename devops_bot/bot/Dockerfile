FROM python:3.10-alpine
WORKDIR /app

COPY requirements.txt .
RUN apk add --no-cache openssh

RUN pip install -r requirements.txt
COPY . .
CMD ["python3","bot.py"]
