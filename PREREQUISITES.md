# Prerequisites

Simple requirements for the AI-Powered Search and Chat workshop using ELSER.

## What You Need

### Absolute Minimum (For Part 1 - Smart Search)

1. **Elasticsearch 8.8+** - For ELSER v2 support
2. **Python 3.8+** - To run the workshop scripts
3. **4GB+ RAM** - For ML nodes to run ELSER

**That's it!** No API keys, no external services, no extra costs.

### Optional (For Part 2 - Conversational AI)

4. **OpenAI API Key** - Only needed for the chatbot LLM (Part 2)
5. **Kibana** - Nice to have for Dev Tools and monitoring (optional)

---

## Quick Start - Option 1: Using helm-elastic-fleet-quickstart

If you don't have Elasticsearch yet, use the helm-elastic-fleet-quickstart repository to deploy a local cluster.

### Step 1: Clone and Setup Infrastructure

```bash
cd ~/dev
git clone https://github.com/bmayroseEGS/helm-elastic-fleet-quickstart.git
cd helm-elastic-fleet-quickstart/helm_elastic_fleet_quickstart/deployment_infrastructure

# Install Docker, K3s, Helm, kubectl
./setup-machine.sh
```

When prompted, choose **Yes** to activate Docker permissions.

### Step 2: Deploy Elasticsearch (and optionally Kibana)

```bash
cd ../helm_charts
./deploy.sh
```

When prompted:
- **Elasticsearch**: `y` ✅ Required
- **Kibana**: `y` ✅ Recommended (for Dev Tools)
- **Logstash**: `n` ❌ Not needed

Wait 2-5 minutes for deployment to complete.

### Step 3: Access Elasticsearch

**If deploying on a remote server:**
```bash
# From your local machine
ssh -i your-key.pem -L 9200:localhost:9200 -L 5601:localhost:5601 user@server

# On the remote server
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200 &
kubectl port-forward -n elastic svc/kibana 5601:5601 &
```

**If deploying locally:**
```bash
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200 &
kubectl port-forward -n elastic svc/kibana 5601:5601 &
```

**Test it:**
```bash
curl http://localhost:9200
```

You should see cluster information.

**Default credentials:**
- Username: `elastic`
- Password: `elastic`

---

## Quick Start - Option 2: Elastic Cloud

Using Elastic Cloud? Even easier:

