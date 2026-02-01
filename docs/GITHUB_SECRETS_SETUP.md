# GitHub Actions Secrets Setup Guide

## Overview

This guide shows how to store sensitive credentials in GitHub Secrets for use in CI/CD workflows.

---

## Secrets to Configure

For staging/production deployments, you'll need:

1. `CLEAR_EMERGENCY_HASH` - SHA256 hash of emergency clearance token
2. `BROKER_API_KEY` - Broker API credentials
3. `NEWS_API_KEY` - News API credentials  
4. `TG_BOT_TOKEN` - Telegram bot token (for alerts)
5. `TG_CHAT_ID` - Telegram chat/group ID

---

## Method 1: GitHub Web UI

### Step 1: Navigate to Secrets
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Step 2: Add Each Secret

#### CLEAR_EMERGENCY_HASH
```
Name: CLEAR_EMERGENCY_HASH
Value: <paste SHA256 hash here>
```

To generate the hash locally:
```bash
echo -n "clear-emergency-2026-02" | sha256sum | awk '{print $1}'
```

Copy the output and paste into the **Value** field.

#### BROKER_API_KEY
```
Name: BROKER_API_KEY
Value: <paste your broker API key>
```

#### NEWS_API_KEY
```
Name: NEWS_API_KEY
Value: <paste your news API key>
```

#### TG_BOT_TOKEN (Optional)
```
Name: TG_BOT_TOKEN
Value: 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

#### TG_CHAT_ID (Optional)
```
Name: TG_CHAT_ID
Value: -1001234567890
```

### Step 3: Verify
After adding all secrets, you should see them listed (values are hidden):
- CLEAR_EMERGENCY_HASH
- BROKER_API_KEY
- NEWS_API_KEY
- TG_BOT_TOKEN
- TG_CHAT_ID

---

## Method 2: GitHub CLI

```bash
# Set CLEAR_EMERGENCY_HASH
HASH=$(echo -n "clear-emergency-2026-02" | sha256sum | awk '{print $1}')
gh secret set CLEAR_EMERGENCY_HASH --body "$HASH"

# Set BROKER_API_KEY
gh secret set BROKER_API_KEY --body "your_broker_key_here"

# Set NEWS_API_KEY
gh secret set NEWS_API_KEY --body "your_news_key_here"

# Set Telegram credentials (optional)
gh secret set TG_BOT_TOKEN --body "123456:ABC-DEF..."
gh secret set TG_CHAT_ID --body "-1001234567890"

# List all secrets
gh secret list
```

---

## Using Secrets in Workflows

Secrets are automatically available in GitHub Actions workflows:

```yaml
# .github/workflows/deploy-staging.yml
name: Deploy to Staging

