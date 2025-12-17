# Git Setup Guide

## Initial Setup

1. Initialize Git repository:
```bash
cd C:\FreshShare-Platform
git init
```

2. Add all files:
```bash
git add .
```

3. Create initial commit:
```bash
git commit -m "Initial commit: Fresh-Share Platform with Observer pattern implementation"
```

4. Create GitHub repository and push:
```bash
git remote add origin <your-github-repo-url>
git branch -M main
git push -u origin main
```

## Suggested Commit History

You can create feature branches to demonstrate proper Git workflow:

```bash
# Feature 1: User Authentication
git checkout -b feature/authentication
git add src/routes/auth_routes.py src/models/__init__.py
git commit -m "feat: Implement user authentication with JWT"
git push origin feature/authentication

# Feature 2: Observer Pattern
git checkout main
git checkout -b feature/observer-pattern
git add src/observers/
git commit -m "feat: Implement Observer pattern for notifications"
git push origin feature/observer-pattern

# Feature 3: Listing Service
git checkout main
git checkout -b feature/listing-service
git add src/services/listing_service.py src/routes/listing_routes.py
git commit -m "feat: Add listing service with geospatial search"
git push origin feature/listing-service

# Feature 4: Testing
git checkout main
git checkout -b feature/testing
git add tests/
git commit -m "test: Add comprehensive test suite"
git push origin feature/testing

# Feature 5: Docker
git checkout main
git checkout -b feature/docker
git add Dockerfile docker-compose.yml
git commit -m "chore: Add Docker configuration for easy deployment"
git push origin feature/docker

# Merge all to main
git checkout main
git merge feature/authentication
git merge feature/observer-pattern
git merge feature/listing-service
git merge feature/testing
git merge feature/docker
```

## Git Configuration for VS Code

1. Open VS Code terminal
2. Configure Git:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

3. VS Code will show Git changes in:
   - Source Control panel (Ctrl+Shift+G)
   - File explorer (colored indicators)
   - Status bar (bottom)

## .gitignore

Already created to exclude:
- Python cache files
- Virtual environment
- Environment variables (.env)
- IDE settings
- Logs and test coverage
