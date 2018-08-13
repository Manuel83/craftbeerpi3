# Dockerfile for development on a pc/mac
FROM python:2

EXPOSE 5000

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run.py"]