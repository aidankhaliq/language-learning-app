# Deployment Guide for Render

## Pre-deployment Changes Made

The following changes have been made to prepare the codebase for Render deployment:

### 1. Database Configuration
- **Fixed database path**: Now uses `/data/database.db` on Render's persistent storage
- **Local development support**: Falls back to local `database.db` when not on Render
- **Auto-directory creation**: Ensures database directory exists before connecting

### 2. Environment Variables
- **Removed hardcoded API keys**: GEMINI_API_KEY now uses environment variables
- **Removed hardcoded email credentials**: SMTP settings now use environment variables
- **Secure defaults**: Console OTP enabled by default for development

### 3. Render Configuration
- **Updated render.yaml**: Optimized for production deployment
- **Persistent storage**: Configured to use `/data` mount for database
- **Proper resource allocation**: 2 workers, 4 threads, 300s timeout

### 4. Dependencies
- **Fixed requirements.txt**: Pinned specific versions for pandas and numpy
- **Added email-validator**: For better email validation support

## Deployment Steps

### Step 1: Set Up Repository
1. Ensure all files are committed to your Git repository
2. The `.gitignore` file will protect sensitive data

### Step 2: Create Render Service
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Render will automatically detect the `render.yaml` file

### Step 3: Configure Environment Variables
In Render's environment variables section, set:

**Required:**
- `GEMINI_API_KEY`: Your Google Gemini API key
- `SMTP_USER`: Your Gmail address (for OTP emails)
- `SMTP_PASSWORD`: Your Gmail app password

**Optional:**
- `USE_CONSOLE_OTP`: Set to `false` to enable email OTP (default: `true`)

### Step 4: Deploy
1. Click "Create Web Service"
2. Render will build and deploy automatically
3. Monitor build logs for any issues

## Health Check
Once deployed, you can check the health at: `https://your-app-name.onrender.com/health`

## Troubleshooting

### Database Issues
- Check if persistent disk is properly mounted at `/data`
- Verify database initialization in build logs
- Use health check endpoint to test database connectivity

### Email Issues
- Ensure Gmail app passwords are used (not regular passwords)
- Verify SMTP environment variables are set
- Test with console OTP first (`USE_CONSOLE_OTP=true`)

### API Issues
- Verify GEMINI_API_KEY is correctly set
- Check API quota and usage limits
- Review application logs for API errors

## Post-Deployment
1. Create admin account via the health check endpoint
2. Test all major functionality
3. Monitor application logs for any issues
4. Set up uptime monitoring if needed

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| FLASK_SECRET_KEY | Yes | Auto-generated | Flask session secret |
| GEMINI_API_KEY | Yes | None | Google Gemini API key |
| SMTP_USER | No | None | Gmail address for emails |
| SMTP_PASSWORD | No | None | Gmail app password |
| USE_CONSOLE_OTP | No | true | Use console OTP instead of email |
| FLASK_ENV | No | production | Flask environment |
| PORT | No | 10000 | Application port | 