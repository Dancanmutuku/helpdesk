# tickets/utils.py
from django.core.mail import send_mail
from django.conf import settings


def send_ticket_email(user, subject, message):
    """
    Send an email notification to a user regarding ticket updates.

    Respects the user's email and optional `email_notifications` preference.
    """
    if not user or not user.email:
        return

    # Optional: respect user preference for notifications
    if hasattr(user, "email_notifications") and not user.email_notifications:
        return

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,  # avoid breaking the view if email fails
    )