# Skill: configure-domain-allowlist

**Version**: 1.0.0
**Created**: 2026-01-19
**Category**: Phase 3 - Configuration

---

## 1. Purpose

Configure OpenAI ChatKit domain allowlist for secure frontend integration with Phase 3 AI Chatbot. This skill documents the complete process of obtaining a domain key from OpenAI, configuring it for local development and production (Vercel), and troubleshooting common issues.

Domain allowlist configuration ensures only authorized domains can use your ChatKit integration, preventing unauthorized usage and protecting your OpenAI API quota.

---

## 2. Applicable Agents

**Primary Agent**: `chatkit-frontend-integrator`
- Configures ChatKit security settings
- Sets up environment variables
- Ensures deployment compatibility

**Supporting Agents**:
- `nextjs-frontend-architect` - Environment configuration review

---

## 3. Input

### Prerequisites
- OpenAI account with organization access
- Frontend Next.js application
- Deployment domains identified (localhost + production)

### Requirements
- Generate domain key from OpenAI dashboard
- Configure environment variables for local and production
- Verify domain allowlist works on Vercel

---

## 4. Output

## Step-by-Step Setup Guide

### Step 1: Access OpenAI ChatKit Dashboard

**1.1 Navigate to ChatKit Settings**

```
https://platform.openai.com/settings/organization/chat-kit
```

**1.2 Sign In**
- Log in with your OpenAI account
- Ensure you have organization access
- If no organization, create one first

**1.3 Locate Domain Keys Section**
- Look for "Domain Keys" or "Allowed Domains"
- Click "Create new domain key" or "Add domain key"

---

### Step 2: Generate Domain Key

**2.1 Create New Domain Key**

In the OpenAI dashboard:

1. Click **"Create Domain Key"** or **"New Key"**
2. Enter a descriptive name: `todo-app-chatkit` or `phase3-chatbot`
3. Click **"Generate"** or **"Create"**

**2.2 Copy Domain Key**

You'll receive a domain key in format:
```
dk_live_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

⚠️ **IMPORTANT**: Copy this immediately - it may only be shown once!

Store securely in password manager or `.env.local`

---

### Step 3: Configure Allowed Domains

**3.1 Add Development Domain**

In the same OpenAI dashboard:

1. Find **"Allowed Domains"** section under your domain key
2. Click **"Add Domain"**
3. Enter: `http://localhost:3000`
4. Click **"Save"** or **"Add"**

**3.2 Add Production Domain**

If deploying to Vercel:

1. Click **"Add Domain"** again
2. Enter your Vercel URL: `https://your-app.vercel.app`
   - Replace `your-app` with your actual Vercel project name
   - Use the exact URL from Vercel dashboard
3. Click **"Save"** or **"Add"**

**3.3 Add Custom Domain (if applicable)**

If using custom domain:

1. Click **"Add Domain"** again
2. Enter: `https://yourdomain.com`
3. Click **"Save"**

**Example Configuration**:
```
Domain Key: dk_live_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890

Allowed Domains:
✓ http://localhost:3000
✓ https://todo-app-xyz123.vercel.app
✓ https://chat.yourdomain.com
```

---

### Step 4: Configure Local Development

**4.1 Create Environment File**

**File**: `frontend/.env.local`

```bash
# OpenAI ChatKit Domain Key
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk_live_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890

# Backend API URL (local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**4.2 Add to .gitignore**

Ensure `.env.local` is NOT committed to git:

**File**: `frontend/.gitignore`

```
# Environment files
.env.local
.env.*.local
```

✅ Already included in default Next.js `.gitignore`

**4.3 Create Example File**

**File**: `frontend/.env.example`

```bash
# OpenAI ChatKit Domain Key
# Get from: https://platform.openai.com/settings/organization/chat-kit
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your_domain_key_here

# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# For production, update to your backend URL:
# NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

---

### Step 5: Configure Production (Vercel)

**Method 1: Vercel Dashboard**

1. Go to https://vercel.com/dashboard
2. Select your project
3. Click **"Settings"** tab
4. Click **"Environment Variables"** in sidebar
5. Add variables:

**Variable 1**:
```
Name:  NEXT_PUBLIC_OPENAI_DOMAIN_KEY
Value: dk_live_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
Environment: Production, Preview, Development (select all)
```

