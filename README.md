# Medical Report Analyzer - Backend

Flask-based REST API for medical report analysis.

## 🚀 Deployment on Render

### Prerequisites
- A Render account (https://render.com)
- Gemini API key from Google AI Studio

### Step-by-Step Deployment

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial backend commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create New Web Service on Render**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select this backend repository

3. **Configure the Service**
   - **Name**: `medical-analyzer-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free (or paid for better performance)

4. **Add Environment Variables**
   In the Render dashboard, add these environment variables:
   - `SECRET_KEY`: Generate a secure random string
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `FRONTEND_URL`: Your Vercel frontend URL (add after deploying frontend)
   - `PYTHON_VERSION`: `3.11.0`

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your backend
   - Copy the backend URL (e.g., `https://your-backend.onrender.com`)

## 📝 Environment Variables

Copy `.env.example` to `.env` for local development:

```bash
cp .env.example .env
```

Then edit `.env` with your actual values.

## 🧪 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py
```

Server will run on `http://localhost:5000`

## 📡 API Endpoints

### Authentication
- `POST /api/signup` - Create new user account
- `POST /api/login` - User login
- `POST /api/logout` - User logout
- `GET /api/user` - Get current user info

### Report Analysis
- `POST /api/analyze` - Analyze single medical report
- `POST /api/analyze-multiple` - Analyze multiple reports
- `POST /api/find-hospitals` - Find nearby hospitals
- `POST /api/chatbot` - Chat with AI assistant

### Health Check
- `GET /api/health` - Check if API is running

## 🔧 Configuration Notes

### CORS Setup
The backend is configured to accept requests from:
- `http://localhost:3000` (Local React dev)
- `http://localhost:5173` (Local Vite dev)
- Your production Vercel frontend URL

Update the CORS origins in `app.py` after deploying your frontend.

### Session Management
- Sessions use secure cookies
- `SESSION_COOKIE_SAMESITE = 'None'` for cross-origin requests
- `SESSION_COOKIE_SECURE = True` for HTTPS

### File Uploads
- Maximum file size: 16MB
- Allowed formats: PDF, PNG, JPG, JPEG, TXT
- Files are temporarily stored and deleted after processing

## 🐛 Troubleshooting

### Render-Specific Issues

1. **Cold Starts**: Free tier services sleep after 15 minutes of inactivity
   - First request may take 30-60 seconds
   - Consider using a paid plan for always-on service

2. **Database Persistence**: SQLite database resets on each deploy
   - Consider upgrading to PostgreSQL for production
   - Add persistent disk storage in Render settings

3. **Environment Variables**: Make sure all required env vars are set
   - Check Render dashboard → Environment
   - Restart service after changing env vars

4. **Build Failures**: Check Render logs
   - Common issue: Missing system dependencies for pytesseract
   - Add `apt-packages` in render.yaml if needed

## 📦 Dependencies

- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-origin resource sharing
- scikit-learn - Machine learning
- pandas - Data manipulation
- PyPDF2 - PDF processing
- google-generativeai - Gemini AI integration
- gunicorn - Production server

## 🔐 Security Notes

1. **Change SECRET_KEY** in production
2. **Secure your Gemini API key**
3. **Enable HTTPS** (automatic on Render)
4. **Update CORS origins** to your actual frontend domain
5. **Use environment variables** for all sensitive data

## 📞 Support

For issues related to:
- Backend API: Check Render logs
- Gemini API: Verify API key and quota
- Database: Check SQLite file permissions

## 🎯 Next Steps

After backend deployment:
1. Copy your Render backend URL
2. Use it in the frontend configuration
3. Update CORS origins with your Vercel URL
4. Test all API endpoints
