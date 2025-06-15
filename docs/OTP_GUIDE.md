# OTP Guide

## Current Setup: Console-Based OTP

The application is currently configured to use a console-based OTP approach. This means that instead of sending verification codes to your email, the codes will be printed to the console (terminal) where the application is running.

### How to Use Console-Based OTP

1. When you log in with your credentials, the system will generate an OTP
2. The OTP will be printed to the console where the application is running
3. Look for output that looks like this:
   ```
   ==================================================
   OTP CODE FOR your-email@example.com: 123456
   ==================================================
   ```
4. Enter this code in the OTP verification page to complete your login

## Switching to Email-Based OTP

If you want to receive OTP codes via email instead of seeing them in the console:

1. Open `app.py`
2. Find the line `USE_CONSOLE_OTP = True` (around line 35)
3. Change it to `USE_CONSOLE_OTP = False`
4. Update the SMTP settings below it with your actual email credentials:
   ```python
   smtp_server = "smtp.gmail.com"
   smtp_port = 587
   smtp_user = "your-actual-email@gmail.com"
   smtp_password = "your-actual-password"
   ```
5. Restart the application

### Gmail-Specific Setup

If you're using Gmail, you might need to:

1. Allow less secure apps:
   - Go to your Google Account → Security
   - Turn on "Less secure app access"

2. Or use an app password (if you have 2-factor authentication):
   - Go to your Google Account → Security → App passwords
   - Generate a password for "Mail" and "Other (Custom name)"
   - Use this password in your configuration

## Troubleshooting

If you're having issues with the OTP verification:

1. For console-based OTP:
   - Make sure you're entering the exact code shown in the console
   - Check that the console output is visible and not hidden

2. For email-based OTP:
   - Check your spam/junk folder
   - Verify your SMTP settings are correct
   - Try using a different email provider

3. General issues:
   - Try logging out and logging in again to generate a new OTP
   - Restart the application