**Variable 2**:
```
Name:  NEXT_PUBLIC_API_URL
Value: https://your-backend.railway.app
Environment: Production, Preview, Development
```

6. Click **"Save"**
7. Redeploy your application for changes to take effect

---

**Method 2: Vercel CLI**

```bash
# Install Vercel CLI (if not already)
npm install -g vercel

# Link project (if not already linked)
vercel link

# Add environment variables
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY production
# Paste: dk_live_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890

vercel env add NEXT_PUBLIC_API_URL production
# Paste: https://your-backend.railway.app

# Add for preview/development as well
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY preview
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY development

vercel env add NEXT_PUBLIC_API_URL preview
vercel env add NEXT_PUBLIC_API_URL development

# Trigger redeploy
vercel --prod
```

---

### Step 6: Verify Configuration

**6.1 Local Verification**

```bash
# Start frontend
cd frontend
npm run dev

# Visit http://localhost:3000/chat
# Open browser console (F12)
# Check for ChatKit load
```

**Expected console output**:
```
ChatKit initialized
Domain key: dk_live_...
```

**If error**:
```
❌ ChatKit domain not allowed
```
→ Check domain key and verify `http://localhost:3000` is in allowed domains

---

**6.2 Production Verification**

After deploying to Vercel:

```bash
# Visit your production URL
https://your-app.vercel.app/chat

# Open browser console
# Check for errors
```

**Expected behavior**:
- ChatKit loads without errors
- Can send and receive messages
- No CORS or domain errors

**If error**:
```
❌ Domain not allowed for this API key
```
→ Add `https://your-app.vercel.app` to OpenAI allowed domains

---

### Step 7: Update ChatKit Component

**File**: `frontend/app/chat/page.tsx`

```tsx
'use client';

import { ChatKit } from '@openai/chatkit';

export default function ChatPage() {
  // Verify environment variable loaded
  const domainKey = process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY;

  // Error handling for missing key
  if (!domainKey) {
    return (
      <div className="p-8 text-center">
        <h2 className="text-xl font-bold text-red-600">
          Configuration Error
        </h2>
        <p className="mt-2 text-gray-600">
          NEXT_PUBLIC_OPENAI_DOMAIN_KEY is not configured.
        </p>
        <p className="mt-1 text-sm text-gray-500">
          See .env.example for setup instructions.
        </p>
      </div>
    );
  }

  return (
    <div className="h-screen">
      <ChatKit
        domainKey={domainKey}
        onSendMessage={handleSendMessage}
        placeholder="Ask me to manage your tasks..."
      />
    </div>
  );
}
```

---

## 5. Environment Variable Requirements

### Development (.env.local)

```bash
# Required for ChatKit to function
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk_live_...

# Required for API communication
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production (Vercel)

```bash
# Required for ChatKit to function
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=dk_live_...

# Required for API communication
NEXT_PUBLIC_API_URL=https://your-backend.railway.app

# Optional: Custom domain
# NEXT_PUBLIC_APP_URL=https://yourdomain.com
```

### Variable Naming Rules

**Must start with `NEXT_PUBLIC_`**:
- ✅ `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` - Accessible in browser
- ❌ `OPENAI_DOMAIN_KEY` - Server-side only (won't work)

**Why**: Next.js only exposes environment variables with `NEXT_PUBLIC_` prefix to the browser. ChatKit runs client-side, so it needs `NEXT_PUBLIC_`.

---

## 6. Security Considerations

### Domain Key Security

**✅ Safe Practices**:
```bash
# Use .env.local for local development (not committed)
# Use Vercel environment variables for production (encrypted)
# Restrict allowed domains to your actual domains only
```

**❌ Unsafe Practices**:
```javascript
// DON'T: Hardcode in source code
const domainKey = "dk_live_AbCdEf...";  // ❌ Visible in git

