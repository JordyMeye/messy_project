FROM python:3.9-slim

WORKDIR /app

# Install standard dependencies without external library bloat
RUN pip install --no-cache-dir mysql-connector-python flask

# Copy everything from your local directory into the container image
COPY . .

EXPOSE 8080

CMD ["python", "runserver.py"]