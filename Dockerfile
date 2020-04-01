FROM python:3.7-slim
FROM locustio/locust
ADD locustfile.py locustfile.py
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]