# Prerequisites

This document outlines the requirements and setup process for the AI-Powered Search and Chat workshop.

## Required Infrastructure

### Running Elasticsearch and Kibana Deployment

To use the scripts and examples in this workshop, you **must** have a functioning Elasticsearch and Kibana deployment. This repository does **not** include deployment automation - it focuses on building AI-powered search and chat capabilities on top of an existing Elasticsearch environment.

**Minimum Requirements:**
- **Elasticsearch**: Version 8.x or 9.x with vector search support
- **Kibana**: Matching version to Elasticsearch
- **Python**: Version 3.8 or higher
- **OpenAI API Key**: For generating embeddings and LLM responses (or compatible alternative)

### Why You Need This

The workshop requires:
1. **Elasticsearch** with vector search capabilities for storing and querying embeddings
2. **Kibana** for Dev Tools access and monitoring search performance
3. **Python environment** for running example scripts
4. **API access** to embedding and LLM services (OpenAI or alternatives)

---

## Quick Setup Using helm-elastic-fleet-quickstart

If you don't already have an Elasticsearch and Kibana deployment, the fastest way to get started is using the `helm-elastic-fleet-quickstart` repository.

### Step 1: Clone the helm-elastic-fleet-quickstart Repository

**Before starting this workshop**, set up your Elasticsearch environment:

```bash
# Navigate to your development directory
cd ~/dev

# Clone the Elastic Fleet quickstart repository
git clone https://github.com/bmayroseEGS/helm-elastic-fleet-quickstart.git
cd helm-elastic-fleet-quickstart/helm_elastic_fleet_quickstart
```

### Step 2: Run the Machine Setup Script

This script installs Docker, Kubernetes (K3s), Helm, and sets up a local Docker registry.

```bash
cd deployment_infrastructure
./setup-machine.sh
```

**What This Script Does:**
- Installs Docker Engine
- Installs K3s (lightweight Kubernetes)
- Installs kubectl command-line tool
- Installs Helm package manager
- Starts a local Docker registry on `localhost:5000`
- Configures Docker group permissions

**At the End:**
When prompted to activate Docker permissions, choose **Yes**:

```
Do you want to activate Docker permissions now and setup the registry? (y/n): y
```

The script will:
- Activate Docker group membership with `newgrp docker`
- Start the local Docker registry
- Display "Setup Complete!" with next steps

### Step 3: Deploy Elasticsearch and Kibana

After the setup script completes, deploy **only Elasticsearch and Kibana**:

```bash
# From the helm-elastic-fleet-quickstart directory
cd ../helm_charts
./deploy.sh
```

**Component Selection:**

When prompted, select:
- **Elasticsearch**: `y` (Yes)
- **Kibana**: `y` (Yes)
- **Logstash**: `n` (No - not needed for this workshop)

```
Deploy Elasticsearch? (y/n): y
Deploy Kibana? (y/n): y
Deploy Logstash? (y/n): n
```

**Why Only Elasticsearch and Kibana?**

For AI-powered search and chat, you only need:
- **Elasticsearch** - Stores documents, embeddings, and executes searches
- **Kibana** - Provides Dev Tools for testing and monitoring

Fleet Server and Logstash are not required for this workshop.

**Deployment Time:**
- Elasticsearch: ~2-5 minutes
- Kibana: ~1-3 minutes

Wait for both components to reach "Running" status before proceeding.

### Step 4: Access Kibana

Once deployed, access Kibana from your local machine using port forwarding.

**If deploying on a remote server:**

From your **local machine**, create an SSH tunnel with port forwarding:

```bash
ssh -i your-key.pem -L 9200:localhost:9200 -L 5601:localhost:5601 user@server
```

Then, on the **remote server**, run:

```bash
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200 &
kubectl port-forward -n elastic svc/kibana 5601:5601 &
```

**If deploying locally:**

```bash
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200 &
kubectl port-forward -n elastic svc/kibana 5601:5601 &
```

**Access Kibana:**

Open your browser and navigate to:
```
http://localhost:5601
```

**Login credentials:**
- **Username**: `elastic`
- **Password**: `elastic`

### Step 5: Verify Deployment

Before proceeding with the workshop, verify your deployment:

**Check Elasticsearch:**
```bash
curl http://localhost:9200
```

Expected response:
```json
{
  "name" : "elasticsearch-master-0",
  "cluster_name" : "elasticsearch",
  "version" : {
    "number" : "9.2.2",
    ...
  }
}
```

