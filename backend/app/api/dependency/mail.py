import os
from pathlib import Path
from typing import Annotated, Any

from fastapi import BackgroundTasks, Depends
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from app.exceptions import InvalidConfiguration

SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PW")


class Mailer:
    """
    A class to handle email sending using FastAPI Mail.
    This class provides methods to configure the SMTP settings, send emails,
    and manage email templates.
    """

    def __init__(self, bg: BackgroundTasks | None = None) -> None:
        """Initialize the Mailer with background tasks."""
        self.bg = bg
        if not all([SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD]):
            raise InvalidConfiguration(
                "Missing SMTP configuration. Ensure all required environment variables are set."
            )

    @property
    def config(self) -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=SMTP_USERNAME,
            MAIL_PASSWORD=SMTP_PASSWORD,
            MAIL_FROM=SMTP_USERNAME,
            MAIL_PORT=SMTP_PORT,
            MAIL_SERVER=SMTP_SERVER,
            MAIL_FROM_NAME=SMTP_USERNAME,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True,
            TIMEOUT=60,
        )

    async def send_mail(
        self,
        recipients: list[str],
        subject: str,
        template: Path,
        replacements: dict[str, Any] | None = None,
    ) -> None:
        """
        Sends an email to the specified recipients using a provided HTML template.

        Args:
            recipients (list[str]): A list of email addresses to send the email to.
            subject (str): The subject line of the email.
            bg (BackgroundTasks): A FastAPI BackgroundTasks instance to handle sending the email asynchronously.
            template (Path): The file path to the HTML template for the email body.
            replacements (dict[str, Any] | None, optional): A dictionary of placeholder keys and their corresponding
                replacement values to be substituted in the HTML template. Defaults to None.
        """
        # Read the HTML template file
        html_template = template.read_text(encoding="utf-8")

        # Replace placeholders in the HTML template with actual values
        if replacements:
            for key, value in replacements.items():
                html_template = html_template.replace(f"{{{{ {key} }}}}", str(value))

        # Create a message schema for the email
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=html_template,
            subtype=MessageType.html,
        )

        # Send the email in the background
        mailer = FastMail(self.config)

        if self.bg:
            self.bg.add_task(mailer.send_message, message)
        else:
            await mailer.send_message(message)


def get_mailer(bg: BackgroundTasks) -> Mailer:
    """
    Dependency to get a Mailer instance.

    Args:
        bg (BackgroundTasks): FastAPI BackgroundTasks instance to handle asynchronous tasks.

    Returns:
        Mailer: An instance of the Mailer class.
    """
    return Mailer(bg=bg)


MailerDep = Annotated[Mailer, Depends(get_mailer)]
