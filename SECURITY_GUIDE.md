# Security Guide

## API Key Management

### ✅ Secure Configuration

All sensitive API keys are now stored securely in the `.env` file, which is:
- ✅ **Excluded from Git** (listed in `.gitignore`)
- ✅ **Not committed to version control**
- ✅ **Environment-specific** (each deployment has its own)

### Current API Keys Location

**Configuration file:** `.env`

```env
# Google Gemini AI (for location insights)
GEMINI_API_KEY=your_key_here

# Agromonitoring API (optional)
AGROMONITORING_API_KEY=your_key_here

# Other APIs (optional)
OPENWEATHER_API_KEY=
SENTINEL_HUB_CLIENT_ID=
SENTINEL_HUB_CLIENT_SECRET=
```

### How It Works

1. **config.py** reads from `.env` using Pydantic Settings:
   ```python
   class Settings(BaseSettings):
       gemini_api_key: str = ""  # Default empty, loaded from .env
       
       class Config:
           env_file = ".env"
   ```

2. **Application** accesses keys via `settings` object:
   ```python
   from config import settings
   
   if settings.gemini_api_key:
       ai = GeminiAI(settings.gemini_api_key)
   ```

### Setup for New Deployments

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your actual API keys:
   ```bash
   GEMINI_API_KEY=AIzaSy...your_actual_key
   ```

3. **Never commit `.env` to version control!**

### ⚠️ Security Checklist

- [x] API keys stored in `.env` file
- [x] `.env` excluded from Git via `.gitignore`
- [x] `.env.example` contains placeholder values only
- [x] No hardcoded keys in source code
- [x] No keys in documentation files
- [x] Config.py uses environment variables

### What Was Fixed

**Before (❌ INSECURE):**
```python
# config.py - API key hardcoded!
gemini_api_key: str = "YOUR_API_KEY_HERE"
```

**After (✅ SECURE):**
```python
# config.py - Loaded from .env
gemini_api_key: str = ""  # Will be populated from .env file

# .env file (not in Git)
GEMINI_API_KEY=YOUR_API_KEY_HERE
```

### Best Practices

1. **Never commit** API keys or secrets to version control
2. **Use environment variables** for all sensitive configuration
3. **Rotate keys** regularly for production systems
4. **Limit API key permissions** to only what's needed
5. **Monitor API usage** for unauthorized access
6. **Use different keys** for development and production

### Files Modified for Security

- ✅ `config.py` - Removed hardcoded API key
- ✅ `.env` - Added GEMINI_API_KEY
- ✅ `.env.example` - Updated with placeholder
- ✅ `AI_INSIGHTS_GUIDE.md` - Removed hardcoded key from documentation
- ✅ `.gitignore` - Already excludes .env (verified)

### Verify Security

Check that your API key is not exposed:

```bash
# Search for API keys in tracked files (should return nothing)
git grep "AIzaSy"

# Verify .env is gitignored
git check-ignore .env
```

## Additional Security Measures

### Secret Key

The `SECRET_KEY` in `.env` is used for token signing. **Change it in production:**

```bash
# Generate a secure random key
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### CORS Configuration

Update `CORS_ORIGINS` in `.env` to only allow your actual frontend domains:

```env
CORS_ORIGINS=["https://yourdomain.com"]
```

### Production Deployment

For production:
1. Set `DEBUG=False` in `.env`
2. Use HTTPS only
3. Implement rate limiting
4. Set up API key usage monitoring
5. Use secret management services (AWS Secrets Manager, Azure Key Vault, etc.)

---

**Status:** ✅ All API keys are now securely configured!
