FROM debian:buster-slim

RUN apt-get update && apt-get install -y \
    python3-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY . /app

ENTRYPOINT ["python3"]

EXPOSE 5000

CMD ["app.py"]