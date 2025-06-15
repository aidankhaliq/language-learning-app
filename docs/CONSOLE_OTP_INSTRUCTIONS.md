# Console OTP Instructions

## How the OTP System Works

The application now uses a console-based OTP (One-Time Password) system for authentication. This means that when you log in, a verification code will be printed to the console (terminal) where the application is running.

## Steps to Use the OTP System

1. **Log in with your credentials**
   - Enter your email, password, and security answer on the login page
   - Click "Login"

2. **Find the OTP in the console**
   - Look at the terminal/console where the application is running
   - You'll see a message that looks like this:
   ```
   ==================================================
   OTP CODE FOR your-email@example.com: 123456
   ==================================================
   ```
   - The 6-digit number (e.g., 123456) is your OTP

3. **Enter the OTP on the verification page**
   - Type the 6-digit code into the OTP field
   - Click "Verify OTP"

4. **If you can't see the OTP**
   - Click the "Resend OTP" link on the verification page
   - A new OTP will be generated and printed to the console
   - Look for the new OTP in the console

## Troubleshooting

If you're having issues with the OTP verification:

1. **Make sure you're entering the correct OTP**
   - The OTP is a 6-digit number
   - Enter exactly what you see in the console
   - Don't include any spaces or other characters

2. **Check the console output**
   - The OTP is printed between lines of equal signs (=)
   - Make sure the console window is visible and not minimized
   - Scroll up if necessary to find the most recent OTP

3. **Try resending the OTP**
   - Click the "Resend OTP" link on the verification page
   - A new OTP will be generated and printed to the console
   - Use this new OTP instead of the old one

4. **Restart the application if necessary**
   - If you're still having issues, try restarting the application
   - Log in again to generate a new OTP

## Why Console-Based OTP?

The console-based OTP approach is used because:

1. It works reliably without requiring email configuration
2. It's easier to test and debug
3. It avoids issues with email delivery, spam filters, etc.

In a production environment, you would typically configure the application to send OTPs via email or SMS instead of printing them to the console.
