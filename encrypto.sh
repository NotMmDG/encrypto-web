#!/bin/sh

check_running_as_root() {
    if [ "$(id -u)" != "0" ]; then
        colorized_echo red "This command must be run as root."
        exit 1
    fi
}

detect_compose() {
    if docker compose >/dev/null 2>&1; then
        COMPOSE='docker compose'
        elif docker-compose >/dev/null 2>&1; then
        COMPOSE='docker-compose'
    else
        colorized_echo red "docker compose not found"
        exit 1
    fi
}

install_docker() {
    colorized_echo blue "Installing Docker"
    curl -fsSL https://get.docker.com | sh
    colorized_echo green "Docker installed successfully"
}
echo "Updating package lists..."
sudo apt-get update

echo "Installing Docker..."
sudo apt-get install -y docker.io

echo "Installing Docker Compose..."
sudo apt-get install -y docker-compose

echo "Installing Python dependencies..."
pip install --no-cache-dir -r requirements.txt

echo "Waiting for the MySQL server to be ready..."
while ! nc -z db 3306; do
  echo "Waiting for the MySQL server..."
  sleep 3
done

echo "Running Alembic migrations..."
PYTHONPATH=./app alembic upgrade head

echo "Starting the application with Uvicorn..."
uvicorn main:app --host 0.0.0.0 --port 443 --reload
