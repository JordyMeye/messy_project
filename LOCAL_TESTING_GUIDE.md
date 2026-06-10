# Local Testing Guide - Before Deployment

This guide helps you test all components locally before pushing to GitHub and deploying to the VM.

---

## Part 1: Test Flask Application Locally

### 1.1 Set up Python environment

```bash
# Navigate to project directory
cd /path/to/DevOps

# Create virtual environment
python3 -m venv test-env

# Activate it
# On Linux/Mac:
source test-env/bin/activate
# On Windows:
test-env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify Flask is installed
pip list | grep Flask
# Should show: Flask 3.0.0 or higher
```

### 1.2 Test /version endpoint locally

```bash
# Start Flask development server
python runserver.py

# In another terminal, test the endpoint:
curl http://localhost:5000/version
# Expected output: {"version":"1.0"}

# Or test other endpoints:
curl http://localhost:5000/
curl http://localhost:5000/about
curl http://localhost:5000/contact

# Stop the server
# Ctrl+C in the terminal
```

### 1.3 Run unit tests

```bash
# Run pytest
pytest FlaskWebProject1/tests/ -v

# Run with coverage
pytest FlaskWebProject1/tests/ --cov=FlaskWebProject1
```

---

## Part 2: Test Docker Image Locally

### 2.1 Build Docker image

```bash
# From project root directory
docker build -t my-app:latest .

# Check if build succeeded
docker images | grep my-app
# Should show: my-app    latest    sha256:abc123...    < 1 minute ago

# View image layers (optional)
docker history my-app:latest
```

### 2.2 Run Docker container

```bash
# Run container in detached mode (background)
docker run -d \
  --name test-app \
  -p 8081:8080 \
  my-app:latest

# Verify container is running
docker ps | grep test-app

# Check container logs
docker logs test-app
# Should see Flask server starting on port 8080
```

### 2.3 Test /version endpoint in container

```bash
# Method 1: curl from host machine
curl http://localhost:8081/version
# Expected: {"version":"1.0"}

# Method 2: curl from inside container
docker exec test-app curl http://localhost:8080/version

# Method 3: In web browser
# Visit: http://localhost:8081/version
```

### 2.4 Inspect running container

```bash
# View container details
docker inspect test-app | grep -E '"NetworkMode"|"PortBindings"|"Status"'

# Check memory/CPU usage
docker stats test-app

# View recent logs (last 50 lines)
docker logs test-app --tail 50

# View real-time logs
docker logs -f test-app
# Press Ctrl+C to exit
```

### 2.5 Test with docker-compose locally

```bash
# Verify docker-compose syntax
docker-compose config

# Start services
docker-compose up -d

# Check status
docker-compose ps
# Should show both mysql-db and webapp_v2 as "running"

# Test from host
curl http://localhost:8081/version

# View logs from both services
docker-compose logs
docker-compose logs -f webapp_v2

# Stop services (keeps data)
docker-compose stop

# Remove containers (keeps volumes)
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

### 2.6 Clean up

```bash
# Stop container
docker stop test-app

# Remove container
docker rm test-app

# Remove image
docker rmi my-app:latest

# Verify cleanup
docker ps -a
docker images
```

---

## Part 3: Test Docker Hub Push

### 3.1 Create Docker Hub account and repository

1. Go to https://hub.docker.com
2. Sign up or login
3. Click "Create Repository"
4. Name: `my-app`
5. Visibility: Public
6. Create

### 3.2 Push image to Docker Hub

```bash
# Login to Docker Hub
docker login
# Enter username and password/token

# Tag image with Docker Hub username
docker tag my-app:latest YOUR_DOCKER_USERNAME/my-app:latest

# Push to Docker Hub
docker push YOUR_DOCKER_USERNAME/my-app:latest
# Wait for upload to complete
# You should see progress bars for each layer

# Verify on Docker Hub
# Visit: https://hub.docker.com/r/YOUR_DOCKER_USERNAME/my-app
# Should show the image and its tags
```

### 3.3 Test pulling from Docker Hub

```bash
# Remove local image
docker rmi YOUR_DOCKER_USERNAME/my-app:latest

