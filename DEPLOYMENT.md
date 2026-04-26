# Yarra Production Deployment Strategy

This document outlines the strategy for deploying Yarra as a commercial-grade website capable of handling **1,000 concurrent users** with sub-2-second response times and 99.9% uptime.

## 1. Infrastructure Architecture

### High-Availability (HA) Stack
- **Load Balancer**: AWS Application Load Balancer (ALB) or Nginx Plus for SSL termination and traffic distribution.
- **Application Tier**: Dockerized Django instances running on **AWS ECS (Fargate)** or **Kubernetes (EKS)**.
- **Auto-Scaling**: 
  - Scale out when CPU > 60% or Memory > 70%.
  - Minimum 3 instances across different Availability Zones (Multi-AZ).
- **CDN**: **Amazon CloudFront** for global delivery of static and media files with edge caching.

## 2. Database Optimization

- **Database**: **Amazon RDS for PostgreSQL** (Multi-AZ).
- **Connection Pooling**: **PgBouncer** to manage high concurrency connections.
- **Optimization**:
  - `conn_max_age` set to 600 in `settings.py`.
  - Proper indexing on `school`, `role`, `is_active`, and `category` fields.
  - Read Replicas for scaling read-heavy operations (e.g., School Network directory).

## 3. Performance Tuning

- **Caching**: **Redis (Amazon ElastiCache)**.
  - Session storage moved to Redis for speed and persistence across app restarts.
  - Query caching for expensive calculations (e.g., analytics).
- **Static Files**: **WhiteNoise** with Brotli compression for optimized asset delivery.
- **Asset Optimization**: Gulp/Webpack for minifying JS/CSS and image optimization (WebP).

## 4. Security Implementation

- **SSL/TLS**: AWS Certificate Manager (ACM) for automatic renewal.
- **WAF**: **AWS WAF** to block common web exploits (SQLi, XSS) and DDoS protection via **AWS Shield**.
- **Secure Headers**: Implemented via `django-csp` and Nginx configuration.
- **Environment Secrets**: **AWS Secrets Manager** for DB credentials and API keys.

## 5. Monitoring & Alerting

- **Application Monitoring**: **Sentry** for real-time error tracking and performance profiling.
- **Infrastructure Metrics**: **Prometheus & Grafana** for monitoring CPU, RAM, and request throughput.
- **Health Checks**: `/health/` endpoint for ALB to verify instance readiness.
- **Alerting**: PagerDuty or Slack integration for critical system failures.

## 6. Backup & Disaster Recovery

- **DB Backups**: Automated daily snapshots with 30-day retention in RDS.
- **Point-in-Time Recovery**: Enabled for up to 5 minutes of data loss.
- **Media Backups**: S3 Versioning and Cross-Region Replication (CRR).
- **Recovery SLA**: 99.9% uptime with a maximum RTO (Recovery Time Objective) of 4 hours.

## 7. CI/CD Pipeline

- **Platform**: **GitHub Actions**.
- **Process**:
  1. **Build**: Linting (flake8) and Unit Tests.
  2. **Staging**: Deploy to a mirror environment for QA.
  3. **Production**: Blue-Green or Rolling deployment for zero downtime.
  4. **Database**: Automated migrations during the build phase.

## 8. Load Testing Strategy

- **Tool**: **k6** or **Locust**.
- **Scenario**: 
  - Simulate 1,000 virtual users performing login, browsing school network, and registering for events.
  - Goal: Maintain < 2s response time at peak load.
- **Execution**: Run weekly in the staging environment before major releases.

## 9. Cost Optimization

- **Reserved Instances**: For base load app servers and RDS.
- **Spot Instances**: For non-critical background tasks.
- **S3 Lifecycle**: Move old logs and backups to Glacier after 90 days.

---

## Deployment Quickstart

1. **Build Image**: `docker build -t yarra-app .`
2. **Setup Env**: Copy `.env.example` to `.env` and fill in secrets.
3. **Run Stack**: `docker-compose up -d`
4. **Initialize**: `docker-compose exec web python manage.py migrate`
