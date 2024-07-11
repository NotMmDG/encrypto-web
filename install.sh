#!/bin/bash

set -e

echo "Updating package index..."
sudo apt-get update

echo "Installing prerequisite packages..."
sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common

echo "Adding Docker's official GPG key..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

echo "Adding Docker APT repository..."
sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

echo "Updating package index again..."
sudo apt-get update

echo "Installing Docker CE..."
sudo apt-get install -y docker-ce

echo "Adding current user to the docker group..."
sudo usermod -aG docker $USER

echo "Downloading Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

echo "Applying executable permissions to Docker Compose binary..."
sudo chmod +x /usr/local/bin/docker-compose

echo "Verifying Docker Compose installation..."
docker-compose --version

echo "Building and running Docker containers..."
sudo docker-compose up --build -d

echo "Installation and setup complete!"
