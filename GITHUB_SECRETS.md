# GitHub CI/CD Pipeline - Secrets Configuration Guide

## Overview
This guide documents all GitHub Secrets required for the CI/CD pipeline and where they are used in the workflow.

---

## Required GitHub Secrets

### 1. **DOCKER_USERNAME**
- **Description**: Your Docker Hub username
- **Value**: Your personal Docker Hub account username (e.g., `johndoe`)
- **Where it's used**:
  - `.github/workflows/cicd.yml` - Line: Docker login authentication
  - `.github/workflows/cicd.yml` - Line: Image naming convention `DOCKER_USERNAME/my-app`
  - `.github/workflows/cicd.yml` - Line: Pushed to Docker Hub tags

**Add this secret:**
```
Settings > Secrets and variables > Actions > New repository secret
Name: DOCKER_USERNAME
Value: [your-docker-username]
```

---

### 2. **DOCKER_PASSWORD**
- **Description**: Your Docker Hub Personal Access Token (recommended) or password
- **Value**: Generated from Docker Hub account
- **Where it's used**:
  - `.github/workflows/cicd.yml` - Step: "Log in to Docker Hub"
  - Authentication for pushing images to Docker Hub registry

**⚠️ Security Best Practice:**
Instead of using your Docker Hub password, create a Personal Access Token:
1. Go to Docker Hub > Account Settings > Security
2. Click "New Access Token"
3. Name it (e.g., `github-actions`)
4. Select read/write permissions
5. Copy the token value

**Add this secret:**
```
Settings > Secrets and variables > Actions > New repository secret
Name: DOCKER_PASSWORD
Value: [your-docker-hub-token-or-password]
```

---

### 3. **VM_HOST**
- **Description**: IP address or hostname of your Ubuntu VM
- **Value**: Public IP or DNS name of the deployment VM
- **Examples**: `192.168.1.100` or `prod-server.example.com`
- **Where it's used**:
  - `.github/workflows/cicd.yml` - Step: "Deploy to VM via SSH"
  - `.github/workflows/cicd.yml` - Step: "Verify deployment health"
  - Used as the target server for SSH deployment

**Add this secret:**
```
Settings > Secrets and variables > Actions > New repository secret
Name: VM_HOST
Value: [your-vm-ip-or-hostname]
```

---

### 4. **VM_USER**
- **Description**: SSH username for the Ubuntu VM
- **Value**: User account name on the VM (typically `ubuntu` or `ec2-user` for cloud VMs)
- **Where it's used**:
  - `.github/workflows/cicd.yml` - Step: "Deploy to VM via SSH"
  - `.github/workflows/cicd.yml` - Step: "Verify deployment health"
  - SSH authentication username

**Add this secret:**
```
Settings > Secrets and variables > Actions > New repository secret
Name: VM_USER
Value: [your-vm-username]
```

---

### 5. **VM_SSH_KEY**
- **Description**: Private SSH key for authentication to the VM
- **Value**: The full private key content (including BEGIN/END lines)
- **Where it's used**:
  - `.github/workflows/cicd.yml` - Step: "Deploy to VM via SSH"
  - `.github/workflows/cicd.yml` - Step: "Verify deployment health"
  - Key-based SSH authentication (more secure than passwords)

**⚠️ Security Best Practice:**
Use SSH key-based authentication instead of passwords.

