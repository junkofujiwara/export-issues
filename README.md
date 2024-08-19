# Export GitHub Issues

# Preparation
Install dependancies
    
```bash
pip install -r requirements.txt
```

# Usage
1. Set target environments

```bash
export GITHUB_API_ENDPOINT="https://api.github.com"
export GITHUB_ORG="your-org"
export GITHUB_REPO="your-repo"
export GITHUB_TOKEN="your-token"
export GITHUB_OUTPUT="/path/to/output"
```

2. Run the script

```bash
python export.py
```

# Output
md files will be generated in the `GITHUB_OUTPUT` directory.

