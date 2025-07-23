<<<<<<< HEAD
# Install the required MySQL package

sudo apt-get update -y
sudo apt-get install mysql-client -y

# Running application locally
pip3 install -r requirements.txt
sudo python3 app.py
# Building and running 2 tier web application locally
### Building mysql docker image 
```docker build -t my_db -f Dockerfile_mysql . ```

### Building application docker image 
```docker build -t my_app -f Dockerfile . ```

### Running mysql
```docker run -d -e MYSQL_ROOT_PASSWORD=pw  my_db```


### Get the IP of the database and export it as DBHOST variable
```docker inspect <container_id>```


### Example when running DB runs as a docker container and app is running locally
```
export DBHOST=127.0.0.1
export DBPORT=3307
```
### Example when running DB runs as a docker container and app is running locally
```
export DBHOST=172.17.0.2
export DBPORT=3306
```
```
export DBUSER=root
export DATABASE=employees
export DBPWD=pw
export APP_COLOR=blue
```
### Run the application, make sure it is visible in the browser
```docker run -p 8080:8080  -e DBHOST=$DBHOST -e DBPORT=$DBPORT -e  DBUSER=$DBUSER -e DBPWD=$DBPWD  my_app```
=======
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

>>>>>>> 6624c36a641e72f9456d2f6baa6277341b2e42c6