1. Create a deployment at [cloud.elastic.co](https://cloud.elastic.co)
2. Choose version 8.8 or higher
3. Copy the Elasticsearch endpoint URL
4. Copy your credentials or create an API key

Update `config.py`:
```python
ELASTICSEARCH_URL = "https://your-deployment.es.region.cloud.es.io:9243"
ELASTICSEARCH_USERNAME = "elastic"
ELASTICSEARCH_PASSWORD = "your-password"
```

---

## Quick Start - Option 3: Already Have Elasticsearch?

If you already have Elasticsearch running:

1. **Verify version** - Must be 8.8+ for ELSER v2
   ```bash
   curl http://localhost:9200
   ```

2. **Check ML nodes** - ELSER needs ML-capable nodes
   ```bash
   curl http://localhost:9200/_cat/ml/nodes?v
   ```

   If you see nodes listed, you're good! If empty, nodes will use general roles (slower but works).

3. **That's it!** You're ready to start the workshop.

---

## Python Environment Setup

### Install Python 3.8+

Check your Python version:
```bash
python3 --version
```

If you need to install Python, visit [python.org](https://www.python.org/downloads/)

### Create Virtual Environment (Recommended)

```bash
cd ~/dev/elasticsearch-ai-search-chat-demo

# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `elasticsearch` - Elasticsearch Python client
- `tqdm` - Progress bars
- `rich` - Pretty terminal output
- `python-dotenv` - Environment management
- `requests` - HTTP client

**No OpenAI package needed for Part 1!**

---

## Configuration

### Create config.py

```bash
cp config.example.py config.py
```

### Edit config.py

Open `config.py` and update:

```python
# Elasticsearch connection
ELASTICSEARCH_URL = "http://localhost:9200"
ELASTICSEARCH_USERNAME = "elastic"
ELASTICSEARCH_PASSWORD = "elastic"

# That's all you need for Part 1!
# ELSER is already the default embedding method
```

**For Part 2 (Optional - Conversational AI):**

If you want to run Part 2 chatbot:

1. Install OpenAI package:
   ```bash
   pip install openai
   ```

2. Add API key to config.py:
   ```python
   OPENAI_API_KEY = "sk-your-api-key-here"
   ```

3. Get API key from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

---

## Verify Everything Works

### Check Elasticsearch

```bash
curl http://localhost:9200/_cluster/health?pretty
```

Expected: `"status" : "green"` or `"yellow"`

### Check Python Environment

```bash
python --version  # Should be 3.8+
pip list | grep elasticsearch  # Should show elasticsearch package
```

### Check Kibana (Optional)

Navigate to: `http://localhost:5601`

Go to Dev Tools and run:
```
GET /
```

You should see cluster information.

---

## What About...

### Do I need API keys?

**For Part 1 (Smart Search):** NO! ELSER runs in Elasticsearch.

**For Part 2 (Conversational AI):** Yes, OpenAI API key for the LLM (GPT).

### Do I need GPU?

NO! ELSER runs on CPU. It's optimized for CPU inference.

### How much will this cost?

**Infrastructure:**
- Local setup: Free (your hardware)
- Elastic Cloud: Starts at ~$17/month

**API costs:**
- Part 1: $0 (no external APIs)
- Part 2: ~$0.50-$1 for the workshop (if using OpenAI GPT)

### What if I don't have 4GB RAM?

ELSER needs at least 4GB for ML nodes. If you don't have this:
- Use Elastic Cloud (handles this for you)
- Or skip Part 1 and use the OpenAI alternative in `examples/openai_alternative/`

### Can I use this in production?

Yes! But consider:
- Dedicated ML nodes for better performance
- More allocations for higher throughput
- Monitor memory usage
- See [ELSER_SETUP.md](ELSER_SETUP.md) for production tips

---

## Troubleshooting

### "Could not connect to Elasticsearch"

**Check if running:**
```bash
curl http://localhost:9200
```

**If using kubectl:**
```bash
kubectl get pods -n elastic
kubectl port-forward -n elastic svc/elasticsearch-master 9200:9200
```

**Check credentials** in `config.py`

### "ELSER model not ready"

First-time setup downloads the model (2-5 minutes). Check status:
```bash
GET _ml/trained_models/.elser_model_2/_stats
```

Look for `"state": "started"`

### "No ML nodes found"

ELSER will use general-purpose nodes (slower but works). For better performance:
- Add dedicated ML nodes, OR
- Use Elastic Cloud (has ML nodes), OR
- Accept slightly slower performance

### Python import errors

Make sure you activated your virtual environment:
```bash
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

And installed dependencies:
```bash
pip install -r requirements.txt
```

---

## Next Steps

Once prerequisites are complete:

1. ✅ Elasticsearch 8.8+ running
2. ✅ Python 3.8+ installed
3. ✅ Dependencies installed (`pip install -r requirements.txt`)
4. ✅ `config.py` created with your credentials

**You're ready!** Start the workshop:

```bash
# Part 1 - Step 1: Setup ELSER
python part1_smart_search/01_setup_index.py
```

---

## Support

**For Elasticsearch setup issues:**
- helm-elastic-fleet-quickstart: [GitHub](https://github.com/bmayroseEGS/helm-elastic-fleet-quickstart)
- Elastic Documentation: [elastic.co/guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

**For ELSER-specific issues:**
- See [ELSER_SETUP.md](ELSER_SETUP.md)
- Elastic ML Docs: [Machine Learning Guide](https://www.elastic.co/guide/en/machine-learning/current/ml-nlp-elser.html)

**For workshop issues:**
- Check [README.md](README.md) troubleshooting section
- Review script output for error messages
- Ensure you ran scripts in order (01 → 02 → 03)