on:
  push:
    branches: [staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Deploy
        env:
          CLEAR_EMERGENCY_HASH: ${{ secrets.CLEAR_EMERGENCY_HASH }}
          BROKER_API_KEY: ${{ secrets.BROKER_API_KEY }}
          NEWS_API_KEY: ${{ secrets.NEWS_API_KEY }}
          TG_BOT_TOKEN: ${{ secrets.TG_BOT_TOKEN }}
          TG_CHAT_ID: ${{ secrets.TG_CHAT_ID }}
        run: |
          # Your deployment script
          ./deploy-staging.sh
```

---

## Environment-Specific Secrets

For multiple environments (staging, production):

### Option 1: Environment Secrets

1. Go to **Settings** → **Environments**
2. Create environments: `staging`, `production`
3. Add secrets specific to each environment

Then in your workflow:
```yaml
jobs:
  deploy:
    environment: staging  # or production
    steps:
      - name: Deploy
        env:
          BROKER_API_KEY: ${{ secrets.BROKER_API_KEY }}
        run: ./deploy.sh
```

### Option 2: Prefixed Secrets

Use prefixed secret names:
- `STAGING_BROKER_API_KEY`
- `PROD_BROKER_API_KEY`

```yaml
- name: Deploy to Staging
  env:
    BROKER_API_KEY: ${{ secrets.STAGING_BROKER_API_KEY }}
  run: ./deploy.sh
```

---

## Security Best Practices

### 1. Rotate Secrets Regularly
```bash
# Monthly token rotation
NEW_TOKEN="clear-emergency-$(date +%Y-%m)"
NEW_HASH=$(echo -n "$NEW_TOKEN" | sha256sum | awk '{print $1}')
gh secret set CLEAR_EMERGENCY_HASH --body "$NEW_HASH"
```

### 2. Limit Access
- Only repository admins can view/edit secrets
- Use environment protection rules for production
- Require approval for deployments to production environment

### 3. Audit Trail
- GitHub logs all secret access in audit logs
- Review **Settings** → **Security** → **Audit log**

### 4. Never Echo Secrets
```yaml
# ❌ BAD - Never do this
- run: echo ${{ secrets.API_KEY }}

# ✅ GOOD - Use secrets only in environment variables
- env:
    API_KEY: ${{ secrets.API_KEY }}
  run: python script.py
```

---

## Verification

Test that secrets are correctly set:

```yaml
# .github/workflows/test-secrets.yml
name: Test Secrets

on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Check secrets exist
        env:
          CLEAR_EMERGENCY_HASH: ${{ secrets.CLEAR_EMERGENCY_HASH }}
          BROKER_API_KEY: ${{ secrets.BROKER_API_KEY }}
        run: |
          if [ -z "$CLEAR_EMERGENCY_HASH" ]; then
            echo "ERROR: CLEAR_EMERGENCY_HASH not set"
            exit 1
          fi
          if [ -z "$BROKER_API_KEY" ]; then
            echo "ERROR: BROKER_API_KEY not set"
            exit 1
          fi
          echo "✅ All required secrets are set"
```

---

## Troubleshooting

### Secret not available in workflow
- Check secret name matches exactly (case-sensitive)
- Verify workflow has access to the environment (if using environment secrets)
- Check branch protection rules

### Need to update a secret
```bash
# Update via CLI
gh secret set SECRET_NAME --body "new_value"

# Or via web UI: Settings → Secrets → Edit
```

### Emergency: Revoke compromised secret
1. Immediately delete the secret from GitHub
2. Revoke the API key/token at the provider
3. Generate new credentials
4. Add new secret to GitHub
5. Redeploy affected services

---

## Example: Complete Setup Script

```bash
#!/bin/bash
# setup-github-secrets.sh

# Generate emergency stop hash
TOKEN="clear-emergency-$(date +%Y-%m)"
HASH=$(echo -n "$TOKEN" | sha256sum | awk '{print $1}')

# Set secrets (will prompt for sensitive values)
gh secret set CLEAR_EMERGENCY_HASH --body "$HASH"

echo "Enter BROKER_API_KEY:"
read -s BROKER_KEY
gh secret set BROKER_API_KEY --body "$BROKER_KEY"

echo "Enter NEWS_API_KEY:"
read -s NEWS_KEY
gh secret set NEWS_API_KEY --body "$NEWS_KEY"

echo "Enter TG_BOT_TOKEN (optional, press enter to skip):"
read -s TG_TOKEN
if [ -n "$TG_TOKEN" ]; then
  gh secret set TG_BOT_TOKEN --body "$TG_TOKEN"
fi

echo "Enter TG_CHAT_ID (optional, press enter to skip):"
read TG_CHAT
if [ -n "$TG_CHAT" ]; then
  gh secret set TG_CHAT_ID --body "$TG_CHAT"
fi

echo "✅ All secrets configured"
echo "📝 Document emergency token: $TOKEN"
```

---

**Remember**: Store the actual emergency clearance token (`clear-emergency-YYYY-MM`) in your password manager or secure vault, NOT in GitHub.
