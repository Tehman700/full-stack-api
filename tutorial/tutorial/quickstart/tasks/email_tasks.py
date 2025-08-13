import logging
from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_blog_notification_email(self, current_user_username, blog_title, subscribers_emails):
    try:
        if not subscribers_emails:
            logger.warning("No subscriber emails provided")
            return {"status": "warning", "message": "No subscribers to notify"}

        if not isinstance(subscribers_emails, list):
            subscribers_emails = [subscribers_emails]

        valid_emails = [email.strip() for email in subscribers_emails if email and email.strip()]
        if not valid_emails:
            logger.warning("No valid subscriber emails found")
            return {"status": "warning", "message": "No valid subscriber emails"}

        logger.info(f"Sending blog notification to {len(valid_emails)} subscribers")

        subject = f"New Blog Post by {current_user_username}"
        body = (
            f"Hello Subscriber,\n\n"
            f"You are subscribed to {current_user_username}'s blog.\n\n"
            f"A new blog has been published!\n"
            f"Title: {blog_title}\n\n"
            f"Visit your dashboard to read it.\n\n"
            f"If you wish to unsubscribe, you can send an Unsubscribe Request.\n\n"
            f"Happy reading!\n"
            f"— Tehman Hassan, CEO Blog API"
        )
        successful_emails = []
        failed_emails = []

        for email in valid_emails:
            try:
                send_mail(
                    subject=subject,
                    message=body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                    fail_silently=False,
                )
                successful_emails.append(email)
                logger.info(f"Email sent successfully to {email}")
            except Exception as email_error:
                logger.error(f"Failed to send email to {email}: {str(email_error)}")
                failed_emails.append({"email": email, "error": str(email_error)})

        result = {
            "status": "completed",
            "successful_emails": len(successful_emails),
            "failed_emails": len(failed_emails),
            "details": {
                "successful": successful_emails,
                "failed": failed_emails,
            }
        }

        logger.info(f"Email task completed: {result}")
        return result

    except Exception as exc:
        logger.error(f"Email task failed: {str(exc)}")
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            logger.error(f"Max retries exceeded for email task: {str(exc)}")
            return {"status": "failed", "error": str(exc)}

