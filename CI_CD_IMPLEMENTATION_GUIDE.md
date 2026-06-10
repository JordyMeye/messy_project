# CI/CD Pipeline - Step-by-Step Implementation Guide

This guide walks through all 6 steps of the class exercise to set up a complete CI/CD pipeline.

---

## Step 1: Dockerfile and /version Endpoint ✓

### What was done:
- ✓ Updated `Dockerfile` with proper Flask app setup
- ✓ Added `.dockerignore` to exclude unnecessary files
- ✓ Added `/version` endpoint in `FlaskWebProject1/views.py`
- ✓ Updated `requirements.txt` with all dependencies

### Files modified:
```
Dockerfile              - Multi-stage build with health checks
.dockerignore           - Exclude __pycache__, .git, tests, etc.
FlaskWebProject1/views.py - Added @app.route('/version')
requirements.txt        - Added Flask, mysql-connector-python, etc.
```

### Build Docker image locally:
```bash
# From project root directory
docker build -t my-app:latest .

# Verify build succeeded
docker images | grep my-app
```

---

## Step 2: Docker Hub Repository Setup

### Create Docker Hub Repository:
1. Go to **https://hub.docker.com/**
2. Sign in or create account
3. Click **Create Repository**
4. Fill in:
   - Repository name: `my-app`
   - Description: "Flask application with Docker CI/CD"
   - Visibility: **Public** (for exercise; use Private in production)
5. Click **Create**

### Push image manually (for verification):
```bash
# Login to Docker Hub
docker login
# Enter your username and password/token when prompted

# Tag the image
docker tag my-app:latest YOUR_DOCKER_USERNAME/my-app:latest

# Push to Docker Hub
docker push YOUR_DOCKER_USERNAME/my-app:latest

# Verify online
# Go to https://hub.docker.com/r/YOUR_DOCKER_USERNAME/my-app
# You should see the image listed
```

### Note the push output:
```
The push refers to repository [docker.io/your-username/my-app]
latest: digest: sha256:abc123...
```

---

## Step 3: Set Up GitHub Secrets

### Required Secrets:

| Secret Name | Value | Example |
|------------|-------|---------|
| `DOCKER_USERNAME` | Your Docker Hub username | `johndoe` |
| `DOCKER_PASSWORD` | Docker Hub token (not password) | `dckr_pat_...` |
| `VM_HOST` | VM IP or hostname | `192.168.1.100` |
| `VM_USER` | SSH username | `ubuntu` |
| `VM_SSH_KEY` | Private SSH key (full content) | `-----BEGIN RSA PRIVATE KEY-----...` |

### Add secrets to GitHub:

**In GitHub:**
1. Go to repository → **Settings**
2. Click **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret from the table above

**Using GitHub CLI:**
```bash
gh secret set DOCKER_USERNAME -b "your-docker-username"
gh secret set DOCKER_PASSWORD -b "your-docker-token"
gh secret set VM_HOST -b "192.168.1.100"
gh secret set VM_USER -b "ubuntu"
gh secret set VM_SSH_KEY < /path/to/private/key
```

### Important Notes:
- **Do NOT use password** - Create Docker Hub Personal Access Token:
  - Docker Hub → Account Settings → Security → New Access Token
  - Give it `read` and `write` permissions
  - Use the token value as `DOCKER_PASSWORD`
  
- **For SSH key**, generate if you don't have one:
  ```bash
  ssh-keygen -t rsa -b 4096 -f ~/.ssh/github-deploy -N ""
  ssh-copy-id -i ~/.ssh/github-deploy.pub ubuntu@192.168.1.100
  ```

---

## Step 4: GitHub Actions Workflow

### Workflow file: `.github/workflows/cicd.yml` ✓

The workflow has 3 stages:

**Stage 1: Build & Test**
- Checkout code
- Set up Python environment
- Install dependencies
- Run Flake8 linting
- Run pytest tests

**Stage 2: Docker Build & Push**
- Set up Docker Buildx (for cross-platform builds)
- Login to Docker Hub using secrets
- Build Docker image
- Tag with commit SHA and `latest`
- Push both tags to Docker Hub

**Stage 3: Deploy to VM**
- SSH to VM using secrets
- Pull new Docker image
- Run `docker compose pull` and `docker compose up -d`
- Verify deployment with health checks

---

## Step 5: SSH Deployment Configuration

### On your Ubuntu VM, prepare for deployment:

```bash
# SSH into your VM
ssh ubuntu@192.168.1.100

# Create deployment directory
sudo mkdir -p /app
sudo chown $USER:$USER /app

# Copy docker-compose.yml to VM
# From your local machine:
scp docker-compose.yml ubuntu@192.168.1.100:/app/

# On the VM, verify Docker is installed
docker --version
docker-compose --version

# If not installed, install Docker:
sudo apt-get update
sudo apt-get install -y docker.io docker-compose
sudo usermod -aG docker $USER

# Log out and back in for group changes to take effect
```

### Test manual deployment on VM:

```bash
# On VM, from /app directory
cd /app

# Create a test docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: '3.8'
services:
  mysql-db:
    image: mysql:latest
    container_name: mysql-db
    environment:
      MYSQL_ROOT_PASSWORD: admin
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - my-custom-bridge

  webapp_v2:
    image: YOUR_DOCKER_USERNAME/my-app:latest
    container_name: webapp_v2
    ports:
      - "8081:8080"
    depends_on:
      - mysql-db
    networks:
      - my-custom-bridge

volumes:
  mysql_data:
    driver: local

networks:
  my-custom-bridge:
    driver: bridge
EOF

# Pull and run containers
docker compose pull
docker compose up -d

# Verify containers are running
docker ps

# Check logs
docker logs webapp_v2
docker logs mysql-db
```

