FROM python:3.6.1-alpine

WORKDIR /app
RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
CMD /usr/local/bin/python sadpandabot.py
