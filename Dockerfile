From python:3.8-slim

EXPOSE 6767

RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
ADD ./app/

ENTRYPOINT ["python"]
CMD ["application.py"]