// DON'T: Commit .env.local to git
git add .env.local  // ❌ Exposed to public
```

### Domain Restrictions

**Recommended Setup**:
```
Development: http://localhost:3000
Staging:     https://staging.yourapp.com
Production:  https://yourapp.com
```

**Not Recommended**:
```
Wildcard:    https://*.yourapp.com  // ❌ Too broad
Any domain:  *                       // ❌ No security
```

### Key Rotation

**When to rotate**:
- Key accidentally committed to public repo
- Team member with access leaves
- Every 90 days (best practice)
- After security incident

**How to rotate**:
1. Generate new domain key in OpenAI dashboard
2. Update environment variables (local + Vercel)
3. Redeploy application
4. Delete old domain key from OpenAI dashboard

---

## 7. Troubleshooting

### Issue: "Domain not allowed for this API key"

**Symptoms**:
```
Error: Domain not allowed for this API key
Request from: http://localhost:3000
```

**Solutions**:

**Check 1**: Verify domain in OpenAI dashboard
```bash
# Current URL must match exactly
Development: http://localhost:3000  (not https, not different port)
Production:  https://your-app.vercel.app  (exact URL)
```

**Check 2**: Clear browser cache
```bash
# Chrome: Ctrl+Shift+Delete → Clear cached images and files
# Or: Hard refresh: Ctrl+Shift+R
```

**Check 3**: Verify environment variable loaded
```javascript
// In browser console
console.log(process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY);
// Should print: dk_live_...
```

**Check 4**: Restart Next.js dev server
```bash
# Stop server: Ctrl+C
# Delete .next folder
rm -rf .next
# Restart
npm run dev
```

---

### Issue: "NEXT_PUBLIC_OPENAI_DOMAIN_KEY is undefined"

**Symptoms**:
```
ChatKit fails to load
Console: undefined
```

**Solutions**:

**Check 1**: Verify file name
```bash
# Must be exactly .env.local (not .env or env.local)
ls -la .env.local
```

**Check 2**: Verify variable name prefix
```bash
# Must start with NEXT_PUBLIC_
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=...  ✅
OPENAI_DOMAIN_KEY=...              ❌
```

**Check 3**: Verify file location
```bash
# Must be in frontend/ directory (same level as package.json)
frontend/
  .env.local       ✅
  package.json

frontend/src/
  .env.local       ❌ Wrong location
```

**Check 4**: Restart server after creating .env.local
```bash
# Next.js reads .env.local on startup only
# Changes require restart
npm run dev
```

---

### Issue: Works locally but not on Vercel

**Symptoms**:
```
✅ http://localhost:3000 - Works
❌ https://your-app.vercel.app - Fails
```

**Solutions**:

**Check 1**: Verify Vercel environment variables set
```bash
# In Vercel dashboard → Settings → Environment Variables
# Both variables must be present for Production
NEXT_PUBLIC_OPENAI_DOMAIN_KEY ✓
NEXT_PUBLIC_API_URL ✓
```

**Check 2**: Redeploy after setting variables
```bash
# Environment variables only apply to new deployments
vercel --prod
# Or trigger redeploy in Vercel dashboard
```

**Check 3**: Add Vercel URL to allowed domains
```bash
# In OpenAI dashboard, add exact Vercel URL
https://your-app-abc123.vercel.app  ✅
https://your-app.vercel.app         ❌ Different URL
```

**Check 4**: Check Vercel deployment logs
```bash
# In Vercel dashboard → Deployments → [Latest] → View Build Logs
# Look for environment variable confirmation
```

---

### Issue: CORS Errors

**Symptoms**:
```
Access to fetch at 'https://api.openai.com/...' from origin
'http://localhost:3000' has been blocked by CORS policy
```

**Solutions**:

**This is NOT a domain key issue** - ChatKit CORS errors are usually:

**Check 1**: Backend CORS configuration
```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Check 2**: API URL configuration
```bash
# Verify NEXT_PUBLIC_API_URL points to correct backend
NEXT_PUBLIC_API_URL=http://localhost:8000  # Development
NEXT_PUBLIC_API_URL=https://backend.railway.app  # Production
```

---

## 8. Testing Checklist

### Local Development Testing

- [ ] Create `.env.local` with domain key
- [ ] Add `http://localhost:3000` to OpenAI allowed domains
- [ ] Start dev server: `npm run dev`
- [ ] Open `http://localhost:3000/chat`
- [ ] Open browser console (F12)
- [ ] Verify no domain errors
- [ ] Send test message
- [ ] Verify ChatKit sends/receives

