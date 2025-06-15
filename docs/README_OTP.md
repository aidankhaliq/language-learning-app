# OTP Authentication Setup Guide

## Overview
This application uses One-Time Password (OTP) authentication as a second factor for user login. The OTP is sent to the user's email address using SMTP.

## Email Configuration

### Setting Up Environment Variables
For security reasons, email credentials are stored as environment variables rather than hardcoded in the application. You need to set these environment variables before running the application:

#### On Windows:
```
set EMAIL_USER=your-email@gmail.com
set EMAIL_PASSWORD=your-app-password
```

#### On macOS/Linux:
```
export EMAIL_USER=your-email@gmail.com
export EMAIL_PASSWORD=your-app-password
```

### Using Gmail for SMTP

If you're using Gmail as your SMTP provider, follow these steps:

1. Make sure you have 2-Step Verification enabled on your Google account
2. Generate an App Password:
   - Go to your Google Account settings
   - Select "Security"
   - Under "Signing in to Google," select "App passwords"
   - Generate a new app password for "Mail" and "Other (Custom name)"
   - Use this generated password as your `EMAIL_PASSWORD` environment variable

### Using Other Email Providers

If you're using another email provider, you'll need to update the SMTP settings in `app.py`:

```python
# --- SMTP Configuration for Email Notifications ---
smtp_server = "your-smtp-server.com"  # e.g., smtp.office365.com for Outlook
smtp_port = 587  # Common ports: 587 (TLS) or 465 (SSL)
smtp_user = os.environ.get('EMAIL_USER', "your-email@example.com")
smtp_password = os.environ.get('EMAIL_PASSWORD', 'your-app-password')
```

## Troubleshooting OTP Issues

If you're experiencing issues with OTP:

1. **OTP not being sent**:
   - Check that your environment variables are set correctly
   - Verify your SMTP server and port settings
   - Make sure your email provider allows SMTP access
   - Check if your email provider requires specific security settings

2. **OTP verification failing**:
   - Make sure you're entering the exact code sent to your email
   - Check if the OTP has expired (valid for 10 minutes)
   - Try requesting a new OTP

3. **Email delivery issues**:
   - Check your spam/junk folder
   - Verify that your email provider isn't blocking automated emails
   - Try using a different email provider

## Security Considerations

- OTPs expire after 10 minutes for security
- After successful verification, OTP data is cleared from the session
- Failed verification attempts are logged
- Consider implementing rate limiting for OTP requests to prevent abuse
