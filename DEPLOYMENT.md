# LiveNewsAI - Deployment Guide

## Overview

This guide covers deploying LiveNewsAI in various environments.

## Quick Start

### Option 1: Local Development (Fastest)

```bash
# 1. Set up environment
export NEWS_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# 2. Run quick start
bash quickstart.sh
```

### Option 2: Docker (Recommended for Production)

```bash
# 1. Set environment variables
export NEWS_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# 2. Start with Docker Compose
bash docker-quickstart.sh

# Or manually:
docker-compose up --build
```

## Detailed Deployment

### Prerequisites

- Python 3.10+ (for local)
- Docker & Docker Compose (for containerized)
- NewsAPI API key (free at newsapi.org)
- OpenAI API key (get at platform.openai.com)
- 2GB RAM minimum
- 100MB disk space

### Local Deployment

#### Step 1: Clone Repository

```bash
git clone <repository-url>
cd LiveNews-AI-A-Real-Time-Thinking-RAG-System
```

#### Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Step 3: Install Dependencies

```bash
cd livenewsai
pip install -r requirements.txt
```

#### Step 4: Configure Environment

```bash
# Create .env file
cp ../.env.example .env

# Edit .env with your API keys
nano .env

# Or set environment variables
export NEWS_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

#### Step 5: Run Application

```bash
python app.py
```

Server will be available at `http://localhost:8000`

### Docker Deployment

#### Using Docker Compose (Recommended)

```bash
# Set environment variables
export NEWS_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Start services
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down
```

#### Manual Docker Build

```bash
# Build image
docker build -t livenewsai:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e NEWS_API_KEY="your-key" \
  -e OPENAI_API_KEY="your-key" \
  --name livenewsai \
  livenewsai:latest

# View logs
docker logs -f livenewsai

# Stop container
docker stop livenewsai
```

### Cloud Deployment

#### AWS EC2

```bash
# 1. Launch t3.small EC2 instance with Ubuntu 24.04

# 2. SSH into instance
ssh -i key.pem ubuntu@your-instance-ip

# 3. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 4. Clone repository
git clone <repository-url>
cd LiveNews-AI-A-Real-Time-Thinking-RAG-System

# 5. Set environment variables
export NEWS_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# 6. Run with Docker Compose
docker-compose up -d

# 7. Configure security group
# Allow inbound on port 8000 from your IP
```

#### Google Cloud Run

```bash
# 1. Install gcloud CLI
curl https://sdk.cloud.google.com | bash

# 2. Authenticate
gcloud auth login

# 3. Create project
gcloud projects create livenewsai

# 4. Set project
gcloud config set project livenewsai

# 5. Build and push to Container Registry
gcloud builds submit --tag gcr.io/livenewsai/app

# 6. Deploy to Cloud Run
gcloud run deploy livenewsai \
  --image gcr.io/livenewsai/app \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars NEWS_API_KEY=your-key,OPENAI_API_KEY=your-key \
  --memory 2G \
  --timeout 3600
```

#### Heroku

```bash
# 1. Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# 2. Login
heroku login

# 3. Create app
heroku create livenewsai

# 4. Set environment variables
heroku config:set NEWS_API_KEY=your-key
heroku config:set OPENAI_API_KEY=your-key

# 5. Deploy
git push heroku main

# 6. View logs
heroku logs --tail
```

### Kubernetes Deployment

#### Create Deployment

```yaml
# livenewsai-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: livenewsai
spec:
  replicas: 2
  selector:
    matchLabels:
      app: livenewsai
  template:
    metadata:
      labels:
        app: livenewsai
    spec:
      containers:
      - name: app
        image: livenewsai:latest
        ports:
        - containerPort: 8000
        env:
        - name: NEWS_API_KEY
          valueFrom:
            secretKeyRef:
              name: livenewsai-secrets
              key: news-api-key
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: livenewsai-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: livenewsai-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: livenewsai
```