# Pull from Docker Hub
docker pull YOUR_DOCKER_USERNAME/my-app:latest
# Should download all layers

# Run the pulled image
docker run -d -p 8081:8080 --name test-from-hub YOUR_DOCKER_USERNAME/my-app:latest

# Test endpoint
curl http://localhost:8081/version

# Clean up
docker stop test-from-hub
docker rm test-from-hub
```

---

## Part 4: Test SSH Connection to VM

### 4.1 Generate SSH keys (if needed)

```bash
# Generate RSA key pair (4096 bits)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github-deploy -N ""

# Shows two files:
# ~/.ssh/github-deploy       (private key - keep secret!)
# ~/.ssh/github-deploy.pub   (public key - share with VM)

# Check permissions (important!)
ls -la ~/.ssh/github-deploy
# Should show: -rw------- (permissions 600)
```

### 4.2 Copy SSH key to VM

```bash
# Option 1: Use ssh-copy-id (automatic)
ssh-copy-id -i ~/.ssh/github-deploy.pub ubuntu@192.168.1.100
# Enter password when prompted

# Option 2: Manual copy
ssh ubuntu@192.168.1.100
# On VM:
mkdir -p ~/.ssh
# On local machine (in another terminal):
cat ~/.ssh/github-deploy.pub | ssh ubuntu@192.168.1.100 'cat >> ~/.ssh/authorized_keys'
chmod 600 ~/.ssh/authorized_keys
```

### 4.3 Test SSH connection

```bash
# Connect without password
ssh -i ~/.ssh/github-deploy ubuntu@192.168.1.100

# Verify you're on VM
whoami  # Should show: ubuntu
hostname  # Should show VM name
pwd  # Should show: /home/ubuntu

# Test Docker is available
docker --version
docker ps

# Exit
exit
```

### 4.4 Copy docker-compose.yml to VM

```bash
# From local machine
scp -i ~/.ssh/github-deploy docker-compose.yml ubuntu@192.168.1.100:/tmp/

# Verify on VM
ssh -i ~/.ssh/github-deploy ubuntu@192.168.1.100 ls -la /tmp/docker-compose.yml
```

---

## Part 5: Test Deployment on VM

### 5.1 Manual deployment test on VM

```bash
# SSH to VM
ssh -i ~/.ssh/github-deploy ubuntu@192.168.1.100

# Create deployment directory
sudo mkdir -p /app
sudo chown $USER:$USER /app

# Copy docker-compose.yml
cp /tmp/docker-compose.yml /app/

# Navigate to app directory
cd /app

# Edit docker-compose.yml to use your Docker Hub image
# Change: image: YOUR_DOCKER_USERNAME/my-app:latest
nano docker-compose.yml

# Deploy
docker compose pull
docker compose up -d

# Check status
docker compose ps
docker ps

# Test /version endpoint
curl http://localhost:8081/version
# Expected: {"version":"1.0"}

# View logs
docker logs webapp_v2
```

### 5.2 Verify MySQL connection

```bash
# SSH to VM
ssh -i ~/.ssh/github-deploy ubuntu@192.168.1.100

# Check MySQL logs
docker logs mysql-db

# Connect to MySQL (if installed locally on VM)
mysql -h localhost -u root -p
# Password: admin (from docker-compose.yml)
# Run: SELECT NOW();
# Exit: \q
```

### 5.3 Test web server responses

```bash
# From VM:
curl -v http://localhost:8081/version
curl -v http://localhost:8081/
curl -v http://localhost:8081/about

# From local machine:
curl http://192.168.1.100:8081/version
curl http://192.168.1.100:8081/

# In web browser:
# http://192.168.1.100:8081/version
# http://192.168.1.100:8081/
# http://192.168.1.100:8081/about
```

### 5.4 Cleanup test deployment

```bash
# On VM:
cd /app

# Stop and remove containers (keep data)
docker compose stop
docker compose down

