name: CI-CD Pipeline

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [main]

permissions:
  contents: write
  pull-requests: write

jobs:
  job1_tests_qualite:
    name: Job 1 - Tests & Qualité
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Lint with flake8
        run: flake8 app/ --count --max-line-length=100 --statistics

      - name: Run tests
        run: pytest tests/ -v

  job2_build_securite:
    name: Job 2 - Build & Sécurité
    runs-on: ubuntu-latest
    needs: [job1_tests_qualite]
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Build Docker image
        run: docker build -t inventory-api:test .

      - name: Check image size (< 100MB)
        run: |
          SIZE=$(docker image inspect inventory-api:test --format='{{.Size}}')
          echo "Image size (bytes): $SIZE"
          MAX=$((100*1024*1024))
          if [ "$SIZE" -ge "$MAX" ]; then
            echo "Image too large (>100MB)"; exit 1
          fi

      - name: Trivy scan (non-blocking)
        continue-on-error: true
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: "inventory-api:test"
          format: "table"
          severity: "CRITICAL,HIGH"

  job3_auto_pr:
    name: Job 3 - Pull Request Auto
    runs-on: ubuntu-latest
    needs: [job1_tests_qualite, job2_build_securite]
    if: github.ref == 'refs/heads/develop'
    steps:
      - name: Create PR develop -> main
        uses: repo-sync/pull-request@v2
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          source_branch: "develop"
          destination_branch: "main"
          pr_title: "Release: Develop to Main"

  job4_deploy_prod:
    name: Job 4 - Déploiement Production
    runs-on: ubuntu-latest
    needs: [job1_tests_qualite, job2_build_securite]
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy message
        run: |
          echo "DEPLOYMENT: PRODUCTION"
          echo "SHA: $GITHUB_SHA"
          echo "DATE: $(date -u)"
