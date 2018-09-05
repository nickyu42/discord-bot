FROM python:3.5-slim

RUN apt-get update && \
	apt-get -y install gcc && \
	rm -rf /var/lib/apt/lists/*

COPY requirements.txt /
RUN pip install -r requirements.txt

WORKDIR /app

ADD . /app

ENV NAME World

CMD ["python", "-u", "bot.py"]
