FROM python:2.7

COPY . /app

WORKDIR app

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "run.py" ]