**Check Kibana:**

Navigate to: `http://localhost:5601/app/dev_tools#/console`

Run this query in Dev Tools:
```elasticsearch
GET _cluster/health
```

Expected response:
```json
{
  "cluster_name" : "elasticsearch",
  "status" : "green",
  "number_of_nodes" : 1,
  ...
}
```

---

## Python Environment Setup

### Install Python 3.8+

Verify Python version:
```bash
python3 --version
```

If not installed or version is too old, install Python 3.8 or higher for your platform.

### Create Virtual Environment (Recommended)

```bash
# Navigate to the workshop directory
cd ~/dev/elasticsearch-ai-search-chat-demo

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

This installs:
- `elasticsearch` - Official Elasticsearch Python client
- `openai` - OpenAI API client for embeddings and LLM
- `python-dotenv` - Environment variable management
- `tqdm` - Progress bars for batch operations
- `jupyter` - Interactive notebooks (optional)

---

## OpenAI API Setup

### Get an OpenAI API Key

1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API keys: [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
4. Create a new API key
5. **Copy and save it** - you won't see it again

### Add Credits to Your Account

OpenAI requires a positive balance to use the API:

1. Go to [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)
2. Add payment method
3. Add at least $5 in credits

**Workshop Cost Estimate:**
- Embedding generation (500 docs): ~$0.01 - $0.05
- LLM responses (100 queries): ~$0.10 - $0.50
- **Total**: Under $1 for the entire workshop

### Alternative: Use Other Embedding Providers

If you prefer not to use OpenAI, you can use alternatives:

**Sentence Transformers (Free, Local):**
```bash
pip install sentence-transformers
```

**Cohere (Alternative API):**
- Sign up at [https://cohere.com/](https://cohere.com/)
- Get API key
- Modify scripts to use Cohere client

**Elasticsearch ELSER (Elastic's Model):**
- No API key needed
- Runs within Elasticsearch
- Automated setup available - see [ELSER_SETUP.md](ELSER_SETUP.md)
- Reference: [ELSER documentation](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)

---

## Configuration

### Create config.py

Copy the example configuration:

```bash
cd ~/dev/elasticsearch-ai-search-chat-demo
cp config.example.py config.py
```

Edit `config.py` with your credentials:

```python
# Elasticsearch connection
ELASTICSEARCH_URL = "http://localhost:9200"
ELASTICSEARCH_USERNAME = "elastic"
ELASTICSEARCH_PASSWORD = "elastic"

# OpenAI configuration
OPENAI_API_KEY = "sk-your-api-key-here"
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4-turbo-preview"

# Index configuration
INDEX_NAME = "products-semantic-search"
VECTOR_DIMENSIONS = 1536  # For OpenAI text-embedding-3-small
```

**Security Note:** Never commit `config.py` to version control. It's included in `.gitignore`.

---

## Verifying Prerequisites

### 1. Elasticsearch is Running

```bash
curl http://localhost:9200/_cluster/health?pretty
```

Expected: `"status" : "green"` or `"yellow"`

### 2. Kibana is Accessible

Navigate to: `http://localhost:5601`

You should see the Kibana interface.

### 3. Dev Tools Works

In Kibana, go to: `Management` → `Dev Tools`

Run:
```elasticsearch
GET /
```

You should see cluster information.

### 4. Python Environment Ready

```bash
python --version  # Should be 3.8+
pip list | grep elasticsearch  # Should show elasticsearch package
```

### 5. OpenAI API Key Valid

Test your API key:

```python
from openai import OpenAI

client = OpenAI(api_key="your-key-here")
response = client.embeddings.create(
    model="text-embedding-3-small",
    input="test"
)
print("API key is valid!")
```

### 6. Sufficient Disk Space

Check Elasticsearch disk usage:

```elasticsearch
GET _cat/allocation?v&h=node,disk.used,disk.avail,disk.total,disk.percent
```

Ensure you have at least **5GB** available for workshop data and indices.

---

## Alternative Deployment Methods

If you already have Elasticsearch and Kibana running through other means (ECK, ECE, Elastic Cloud, etc.), you can use this workshop directly. Ensure you have:

### Required Elasticsearch Features

- **Version**: 8.0 or higher (for vector search support)
- **Dense vector support**: Enabled by default in 8.x+
- **Sufficient memory**: At least 4GB heap for Elasticsearch
- **API access**: HTTP/HTTPS access to Elasticsearch

