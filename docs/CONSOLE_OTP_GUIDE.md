# Console-Based OTP Guide

## Overview

The application has been modified to use a console-based OTP approach instead of sending emails. This makes it easier to test and use the application without setting up email credentials.

## How It Works

1. When you log in with your email, password, and security answer, the system will generate an OTP
2. Instead of sending the OTP to your email, it will be printed to the console (terminal)
3. You can then copy this OTP from the console and paste it into the OTP verification page

## Example Console Output

When an OTP is generated, you'll see something like this in the console:

```
==================================================
OTP CODE FOR user@example.com: 123456
==================================================
```

## Using the OTP

1. Log in with your credentials
2. Look at the console/terminal where the application is running
3. Find the OTP code printed between the lines of equal signs (==)
4. Enter this code in the OTP verification page
5. Click "Verify OTP" to complete the login process

## Switching Back to Email-Based OTP

If you want to use actual email sending instead of the console approach:

1. Open `app.py`
2. Find the line `USE_CONSOLE_OTP = True` (around line 36)
3. Change it to `USE_CONSOLE_OTP = False`
4. Update the SMTP settings below it with your actual email credentials:
   ```python
   smtp_server = "smtp.gmail.com"  # Or your email provider's SMTP server
   smtp_port = 587                 # TLS port
   smtp_user = "your-actual-email@gmail.com"
   smtp_password = "your-actual-password"
   ```
5. Restart the application

## Troubleshooting

If you're having issues with the OTP verification:

1. Make sure you're entering the exact OTP code shown in the console
2. Check that the console output is visible and not hidden
3. If you've switched to email-based OTP, verify your SMTP settings are correct
4. Try logging out and logging in again to generate a new OTP
