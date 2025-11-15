# Deployment Guide

## 🚀 Deploying PDF Editor to Production

This guide covers deploying the PDF Editor application to various platforms.

---

## Option 1: Vercel (Frontend Only - Recommended for Start)

**Best for**: Quick deployment, automatic CI/CD, free tier available

### Steps:

1. **Install Vercel CLI** (if not already installed):
```bash
npm install -g vercel
```

2. **Login to Vercel**:
```bash
vercel login
```

3. **Deploy Frontend**:
```bash
cd frontend
vercel
```

4. **Follow prompts**:
   - Set up and deploy: Yes
   - Which scope: Your account
   - Link to existing project: No
   - Project name: pdf-editor-oss
   - Directory: `./` (current directory)
   - Override settings: No

5. **Set Environment Variables** in Vercel Dashboard:
   - `VITE_API_URL` = Your backend URL (see backend deployment below)

6. **Production Deployment**:
```bash
vercel --prod
```

### ✅ Result:
Frontend will be live at: `https://pdf-editor-oss.vercel.app`

---

## Option 2: Railway (Backend) + Vercel (Frontend)

**Best for**: Full-stack deployment with Python backend

### Backend Deployment (Railway):

1. **Install Railway CLI**:
```bash
npm install -g @railway/cli
```

2. **Login to Railway**:
```bash
railway login
```

3. **Deploy Backend**:
```bash
cd backend-python
railway init
railway up
```

4. **Set Environment Variables** in Railway Dashboard:
   - `CORS_ORIGINS` = `https://your-frontend-domain.vercel.app`
   - `PORT` = `8080`
   - `DEBUG` = `false`
   - `LOG_LEVEL` = `INFO`

5. **Get Backend URL**:
```bash
railway domain
```

### Frontend Deployment (Vercel):

Follow Option 1 steps, but set:
- `VITE_API_URL` = Your Railway backend URL

---

## Option 3: Render (Full Stack)

**Best for**: Simplified full-stack deployment

### Steps:

1. **Create `render.yaml`** in project root (already configured)

2. **Connect GitHub** to Render:
   - Go to https://dashboard.render.com
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will auto-detect and deploy both services

3. **Set Environment Variables** in Render Dashboard:

**Backend Service**:
- `CORS_ORIGINS` = Your frontend URL
- `DEBUG` = `false`
- `PORT` = `8080`

**Frontend Service**:
- `VITE_API_URL` = Your backend URL

---

## Option 4: Docker + Any Cloud Provider

**Best for**: Maximum control and portability

### Steps:

1. **Build Docker Images**:

**Frontend**:
```bash
cd frontend
docker build -t pdf-editor-frontend .
```

**Backend**:
```bash
cd backend-python
docker build -t pdf-editor-backend .
```

2. **Run Containers**:
```bash
# Backend
docker run -d -p 8080:8080 \
  -e CORS_ORIGINS="http://localhost:3000" \
  pdf-editor-backend

# Frontend
docker run -d -p 3000:80 \
  -e VITE_API_URL="http://localhost:8080" \
  pdf-editor-frontend
```

3. **Deploy to Cloud**:
   - **AWS ECS**: Push images to ECR, create task definitions
   - **Google Cloud Run**: `gcloud run deploy`
   - **Azure Container Instances**: `az container create`
   - **DigitalOcean App Platform**: Connect GitHub repo

---

## Environment Variables Reference

### Frontend (.env)
```bash
VITE_API_URL=https://your-backend-url.com
```

### Backend (.env)
```bash
# Application
APP_NAME="PDF Editor API"
APP_VERSION="2.0.0"
DEBUG=false

# Server
HOST=0.0.0.0
PORT=8080

# CORS - IMPORTANT for production!
CORS_ORIGINS="https://your-frontend-domain.com"
CORS_ALLOW_CREDENTIALS=true

# File Storage
MAX_UPLOAD_SIZE=104857600  # 100MB
MAX_MERGE_FILES=50
MAX_PDF_PAGES=5000

# Logging
LOG_LEVEL=INFO

# Security
ENABLE_RATE_LIMITING=true
RATE_LIMIT_PER_MINUTE=60

# Cleanup
AUTO_CLEANUP_ENABLED=true
CLEANUP_INTERVAL_MINUTES=5
FILE_RETENTION_MINUTES=5
```

---

## Post-Deployment Checklist

- [ ] Frontend loads and displays correctly
- [ ] Backend API health check returns 200: `/health`
- [ ] CORS configured correctly (test file upload)
- [ ] Environment variables set properly
- [ ] File upload/download working
- [ ] All PDF operations functional
- [ ] SSL/HTTPS enabled
- [ ] Domain configured (if using custom domain)
- [ ] Monitoring/logging set up
- [ ] Backup strategy in place

---

## Troubleshooting

### CORS Errors
**Problem**: `Access-Control-Allow-Origin` errors
**Solution**: Update `CORS_ORIGINS` in backend to match frontend URL exactly

### File Upload Fails
**Problem**: Files not uploading
**Solution**: Check `MAX_UPLOAD_SIZE` and cloud provider file size limits

### Backend Not Responding
**Problem**: API calls timeout
**Solution**:
- Check backend logs
- Verify PORT environment variable
- Ensure health endpoint works: `/health`

### Build Failures
**Problem**: Vercel/Railway build fails
**Solution**:
- Check build logs for missing dependencies
- Verify `requirements.txt` (backend) and `package.json` (frontend)
- Ensure Python 3.11+ for backend

---

## Performance Optimization

### Frontend:
- Enable Vercel CDN (automatic)
- Configure caching headers
- Lazy load PDF viewer components

### Backend:
- Enable file cleanup scheduler
- Configure rate limiting
- Use production ASGI server (uvicorn with workers)

---

## Scaling Considerations

### When Traffic Grows:
1. **Enable Auto-scaling** in your cloud provider
2. **Add Redis** for session management
3. **Use S3/Cloud Storage** for file uploads instead of local filesystem
4. **Add CDN** for static assets
5. **Database** if you need persistence (currently stateless)
6. **Load Balancer** for multiple backend instances

---

## Need Help?

- Check the logs first
- Review environment variables
- Test locally with production config
- Open an issue on GitHub

Happy deploying! 🚀