### Required Permissions

For basic workshop usage:
- `create` and `write` access to indices
- `read` access for searching
- Dev Tools access in Kibana

For production deployments:
- `manage` cluster privilege (for index templates)
- `manage_ilm` privilege (for index lifecycle management)
- `monitor` privilege (for performance monitoring)

---

## Troubleshooting Prerequisites

### Cannot Access Kibana

**Check pod status:**
```bash
kubectl get pods -n elastic
```

**Check Kibana logs:**
```bash
kubectl logs -n elastic -l app=kibana
```

**Verify port-forward:**
```bash
kubectl port-forward -n elastic svc/kibana 5601:5601
```

### Cannot Connect to Elasticsearch

**Check Elasticsearch pods:**
```bash
kubectl get pods -n elastic -l app=elasticsearch
```

**Test connectivity:**
```bash
curl http://localhost:9200/_cluster/health
```

### Python Package Installation Fails

**Upgrade pip:**
```bash
pip install --upgrade pip
```

**Install packages one by one:**
```bash
pip install elasticsearch
pip install openai
pip install python-dotenv
pip install tqdm
```

### OpenAI API Errors

**Error: "You exceeded your current quota"**
- Add credits to your OpenAI account
- Check billing: [https://platform.openai.com/account/billing](https://platform.openai.com/account/billing)

**Error: "Invalid API key"**
- Verify your API key in `config.py`
- Check that you copied the full key (starts with `sk-`)
- Regenerate a new key if needed

**Error: "Rate limit exceeded"**
- You're making requests too quickly
- Scripts include retry logic
- Wait a few seconds and try again

### Insufficient Storage

**Check current disk usage:**
```elasticsearch
GET _cat/allocation?v&h=node,disk.used,disk.avail,disk.total,disk.percent
```

**If storage is low:**
1. Delete old or unused indices
2. Add more storage to your Kubernetes cluster
3. Use external Elasticsearch deployment with more disk space

---

## Workshop Data Requirements

### Sample Dataset

The workshop uses a sample product catalog with:
- **500 products** across various categories
- Product names, descriptions, specifications
- Price ranges: $100 - $5000
- Categories: Laptops, monitors, accessories, software

### Storage Requirements

**Per document:**
- Text fields: ~1-2 KB
- Embedding vector (1536 dimensions, quantized): ~1.5 KB
- Total per document: ~3-4 KB

**For 500 documents:**
- Raw data: ~1.5 MB
- With indices and metadata: ~5-10 MB

**Total workshop storage:** Under 100 MB including all indices and temporary data.

---

## Next Steps

Once you have verified all prerequisites:

1. **Run the setup script**: `cd scripts && ./setup-environment.sh`
2. **Follow Part 1**: Work through smart search examples
3. **Follow Part 2**: Build conversational AI applications
4. **Experiment**: Try your own data and queries

---

## Quick Reference Commands

**Port Forwarding (Remote Server):**
```bash
# From local machine
ssh -i your-key.pem -L 9200:localhost:9200 -L 5601:localhost:5601 user@server

# On remote server
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200 &
kubectl port-forward -n elastic svc/kibana 5601:5601 &
```

**Port Forwarding (Local):**
```bash
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200 &
kubectl port-forward -n elastic svc/kibana 5601:5601 &
```

**Access URLs:**
- Elasticsearch: `http://localhost:9200`
- Kibana: `http://localhost:5601`
- Dev Tools: `http://localhost:5601/app/dev_tools#/console`

**Default Credentials:**
- Username: `elastic`
- Password: `elastic`

**Python Virtual Environment:**
```bash
# Activate
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Deactivate
deactivate
```

---

## Support

For setup issues with the helm-elastic-fleet-quickstart repository:
- Visit: [https://github.com/bmayroseEGS/helm-elastic-fleet-quickstart](https://github.com/bmayroseEGS/helm-elastic-fleet-quickstart)
- Check: `TROUBLESHOOTING.md` in that repository

For Elasticsearch/Kibana specific issues:
- Elasticsearch Documentation: [https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- Kibana Documentation: [https://www.elastic.co/guide/en/kibana/current/index.html](https://www.elastic.co/guide/en/kibana/current/index.html)

For OpenAI API issues:
- OpenAI Documentation: [https://platform.openai.com/docs](https://platform.openai.com/docs)
- OpenAI Help Center: [https://help.openai.com/](https://help.openai.com/)