**Generate SSH keys (if you don't have them):**
```bash
# On your local machine
ssh-keygen -t rsa -b 4096 -f ~/.ssh/github-deploy -N ""

# Copy public key to VM
ssh-copy-id -i ~/.ssh/github-deploy.pub ubuntu@your-vm-host
```

**Add this secret:**
```
Settings > Secrets and variables > Actions > New repository secret
Name: VM_SSH_KEY
Value: [paste-entire-private-key-content]
```

The private key should look like:
```
-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEA2x...
...
-----END RSA PRIVATE KEY-----
```

---

## How to Set Up GitHub Secrets

### Method 1: GitHub Web Interface
1. Go to your GitHub repository
2. Click **Settings**
3. Select **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Enter Name and Value
6. Click **Add secret**

### Method 2: GitHub CLI
```bash
# Prerequisites: Install GitHub CLI (https://cli.github.com/)
gh auth login

# Add secrets
gh secret set DOCKER_USERNAME -b "your-docker-username"
gh secret set DOCKER_PASSWORD -b "your-docker-token"
gh secret set VM_HOST -b "192.168.1.100"
gh secret set VM_USER -b "ubuntu"
gh secret set VM_SSH_KEY < ~/.ssh/github-deploy
```

---

## Workflow Stages & Secret Usage

### Stage 1: Build & Test
- **No secrets used** - Runs linting and tests locally

### Stage 2: Docker Build & Push
- **DOCKER_USERNAME** - Used in image naming (`DOCKER_USERNAME/my-app:tag`)
- **DOCKER_PASSWORD** - Used to authenticate with Docker Hub
- **Workflow step**: "Log in to Docker Hub"

### Stage 3: Deploy to VM
- **VM_HOST** - SSH target server address
- **VM_USER** - SSH authentication username
- **VM_SSH_KEY** - SSH authentication private key
- **Workflow steps**: 
  - "Deploy to VM via SSH"
  - "Verify deployment health"

---

## Verification Checklist

- [ ] All 5 secrets are created in GitHub
- [ ] Secrets are accessible in the Actions tab under "Run workflow"
- [ ] SSH key is properly formatted (includes BEGIN/END lines)
- [ ] Docker Hub credentials are valid and have push permissions
- [ ] VM SSH key matches the public key on the VM
- [ ] VM is accessible from GitHub Actions (port 22 open)
- [ ] Application directory `/app` exists on the VM

---

## Troubleshooting

### "Docker login failed"
- Verify `DOCKER_USERNAME` and `DOCKER_PASSWORD` are correct
- Check if Docker Hub account has 2FA enabled (use token instead of password)

### "SSH connection refused"
- Verify `VM_HOST` is correct and accessible
- Check if port 22 is open on the VM firewall
- Ensure `VM_USER` exists on the VM

### "Permission denied (publickey)"
- Verify `VM_SSH_KEY` is the correct private key
- Ensure the public key is in `~/.ssh/authorized_keys` on the VM
- Check SSH key permissions: `chmod 600 ~/.ssh/authorized_keys`

### "docker compose command not found"
- SSH into VM and install Docker Compose: `sudo apt-get install docker-compose`
- Or use `docker-compose` (with hyphen) if on older Docker version

---

## Local Testing (Before Deployment)

### Test Docker Build Locally
```bash
# Build the Docker image
docker build -t my-app:latest .

# Run the container
docker run -d -p 8081:8080 --name test-app my-app:latest

# Test the /version endpoint
curl http://localhost:8081/version
# Expected output: {"version": "1.0"}

# View logs
docker logs test-app

# Clean up
docker stop test-app
docker rm test-app
```

### Test SSH Connection
```bash
# Test SSH access to VM
ssh -i ~/.ssh/github-deploy ubuntu@your-vm-host

# Verify docker-compose is installed
docker-compose --version

# Test docker commands
docker ps
```

---

## Next Steps

1. **Create Docker Hub Repository**
   - Go to https://hub.docker.com/
   - Click "Create Repository"
   - Name: `my-app`
   - Visibility: Public
   - Click Create

2. **Set Up GitHub Secrets** (as outlined above)

3. **Prepare VM**
   - Install Docker and Docker Compose
   - Create `/app` directory
   - Copy `docker-compose.yml` to `/app`
   - Test local deployment manually

4. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Add CI/CD pipeline with GitHub Actions"
   git push origin main
   ```

5. **Monitor Workflow**
   - Go to GitHub repo → Actions tab
   - Watch the workflow run in real-time
   - Check logs for any errors

6. **Verify Deployment**
   - SSH to VM and check: `docker ps`
   - Test /version endpoint: `curl http://localhost:8081/version`

---

## Security Notes

1. **Never commit secrets** to the repository
2. **Rotate credentials** regularly
3. **Use token-based auth** instead of passwords where possible
4. **Limit SSH key permissions** - create separate keys for each purpose
5. **Monitor workflow runs** for failed deployments
6. **Enable branch protection** to require status checks before merging

---