### Production Testing

- [ ] Set environment variables in Vercel dashboard
- [ ] Add Vercel URL to OpenAI allowed domains
- [ ] Deploy to Vercel
- [ ] Visit production URL
- [ ] Open browser console
- [ ] Verify no domain errors
- [ ] Send test message
- [ ] Verify ChatKit works end-to-end

### Security Testing

- [ ] Verify `.env.local` in `.gitignore`
- [ ] Check domain key not in source code
- [ ] Verify only authorized domains in allowlist
- [ ] Test unauthorized domain (should fail)
- [ ] Verify environment variables not exposed in client bundle

---

## 9. Documentation Templates

### README Section

Add to `frontend/README.md`:

````markdown
## ChatKit Configuration

### Setup Domain Key

1. Get domain key from OpenAI:
   - Visit: https://platform.openai.com/settings/organization/chat-kit
   - Create new domain key
   - Add allowed domains:
     - Development: `http://localhost:3000`
     - Production: `https://your-app.vercel.app`

2. Configure locally:
   ```bash
   cp .env.example .env.local
   # Edit .env.local and add your domain key
   ```

3. Configure on Vercel:
   ```bash
   vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY production
   vercel env add NEXT_PUBLIC_API_URL production
   ```

### Troubleshooting

If you see "Domain not allowed" error:
- Verify domain key is set in environment variables
- Check current URL matches allowed domains in OpenAI dashboard
- Restart dev server after changing .env.local
````

---

### Team Onboarding Doc

**File**: `docs/CHATKIT_SETUP.md`

```markdown
# ChatKit Setup for New Developers

## Prerequisites
- OpenAI organization access (ask team lead)
- Access to Vercel project (request from DevOps)

## Steps

1. **Get Domain Key from Team Lead**
   - Ask for: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`
   - Store in password manager

2. **Local Setup**
   ```bash
   cd frontend
   cp .env.example .env.local
   # Edit .env.local and paste domain key
   npm run dev
   ```

3. **Verify**
   - Open http://localhost:3000/chat
   - Should see ChatKit interface
   - Try sending a message

4. **Troubleshooting**
   - If "Domain not allowed" error → Contact team lead
   - If environment variable undefined → Restart dev server
   - If CORS error → Check backend is running

## Security
⚠️ NEVER commit `.env.local` to git
⚠️ NEVER share domain key in Slack/email
```

---

## 10. Quick Reference

### Commands

```bash
# Local development
npm run dev

# Check environment variable
echo $NEXT_PUBLIC_OPENAI_DOMAIN_KEY

# Vercel deployment
vercel --prod

# Add Vercel env variable
vercel env add NEXT_PUBLIC_OPENAI_DOMAIN_KEY production
```

### URLs

```
OpenAI ChatKit Dashboard:
https://platform.openai.com/settings/organization/chat-kit

Vercel Dashboard:
https://vercel.com/dashboard

Vercel Environment Variables:
https://vercel.com/[team]/[project]/settings/environment-variables
```

### File Locations

```
frontend/.env.local                    (gitignored)
frontend/.env.example                  (committed)
frontend/app/chat/page.tsx             (ChatKit usage)
frontend/.gitignore                    (exclude .env.local)
docs/CHATKIT_SETUP.md                  (team documentation)
```

---

## Implementation Checklist

- [ ] Access OpenAI ChatKit dashboard
- [ ] Create new domain key with descriptive name
- [ ] Copy domain key to password manager
- [ ] Add `http://localhost:3000` to allowed domains
- [ ] Add Vercel production URL to allowed domains
- [ ] Create `frontend/.env.local` with domain key
- [ ] Verify `.env.local` in `.gitignore`
- [ ] Create `frontend/.env.example` for team reference
- [ ] Test local development (http://localhost:3000/chat)
- [ ] Add environment variables to Vercel dashboard
- [ ] Deploy to Vercel
- [ ] Test production URL
- [ ] Verify no domain errors in browser console
- [ ] Document setup in README.md
- [ ] Create team onboarding doc (CHATKIT_SETUP.md)
- [ ] Share domain key securely with team

---

**Skill Version**: 1.0.0
**Last Updated**: 2026-01-19
**Status**: Ready for Implementation
