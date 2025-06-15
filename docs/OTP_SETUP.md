# OTP Setup Guide

## Simple Email Configuration

To make the OTP functionality work, you need to update the SMTP settings in the `app.py` file:

1. Open `app.py`
2. Find the SMTP configuration section (around line 35)
3. Replace the placeholder values with your actual email credentials:

```python
# --- SMTP Configuration for Email Notifications ---
smtp_server = "smtp.gmail.com"  # Use your email provider's SMTP server
smtp_port = 587  # Standard TLS port
smtp_user = "your-email@gmail.com"  # Your actual email address
smtp_password = "your-password"  # Your actual email password
```

## For Gmail Users

If you're using Gmail, you have two options:

### Option 1: Use Less Secure Apps (Simplest)
1. Go to your Google Account settings
2. Search for "Less secure app access" or go directly to https://myaccount.google.com/lesssecureapps
3. Turn on "Allow less secure apps"

Note: Google may disable this option for accounts with enhanced security.

### Option 2: Use App Password (More Secure)
1. Enable 2-Step Verification on your Google account
2. Go to App Passwords: https://myaccount.google.com/apppasswords
3. Select "Mail" and "Other (Custom name)"
4. Generate the app password
5. Use this password in the SMTP configuration

## For Other Email Providers

If you're using another email provider:
1. Find their SMTP server address and port
2. Update the `smtp_server` and `smtp_port` values accordingly
3. Use your regular email and password

## Troubleshooting

If OTP emails are not being sent:

1. Check that your email and password are correct
2. Verify that your email provider allows SMTP access
3. Check if your email provider requires specific security settings
4. Try using a different email provider

For Gmail-specific issues:
- Check if you need to allow less secure apps
- Try using an app password instead of your regular password
- Make sure your Google account doesn't have additional security restrictions
