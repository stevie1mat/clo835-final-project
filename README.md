# CLO835 Final Project

## 📘 Project Title: 2-Tier Web Application Deployment on Amazon EKS

This project is the final assignment for the CLO835 course. It involves building, containerizing, and deploying a two-tier web application using Amazon EKS, with Docker, GitHub Actions, IRSA, ECR, and optional FluxCD/HPA.

---

## 👥 Team Members
| Name        | GitHub Username     | Role                        |
|-------------|---------------------|-----------------------------|
| Person A    | `@your-username`    | Flask app & Docker + S3     |
| Person B    | `@your-username`    | EKS & Kubernetes manifests  |
| Person C    | `@your-username`    | GitHub Actions & Automation |

---


## 🧱 Tasks Overview

### 🔹 Person A - App + Docker
- Enhance Flask app to:
  - Load background image from private S3
  - Use ConfigMap and Secrets
  - Log background image URL
  - Listen on port 81
- Dockerize and test app locally
- Test S3 download from within container

### 🔹 Person B - EKS + K8s
- Create EKS cluster with 2 worker nodes
- Create namespace `final`
- Write manifests for:
  - ConfigMap (image URL)
  - Secret (MySQL creds)
  - PVC (2Gi gp2)
  - ServiceAccount + IRSA for S3
  - Role/Binding for namespace creation
  - MySQL deployment + service
  - Flask deployment + service

### 🔹 Person C - CI/CD + Extras
- Set up GitHub Actions:
  - On `main` branch push
  - Build Docker image
  - Push to ECR
- Protect `main` branch
- BONUS: Add HPA, metrics-server, and FluxCD

---

