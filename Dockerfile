FROM python:3.10-slim

WORKDIR /app

# Install the native mysql connector using pip during build time
RUN pip install --no-cache-dir mysql-connector-python

COPY runserver.py .

EXPOSE 8080

CMD ["python", "runserver.py"]