# Or remove everything (delete volumes)
docker compose down -v
```

---

## Part 6: Test GitHub Actions Setup

### 6.1 Verify workflow file

```bash
# Validate YAML syntax
python -m yamllint .github/workflows/cicd.yml

# Or online: https://www.yamllint.com/
```

### 6.2 Simulate workflow locally (optional)

```bash
# Install act: https://github.com/nektos/act
# On Mac:
brew install act

# On Linux:
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | bash

# Run workflow locally
act -l  # List workflows
act push  # Simulate push event
```

### 6.3 Add secrets to GitHub

```bash
# Using GitHub CLI
gh auth login  # If not already logged in

gh secret set DOCKER_USERNAME -b "your-docker-username"
gh secret set DOCKER_PASSWORD -b "your-docker-token"
gh secret set VM_HOST -b "192.168.1.100"
gh secret set VM_USER -b "ubuntu"
gh secret set VM_SSH_KEY < ~/.ssh/github-deploy

# Verify secrets
gh secret list
```

### 6.4 Test by pushing to GitHub

```bash
# Commit changes
git add .
git commit -m "Add CI/CD pipeline"

# Push to main branch
git push origin main

# Go to GitHub Actions tab
# Watch the workflow run in real-time
# Click on the workflow run to see detailed logs
```

---

## Troubleshooting Checklist

- [ ] Flask app runs locally and /version endpoint returns `{"version":"1.0"}`
- [ ] Docker image builds successfully with no errors
- [ ] Docker image runs and port 8081 is accessible
- [ ] Image pushes to Docker Hub successfully
- [ ] Image can be pulled from Docker Hub
- [ ] SSH connection to VM works without password
- [ ] docker-compose is installed on VM
- [ ] /app directory exists and is writable on VM
- [ ] docker-compose.yml runs successfully on VM
- [ ] Containers are accessible on port 8081 from host machine
- [ ] GitHub secrets are all set correctly
- [ ] Workflow file has valid YAML syntax

---

## Common Issues & Fixes

### Issue: Port already in use
```
Error: Cannot start service on 0.0.0.0:8081
```
**Fix:**
```bash
# Find process using port
lsof -i :8081
# Kill process
kill -9 <PID>
# Or use different port in docker-compose.yml
# Change: "8081:8080" to "8082:8080"
```

### Issue: Docker image too large
```bash
# Check image size
docker images | grep my-app

# Optimize Dockerfile by:
# 1. Using smaller base image (python:3.10-slim ✓)
# 2. Combining RUN commands
# 3. Using .dockerignore properly ✓
```

### Issue: Cannot connect to MySQL
```bash
# Check if MySQL container is running
docker ps | grep mysql

# Check MySQL logs
docker logs mysql-db

# Test connection
docker exec webapp_v2 python -c "import mysql.connector; print('OK')"
```

### Issue: Permission denied on SSH
```bash
# Check key permissions
ls -la ~/.ssh/github-deploy
# Should be: -rw------- (600)

# If wrong, fix it:
chmod 600 ~/.ssh/github-deploy
chmod 700 ~/.ssh
```

---

## Performance Testing

### Check container resource usage

```bash
# Real-time stats
docker stats my-app

# Memory usage
docker exec my-app ps aux

# Network I/O
docker stats --no-stream my-app
```

### Load testing

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Simple load test (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8081/version

# More detailed test with wrk
brew install wrk  # Mac
wrk -t4 -c100 -d30s http://localhost:8081/version
```

---

## Sign-off Checklist

Before pushing to production, confirm:

- [ ] Local tests all pass
- [ ] Docker image builds locally
- [ ] Container runs and responds to requests
- [ ] Image pushes to Docker Hub
- [ ] SSH connection to VM works
- [ ] Manual deployment on VM succeeds
- [ ] /version endpoint accessible on VM
- [ ] GitHub secrets configured correctly
- [ ] Workflow file syntax is valid
- [ ] Ready to push to main branch and trigger CI/CD
