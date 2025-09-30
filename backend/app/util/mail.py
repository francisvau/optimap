from datetime import timedelta
from typing import List, Tuple
from urllib.parse import quote

from app.api.dependency.mail import Mailer
from app.config import (
    LOGO_PATH,
    TEMPLATE_PATH,
    URL_PREFIX,
)
from app.model.organization import Organization
from app.schema.organization import OrganizationStatsResponse
from app.schema.user import UserResponse
from app.util.jwt import create_jwt_token


async def send_forgot_password_email(user: UserResponse, mailer: Mailer) -> None:
    """
    Sends a password reset email to the specified email address.

    This function generates a password reset token for the given email address,
    constructs a password reset URL, and sends an HTML email containing the reset
    link. The email is sent asynchronously using background tasks.

    Args:
        user (User): The user object containing user details such as email and first name.
        background_tasks (BackgroundTasks): The background tasks instance to handle
                                            asynchronous email sending.

    Returns:
        None
    """
    token = create_jwt_token(sub=user.email)
    reset_url = f"{URL_PREFIX}/auth/password/reset/{token}"

    # The replacement dictionary for the template.
    replacements = {
        "base64_url_logo": LOGO_PATH.read_text(),
        "reset_url": reset_url,
        "username": user.first_name,
    }

    # Send an email.
    await mailer.send_mail(
        template=TEMPLATE_PATH / "forgot_password.html",
        recipients=[user.email],
        subject="Optimap Prime - Password Reset Request",
        replacements=replacements,
    )


async def send_invite_to_unregistered_user_for_organization(
    email: str,
    user_role: str,
    invite_token: str,
    org: Organization,
    mailer: Mailer,
) -> None:
    """
    Sends an email to an unregistered user with a join link containing a valid invite token.

    Args:
        email: The email address of the invitee.
        user_role: The name of the role the invitee will have.
        invite_token: The unique token for the invite.
        org: The organization the invitee is being invited to.
        mailer: The mailer instance for sending the email.
    """
    # The replacement dictionary for the template
    replacements = {
        "base64_url_logo": LOGO_PATH.read_text(),
        "join_url": f"{URL_PREFIX}/auth/register?token={invite_token}&email={quote(email)}",
        "user_role": user_role,
        "organization_name": org.name,
        "organization_id": org.id,
        "organization_logo": LOGO_PATH.read_text(),
        "organization_invite_token": invite_token,
        "organization_invite_expiration_days": 7,
        "organization_invite_expiration_time": timedelta(days=7).total_seconds(),
    }

    # Send an email
    await mailer.send_mail(
        template=TEMPLATE_PATH / "join_organization_unregistered.html",
        recipients=[email],
        subject="Optimap Prime - Join Organization Request",
        replacements=replacements,
    )


async def send_invite_to_organization_mail(
    user: UserResponse,
    user_role: str,
    invite_token: str,
    org: Organization,
    mailer: Mailer,
) -> None:
    """
    Sends an email to the join link with a valid invite-token
    """
    # The replacement dictionary for the template.
    replacements = {
        "base64_url_logo": LOGO_PATH.read_text(),
        "join_url": f"{URL_PREFIX}/dashboard/organizations/join/{invite_token}",
        "username": user.first_name,
        "user_role": user_role,
        "organization_name": org.name,
        "organization_id": org.id,
        "organization_logo": LOGO_PATH.read_text(),
        "organization_invite_token": invite_token,
        "organization_invite_expiration_days": 7,
        "organization_invite_expiration_time": timedelta(days=7).total_seconds(),
    }

    # Send an email.
    await mailer.send_mail(
        template=TEMPLATE_PATH / "join_organization.html",
        recipients=[user.email],
        subject="Optimap Prime - Join Organization Request",
        replacements=replacements,
    )


async def send_verify_user_email(user: UserResponse, mailer: Mailer) -> None:
    """
    Sends a verification email to the user.

    This function generates a JWT token for the user's email, constructs a verification URL,
    reads an HTML email template, replaces placeholders in the template with actual values,
    and sends the email using FastMail in the background.

    Args:
        user (User): The user object containing user details such as email and first name.
        background_tasks (BackgroundTasks): The background tasks manager to handle asynchronous tasks.

    Returns:
        None
    """

    # The replacement dictionary for the template.
    token = create_jwt_token(user.email)
    replacements = {
        "base64_url_logo": LOGO_PATH.read_text(),
        "verification_url": f"{URL_PREFIX}/auth/verify/{token}",
        "username": user.first_name,
    }

    # Send an email.
    await mailer.send_mail(
        template=TEMPLATE_PATH / "verify_user.html",
        recipients=[user.email],
        subject="Optimap Prime - Verify User Request",
        replacements=replacements,
    )


async def send_job_complete_mail(
    user: UserResponse,
    job_id: str,
    job_success: bool,
    mailer: Mailer,
) -> None:
    """
    Sends a job completion email to the user.

    Args:
        user (User): The user object containing user details such as email and first name.
        job_id (str): The ID of the completed job.
        job_success (bool): Indicates whether the job was successful or not.
        mailer (Mailer): The mailer instance to send the email.

    Returns:
        None
    """
    replacements = {
        "base64_url_logo": LOGO_PATH.read_text(),
        "job_id": job_id,
        "username": user.first_name,
    }

    if job_success:
        replacements["job_status"] = "success"
        replacements["job_status_message"] = "Your job has been completed successfully."
    else:
        replacements["job_status"] = "error"
        replacements["job_status_message"] = (
            "Your job has failed. Please check the logs for more details."
        )

    # Send an email.
    await mailer.send_mail(
        template=TEMPLATE_PATH / "job_complete.html",
        recipients=[user.email],
        subject="Optimap Prime - Job Completed",
        replacements=replacements,
    )


async def send_combined_org_stats_mail(
    user: UserResponse,
    stats_by_org: List[Tuple[str, int, OrganizationStatsResponse]],
    mailer: Mailer,
) -> None:
    """
    Send a single email to the user with stats for all organizations they belong to.
    """
    org_stats_html = ""
    for name, org_id, stats in stats_by_org:
        org_stats_html += f"""
        <h3 style="color:#2e5577;">{name}</h3>
        <ul style="color:#555;">
            <li><strong>Mapping Jobs Started:</strong> {stats.job_count}</li>
            <li><strong>Mapping Jobs Execution Times (min/max/avg):</strong> {stats.min_execution_time}/{stats.max_execution_time}/{stats.avg_execution_time}</li>
            <li><strong>Data Processed:</strong> {round(stats.bytes / 1024 / 1024, 2)}MB</li>
            <li><a href="{URL_PREFIX}/organizations/{org_id}/dashboard">View Dashboard</a></li>
        </ul>
        <hr/>
        """

    replacements = {
        "base64_url_logo": LOGO_PATH.read_text(),
        "username": user.first_name,
        "org_stats_html": org_stats_html,
    }

    await mailer.send_mail(
        template=TEMPLATE_PATH / "combined_orgs_stats.html",
        recipients=[user.email],
        subject="Optimap Prime - Your Organization Stats",
        replacements=replacements,
    )
