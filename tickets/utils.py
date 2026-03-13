from django.core.mail import send_mail
from django.conf import settings


def send_ticket_email(user, subject, message):
    """
    Safely send ticket notification email.
    Prevents crashes if email is missing or invalid.
    """

    # No user
    if not user:
        return

    # No email or blank email
    email = (user.email or "").strip()
    if not email:
        return

    # Respect notification preference
    if hasattr(user, "email_notifications") and not user.email_notifications:
        return

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        # Prevent breaking ticket workflow
        print("Email sending failed:", e)