# Streamlit Cloud Deployment Guide

## Prerequisites

Your application is **ready to deploy** to Streamlit Community Cloud with zero configuration needed! The app doesn't require any API keys or environment variables.

## Deployment Steps

### 1. Go to Streamlit Cloud
Visit [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.

### 2. Create New App
Click **"New app"** or **"Deploy an app"** button.

### 3. Configure Deployment

Fill in the following fields:

- **Repository:** `SaudMonsour/ai-trader` (or `investing` if you renamed it)
- **Branch:** `main`
- **Main file path:** `streamlit_app.py`

### 4. Advanced Settings (Optional)

Click **"Advanced settings"** if you want to customize:
- **Python version:** 3.9 or higher
- **Secrets:** None required for this app

### 5. Deploy!

Click **"Deploy!"** button. Streamlit will:
1. Clone your repository
2. Install dependencies from `requirements.txt`
3. Start your application
4. Provide you with a public URL

## What Gets Deployed

The application includes:
- **Frontend:** Streamlit dashboard (`streamlit_app.py`)
- **Configuration:** `config/config.yaml` with 500+ S&P stocks
- **State Management:** `data/state.json` for portfolio tracking
- **Logging:** System logs at `logs/trading.log`

## Pages Available

Your deployed app will have:
1. **Dashboard** - System health, cash, positions, recent orders
2. **Signals** - Trading signals history
3. **Orders** - Complete order history
4. **Logs** - System logs with search
5. **Settings** - Emergency controls and configuration viewer

## Important Notes

⚠️ **File Persistence:** Streamlit Cloud has ephemeral storage. Data in `data/state.json` will reset on app restart. For persistent storage, you'll need to:
- Connect to a database (e.g., PostgreSQL, MongoDB)
- Or use cloud storage (e.g., AWS S3, Google Cloud Storage)

✅ **No Secrets Needed:** This app runs in paper trading mode and doesn't require broker API keys for basic functionality.

## Monitoring

After deployment, monitor your app at:
- App URL: `https://[your-app-name].streamlit.app`
- Logs: Available in the Streamlit Cloud dashboard
- Resources: Check CPU/memory usage in app settings

## Troubleshooting

### App won't start
- Check the Build Logs in Streamlit Cloud dashboard
- Ensure `requirements.txt` has all dependencies
- Verify Python version compatibility

### Missing data/logs
- The app creates empty files on first run
- Check `data/` and `logs/` directories exist in repository

### Permission errors
- Ensure write permissions in Streamlit Cloud settings
- Or modify app to work in read-only mode

## Next Steps

After successful deployment:
1. Test all pages (Dashboard, Signals, Orders, Logs, Settings)
2. Configure your desired stocks in `config/config.yaml`
3. Set up persistent storage if needed
4. Share your app URL with stakeholders!

## Support

For issues specific to:
- **Streamlit Cloud:** Visit [docs.streamlit.io](https://docs.streamlit.io)
- **This App:** Check repository README or create an issue on GitHub
