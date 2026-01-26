# OpenAI API Key Setup Guide

## Quick Start

Your FastAPI backend is configured to load the OpenAI API key from `backend/.env`.

### Current Status

The `.env` file currently has a **placeholder** key:

```bash
OPENAI_API_KEY=sk-REPLACE_ME_WITH_REAL_KEY
```

### How to Add Your Real API Key

1. **Get your OpenAI API key:**
   - Go to https://platform.openai.com/api-keys
   - Log in to your OpenAI account
   - Click "Create new secret key"
   - Copy the key (starts with `sk-proj-` or `sk-`)

2. **Replace the placeholder in backend/.env:**

   Open `backend/.env` and replace line 52:

   ```bash
   # Before (placeholder):
   OPENAI_API_KEY=sk-REPLACE_ME_WITH_REAL_KEY

   # After (your real key):
   OPENAI_API_KEY=sk-proj-abc123xyz...your-actual-key-here
   ```

3. **Restart your FastAPI server:**

   ```bash
   cd backend
   uvicorn main:app --reload
   ```

4. **Verify it's loaded:**

   You should see in the startup logs:

   ```
   INFO - ✓ Environment variables loaded from: /path/to/backend/.env
   INFO - ✓ OPENAI_API_KEY loaded successfully (starts with: sk-proj-abc123...)
   INFO - Runtime check - OPENAI_API_KEY loaded: True
   ```

   If you see a warning:
   ```
   ⚠ OPENAI_API_KEY is set to placeholder value - Replace with real key
   ```
   It means you need to replace the placeholder with your real key.

## Production Deployment

### Docker / Railway / Render

For production deployments, **set the environment variable directly** in your platform:

**Railway:**
```bash
# In Railway dashboard > Variables
OPENAI_API_KEY=sk-proj-your-real-key
```

**Docker:**
```bash
docker run -e OPENAI_API_KEY=sk-proj-your-real-key ...
```

**Render:**
```bash
# In Render dashboard > Environment
OPENAI_API_KEY=sk-proj-your-real-key
```

The backend is configured with `override=False`, so environment variables from your deployment platform will take precedence over the `.env` file.

## Verification

Run this command to verify the key is loaded:

```bash
cd backend
python3 -c "from app.config import settings; print(f'Loaded: {settings.OPENAI_API_KEY is not None}')"
```

Expected output:
```
✓ Environment variables loaded from: /path/to/backend/.env
⚠ OPENAI_API_KEY is set to placeholder value - Replace with real key
Loaded: True
```

After replacing with a real key:
```
✓ Environment variables loaded from: /path/to/backend/.env
✓ OPENAI_API_KEY loaded successfully (starts with: sk-proj-...)
Loaded: True
```

## Troubleshooting

### "OPENAI_API_KEY not set" error

1. Check that `backend/.env` exists
2. Check that the key is not commented out (no `#` at the start)
3. Restart the FastAPI server after editing `.env`
4. Verify the key format starts with `sk-`

### "Invalid API key" error from OpenAI

1. Verify your key is active at https://platform.openai.com/api-keys
2. Check you have billing enabled on your OpenAI account
3. Ensure you copied the full key (they're usually 48-64 characters)

## Security Notes

- **Never commit your real API key to git**
- The `.env` file is in `.gitignore`
- Use environment variables for production deployments
- Rotate your API key if it's exposed
