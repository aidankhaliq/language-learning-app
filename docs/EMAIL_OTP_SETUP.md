# Email OTP Setup Guide

## Overview

The application is now configured to send verification codes (OTPs) via email. This guide will help you set up the email sending functionality properly.

## Email Configuration

To make the email OTP functionality work, you need to update the SMTP settings in the `app.py` file:

1. Open `app.py`
2. Find the SMTP configuration section (around line 35-41)
3. Replace the placeholder values with your actual email credentials:

```python
# SMTP settings for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS port for Gmail
smtp_user = "your-actual-email@gmail.com"  # Your email address
smtp_password = "your-actual-password"     # Your email password
```

## Gmail-Specific Setup

If you're using Gmail, you have two options:

### Option 1: Use App Passwords (Recommended for accounts with 2FA)

1. Make sure 2-Step Verification is enabled on your Google account
   - Go to your Google Account → Security → 2-Step Verification

2. Generate an App Password:
   - Go to your Google Account → Security → App passwords
   - Select "Mail" as the app and "Other (Custom name)" as the device
   - Enter a name like "Language Learning App"
   - Click "Generate"
   - Google will display a 16-character password
   
3. Use this app password in your SMTP configuration:
   ```python
   smtp_password = "your-16-character-app-password"  # No spaces
   ```

### Option 2: Allow Less Secure Apps (For accounts without 2FA)

1. Go to your Google Account → Security
2. Turn on "Less secure app access"
3. Use your regular Gmail password in the SMTP configuration

**Note**: Google may disable this option for accounts with enhanced security features.

## Other Email Providers

For other email providers, you'll need to:

1. Find their SMTP server address and port
2. Update the configuration accordingly:

```python
# Example for Outlook/Hotmail
smtp_server = "smtp-mail.outlook.com"
smtp_port = 587
smtp_user = "your-outlook-email@hotmail.com"
smtp_password = "your-outlook-password"
```

Common SMTP servers:
- Outlook/Hotmail: smtp-mail.outlook.com (port 587)
- Yahoo: smtp.mail.yahoo.com (port 587)
- ProtonMail: smtp.protonmail.ch (port 587)

## Troubleshooting

If you're experiencing issues with email sending:

1. **Authentication Errors**:
   - Double-check your email and password
   - For Gmail, make sure you're using an app password if 2FA is enabled
   - Check if your email provider requires specific security settings

2. **Connection Errors**:
   - Verify the SMTP server address and port
   - Check if your network blocks outgoing SMTP connections
   - Try a different email provider

3. **Email Not Received**:
   - Check your spam/junk folder
   - Verify that your email provider isn't blocking automated emails
   - Try using a different email address

4. **Debug Mode**:
   - If you're still having issues, you can temporarily switch to console mode:
   ```python
   USE_CONSOLE_OTP = True  # Set to True to print OTP to console
   ```

## Security Considerations

- Never commit your email credentials to version control
- Consider using environment variables for sensitive information
- Regularly update your passwords
- Use app passwords instead of your main password when possible
