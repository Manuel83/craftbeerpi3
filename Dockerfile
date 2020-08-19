# Dockerfile for development on a pc/mac
FROM python:3.8

EXPOSE 5000

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]
