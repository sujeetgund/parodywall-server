import resend
from config import settings

RESEND_API_KEY = settings.resend_api_key
RESEND_FROM_EMAIL = settings.resend_from_email

if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

def get_verification_email_html(code: str) -> str:
    """
    Returns an HTML email template for email verification,
    styled according to the ParodyWall DESIGN.md guidelines.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verify your ParodyWall email</title>
        <style>
            body {{
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                background-color: #fbfbf9;
                color: #000000;
            }}
            .container {{
                max-width: 500px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 24px;
                padding: 40px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                text-align: center;
            }}
            .logo {{
                width: 48px;
                height: 48px;
                background-color: #e60023;
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                line-height: 48px;
                margin-bottom: 24px;
            }}
            h1 {{
                font-size: 28px;
                font-weight: 700;
                margin: 0 0 12px 0;
                letter-spacing: -0.8px;
            }}
            p {{
                font-size: 16px;
                color: #62625b;
                line-height: 1.4;
                margin: 0 0 32px 0;
            }}
            .code-box {{
                background-color: #f6f6f3;
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 32px;
                font-size: 32px;
                font-weight: 700;
                letter-spacing: 8px;
                color: #000000;
            }}
            .footer {{
                font-size: 12px;
                color: #91918c;
                margin-top: 40px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">P</div>
            <h1>Check your email</h1>
            <p>Welcome to ParodyWall! Please use the following 6-digit code to verify your email address and continue.</p>
            <div class="code-box">{code}</div>
            <p style="font-size: 14px; margin-bottom: 0;">If you didn't request this, you can safely ignore this email.</p>
            <div class="footer">
                &copy; 2026 ParodyWall. All rights reserved.
            </div>
        </div>
    </body>
    </html>
    """

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# fallback to stream handler
if not logger.handlers:
    ch = logging.StreamHandler()
    logger.addHandler(ch)

def send_verification_email(to_email: str, code: str):
    logger.info(f"Attempting to send verification email to {to_email}")
    if not RESEND_API_KEY:
        logger.error(f"Mock send email to {to_email} with code {code} (No Resend API Key)")
        return
    
    html_content = get_verification_email_html(code)
    
    try:
        payload = {
            "from": RESEND_FROM_EMAIL,
            "to": to_email,
            "subject": f"{code} is your ParodyWall verification code",
            "html": html_content
        }
        logger.info(f"Sending with payload: {payload['from']} -> {payload['to']}")
        r = resend.Emails.send(payload)
        logger.info(f"Successfully sent email to {to_email}: {r}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)

