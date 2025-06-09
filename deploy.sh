#!/bin/bash

# Update system
sudo yum update -y

# Install Docker
sudo yum install -y docker
sudo service docker start
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Node.js
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
. ~/.nvm/nvm.sh
nvm install 16

# Clone repository
git clone https://github.com/Salman78687/CodeCrate.git
cd CodeCrate

# Build frontend
cd frontend
npm install
REACT_APP_API_URL=http://$(curl -s http://169.254.169.254/latest/meta-data/public-hostname):8000 npm run build

# Start backend
cd ..
docker-compose up -d 