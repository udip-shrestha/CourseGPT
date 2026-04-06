from fastapi import HTTPException, status
from email.message import EmailMessage
import smtplib
import ssl

from API.Util.decorators import clean_service


class GmailService:
    """
    Handles outbound email delivery through Gmail gmail.
    """

    def __init__(
        self,
        gmail_host: str,
        gmail_port: int,
        gmail_username: str,
        gmail_password: str,
        gmail_from_email: str,
        gmail_from_name: str
    ):
        self.gmail_host = gmail_host
        self.gmail_port = gmail_port
        self.gmail_username = gmail_username
        self.gmail_password = gmail_password
        self.gmail_from_email = gmail_from_email
        self.gmail_from_name = gmail_from_name


    def _send_email(self, to_email: str, subject: str, body: str, html_body: str | None = None):
        """
        Send an email to a single recipient using SMTP (Gmail).

        ⚠️ Note:
        When using Gmail SMTP, there are sending limits (~500 emails/day for personal accounts).
        This method is intended for low-volume use (e.g., notifications, testing), not bulk emailing.
        """
        for field in [to_email, subject, body]:
            if not field.strip():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field} is required.")
        
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = f"{self.gmail_from_name} <{self.gmail_from_email}>"
        message["To"] = to_email
        message.set_content(body)
        if html_body:
            message.add_alternative(html_body, subtype="html")

        context = ssl.create_default_context()
        with smtplib.SMTP(self.gmail_host, self.gmail_port) as gmail:
            gmail.ehlo()
            gmail.starttls(context=context)
            gmail.ehlo()
            gmail.login(self.gmail_username, self.gmail_password)
            gmail.send_message(message)


    @clean_service
    def send_password_reset_email(self, to_email: str, reset_code: str):
        """
        Send a password reset email with a 6-digit code.
        """
        subject = "Your CourseGPT password reset code"

        body = (
            "We received a request to reset your password.\n\n"
            f"Your password reset code is: {reset_code}\n\n"
            "This code expires in 10 minutes.\n\n"
            "If you did not request this, you can ignore this email.\n\n"
            "Best,\n"
            "CourseGPT"
        )

        html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #111827;">
                    <p>We received a request to reset your password.</p>

                    <p>Your password reset code is:</p>

                    <div style="
                        display: inline-block;
                        padding: 12px 20px;
                        margin: 8px 0 16px 0;
                        font-size: 24px;
                        font-weight: bold;
                        letter-spacing: 4px;
                        background-color: #f3f4f6;
                        border: 1px solid #d1d5db;
                        border-radius: 8px;
                    ">
                        {reset_code}
                    </div>

                    <p>This code expires in <strong>10 minutes</strong>.</p>

                    <p>If you did not request this, you can ignore this email.</p>

                    <p>
                        Best,<br>
                        CourseGPT
                    </p>
                </body>
            </html>
            """

        self._send_email(to_email=to_email, subject=subject, body=body, html_body=html_body)