---

## Step 6: Testing & Verification

### Test the /version endpoint:

**Locally (before pushing):**
```bash
# Build and run locally
docker build -t my-app:latest .
docker run -d -p 8081:8080 --name test-app my-app:latest

# Test endpoint
curl http://localhost:8081/version
# Expected: {"version":"1.0"}

# Clean up
docker stop test-app
docker rm test-app
```

**On VM (after deployment):**
```bash
# SSH to VM
ssh ubuntu@192.168.1.100

# Test endpoint
curl http://localhost:8081/version
# Expected: {"version":"1.0"}

# Test from another machine (replace VM_IP):
curl http://192.168.1.100:8081/version
```

**In browser:**
- Navigate to: `http://192.168.1.100:8081/version`
- See JSON response: `{"version":"1.0"}`

### Screenshots to capture:

1. **Docker Build Success**
   ```bash
   docker build -t my-app .
   # Screenshot: Final "Successfully tagged my-app:latest" message
   ```

2. **Docker Hub Repository**
   - https://hub.docker.com/r/YOUR_USERNAME/my-app
   - Screenshot: Image tags and digest listed

3. **GitHub Actions Workflow Run**
   - Repository → Actions tab → Click latest workflow run
   - Screenshot: All three stages (Build, Docker Build & Push, Deploy) showing green checkmarks

4. **Running Containers on VM**
   ```bash
   docker ps
   # Screenshot: webapp_v2 and mysql-db containers running
   ```

5. **/version Endpoint Response**
   - Browser: `http://192.168.1.100:8081/version`
   - Screenshot: JSON response `{"version":"1.0"}`
   - Or terminal: `curl http://192.168.1.100:8081/version | python -m json.tool`

6. **Workflow Logs**
   - GitHub Actions → cicd.yml run → deploy job → "Deploy to VM via SSH" step
   - Screenshot: Shows docker compose commands executing successfully

---

## Troubleshooting

### Issue: Docker login failed
```
Error: Error response from daemon: unauthorized: authentication required
```
**Solution:**
- Verify DOCKER_USERNAME is correct
- Check DOCKER_PASSWORD is a valid Docker Hub token (not password)
- Create new token: Docker Hub → Account Settings → Security

### Issue: SSH connection refused
```
Error: connect to host 192.168.1.100 port 22: Connection refused
```
**Solution:**
- Verify VM_HOST is correct
- Check SSH port 22 is open: `sudo ufw allow 22`
- Test local SSH: `ssh -i ~/.ssh/github-deploy ubuntu@192.168.1.100`

### Issue: docker-compose not found
```
Error: /bin/sh: docker-compose: not found
```
**Solution:**
- SSH to VM and install: `sudo apt-get install docker-compose`
- Or use: `docker compose` (Docker 20.10+)

### Issue: Permission denied on /app
```
Error: mkdir: cannot create directory '/app': Permission denied
```
**Solution:**
```bash
# On VM
sudo mkdir -p /app
sudo chown $USER:$USER /app
ls -la / | grep app  # Should show your username as owner
```

### Issue: Container exits immediately
```bash
# On VM
docker logs webapp_v2
# Check if Flask app is running correctly
```
**Solution:**
- Ensure requirements.txt installs Flask
- Check views.py has @app.route decorators
- Verify runserver.py binds to 0.0.0.0:8080

---

## Full Deployment Flow Summary

```
1. Developer pushes code to main branch
   ↓
2. GitHub Actions triggered automatically
   ↓
3. Stage 1: Build & Test (runs locally)
   - Python linting (Flake8)
   - Run pytest
   ↓
4. Stage 2: Docker Build & Push (if tests pass)
   - Builds Docker image
   - Tags with commit SHA
   - Pushes to Docker Hub
   ↓
5. Stage 3: Deploy (if push succeeds)
   - SSH to VM
   - Pulls new image
   - Runs docker compose up -d
   ↓
6. Production Live
   - Container running on port 8081
   - /version endpoint responding
   - MySQL database available
```

---

## Complete Command Reference

### Local development:
```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask app locally
python runserver.py

# Build Docker image
docker build -t my-app:latest .

# Run Docker container
docker run -d -p 8081:8080 my-app:latest

# View logs
docker logs -f container_name

# Push to Docker Hub
docker push username/my-app:latest
```

### VM operations:
```bash
# SSH to VM
ssh -i ~/.ssh/github-deploy ubuntu@192.168.1.100

# Deploy containers
cd /app
docker compose pull
docker compose up -d

# Monitor
docker ps
docker logs -f webapp_v2
curl http://localhost:8081/version
```

### GitHub secrets (CLI):
```bash
gh secret set DOCKER_USERNAME -b "username"
gh secret set DOCKER_PASSWORD -b "token"
gh secret set VM_HOST -b "192.168.1.100"
gh secret set VM_USER -b "ubuntu"
gh secret set VM_SSH_KEY < ~/.ssh/github-deploy
```

---

## Next Exercise Ideas

1. **Add database migrations** - Auto-migrate MySQL schema on deployment
2. **Implement health checks** - Add `/health` endpoint for monitoring
3. **Blue-green deployment** - Run two versions, switch traffic gradually
4. **Rollback mechanism** - Quickly revert to previous version
5. **Notification alerts** - Slack/email on deployment success/failure
6. **Load balancing** - Deploy to multiple VMs with nginx

