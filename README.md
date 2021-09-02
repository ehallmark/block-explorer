# Blockchain Explorer

This repository contains code for provisioning an application in Google Cloud that contains a dashboard for viewing transactions on Ethereum, Polygon, and Binance Smart Chain for a given account address.

The dashboard is currently hosted here: https://bsc-explorer.evanhallmark.com

## Technology Overview

### Infrastructure

+ Kubernetes (GKE)
  
    + Service Namespace - contains a K8s Deployment resource and Service resource for hosting the Python Flask webserver
    
    + ETL Namespace - contains a K8s CronJob that runs the ETL process on an hourly cadence

    + Load Balancer for exposing public endpoint
    
+ SQL (Postgres) for storing structured data

### Backend

+ Python
+ Flask
+ Pandas

### Frontend

+ Javascript/CSS/HTML: [block_explorer/service/templates/](block_explorer/service/templates/)
+ [Chart.js](https://www.chartjs.org/docs/latest/) for visualizations
+ [Bootstrap](https://getbootstrap.com/docs/3.4/css/) for styling

## Deployment

Prerequisites:

+ Terraform
+ Docker
+ Gcloud

### Setup secrets

Create a file in [block_explorer/](block_explorer/) called `.env`. This file will contain any sensitive data and is automatically ignored from version control. Values in this file are picked up by the Terraform deployment script, as well as secrets when running the Python code locally. Refer to [block_explorer/.env.sample](block_explorer/.env.sample) for an example.

### Build and push docker image

Set environment variables in [scripts/build_push_docker.sh](scripts/build_push_docker.sh)

Then run:

```bash
./scripts/build_push_docker.sh
```

### Deploy Terraform Stack

Set environment variables in [scripts/deploy_stack.sh](scripts/deploy_stack.sh)

Then run:

```bash
./scripts/deploy_stack.sh
```

A Terraform confirmation will be displayed. Assuming everything looks reasonable, type `yes` into the input prompt. Terraform will then start provisioning the infrastructure.

### Setup DNS (Optional)

Terraform will output the IP address of the exposed Kubernetes endpoint. If desired, point a DNS A-record to this IP address.

## Local Development

Prerequisites:

+ Python (3.8)

### Setup local environment

```bash
# Create a fresh Python 3.8 environment
conda create -n block_explorer -y python=3.8
conda activate block_explorer

# Install requirements
pip install -r requirements.txt

# Add source code to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:`pwd`/block_explorer"

# Run ETL locally
python -m etl

# Start Flask server locally
python -m service.server
```