Deploy:
```bash
# Create secrets
kubectl create secret generic livenewsai-secrets \
  --from-literal=news-api-key=your-key \
  --from-literal=openai-api-key=your-key

# Deploy
kubectl apply -f livenewsai-deployment.yaml

# Check status
kubectl get pods
kubectl get services

# View logs
kubectl logs -f deployment/livenewsai
```

## Post-Deployment

### Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Check API documentation
open http://localhost:8000/docs

# Test ask endpoint
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the latest news?"}'
```

### Monitor Application

```bash
# View logs
docker-compose logs -f app

# Check container stats
docker stats livenewsai

# View system metrics
docker-compose exec app bash
  ps aux
  df -h
```

### Scaling Considerations

- **Single instance**: Suitable for up to 100 requests/minute
- **Multiple instances**: Use load balancer (AWS ALB, GCP Load Balancer)
- **Database**: For persistent storage, add PostgreSQL for document storage
- **Caching**: Redis for query caching
- **Message Queue**: RabbitMQ for async processing

### Security Best Practices

1. **API Keys**: Use secrets management (AWS Secrets Manager, K8s Secrets)
2. **Environment Variables**: Never commit `.env` files
3. **HTTPS**: Use TLS/SSL in production (nginx, cloudflare)
4. **Rate Limiting**: Implement API rate limiting
5. **Authentication**: Add OAuth2/JWT if exposing publicly
6. **Monitoring**: Set up alerts for errors and downtime

### Performance Tuning

```bash
# Increase polling interval if rate limited
export NEWS_POLLING_INTERVAL=120

# Reduce batch size for slower networks
export NEWS_BATCH_SIZE=10

# Use faster embedding model
export EMBEDDING_MODEL=text-embedding-3-small

# Reduce context for faster answers
export MAX_CONTEXT_LENGTH=2000
```

### Troubleshooting

#### Container won't start
```bash
# Check logs
docker-compose logs app

# Common issues:
# - API keys not set
# - Port 8000 already in use
# - Insufficient memory
```

#### Vector index not growing
```bash
# Check if articles are being fetched
curl http://localhost:8000/stats

# Verify NewsAPI connection
# - Check API key validity
# - Check rate limits
```

#### Slow queries
```bash
# Reduce TOP_K_RESULTS
export TOP_K_RESULTS=3

# Increase embedding cache
# Edit pathway_pipeline.py

# Use simpler embedding model
export EMBEDDING_MODEL=text-embedding-3-small
```

## Maintenance

### Regular Tasks

- **Daily**: Monitor error logs
- **Weekly**: Check API rate limits and costs
- **Monthly**: Update dependencies
- **Quarterly**: Capacity planning

### Updating

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Rebuild Docker image
docker-compose build --no-cache

# Restart services
docker-compose restart
```

### Backup

```bash
# Backup vector index
docker cp livenewsai:/tmp/livenewsai ./backup/

# Version control
git commit -am "Backup before update"
```

## Cost Estimation

### API Costs (Monthly)

- **NewsAPI**: $0 (free) or $50+ (professional)
- **OpenAI Embeddings**: $0.02 per 1M tokens (~$2-5/month)
- **OpenAI GPT-4**: $0.03 per 1K tokens input (~$10-50/month)
- **Total**: ~$12-55/month

### Infrastructure Costs

- **Local**: Free (use existing machine)
- **Cloud VPS**: $5-20/month (AWS t3.small, GCP e2-small)
- **Cloud Run**: ~$0.25-2/month (minimal usage)
- **Kubernetes**: $20+ (managed cluster)

## Support

For deployment issues:
1. Check logs: `docker-compose logs app`
2. Verify API keys
3. Check disk space: `df -h`
4. Check memory: `free -h`
5. Check internet: `curl https://newsapi.org/v2/everything`

## Additional Resources

- [Pathway Documentation](https://pathway.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [OpenAI API Docs](https://platform.openai.com/docs)
- [NewsAPI Docs](https://newsapi.org/docs)
