# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install dependencies and tools
RUN apt-get update && \
    apt-get install -y netcat-openbsd curl && \
    apt-get clean


# Set the working directory
WORKDIR /app

# Copy the application files
COPY requirements.txt requirements.txt
COPY ./app /app/app
COPY ./.env /app/.env
COPY ./alembic.ini /app/alembic.ini
COPY ./main.py /app/main.py
COPY ./install.sh /app/install.sh
COPY ./env.py /app/env.py

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Ensure the install.sh script is executable
RUN chmod +x /app/install.sh

# Expose the port the app runs on
EXPOSE 443

# Run the application
CMD ["/bin/sh", "/app/encrypto.sh"]
