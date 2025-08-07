from datetime import datetime
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from quickstart.models.authentication_models import User_Data
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, ReplyCommentModel
from quickstart.models.reaction_models import ReplyReactionModel, BlogReactionModel, CommentReactionModel
from quickstart.models.signals_model import ActivityLog, BlogActivityMap


# === Utility Functions ===
def get_current_time():
    now = datetime.now()
    return now.strftime("%B %d, %Y at %I:%M %p")

def track_activity(blog_id, activity_id):
    try:
        blog = BlogModel.objects.get(id=blog_id)
        activity = ActivityLog.objects.get(id=activity_id)
        blog_map, created = BlogActivityMap.objects.get_or_create(blog=blog)
        blog_map.activity_logs.add(activity)
    except (BlogModel.DoesNotExist, ActivityLog.DoesNotExist):
        pass  # Optional: log error or raise

# === USER REGISTERED ===
@receiver(post_save, sender=User_Data)
def user_register_handler(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.user,
            action='User registered',
            model_name=sender.__name__,
            instance_id=instance.id,
            description=f"{instance.user}! Account created successfully at {get_current_time()}"
        )

# === BLOG CREATED AND UPDATED ===
@receiver(post_save, sender=BlogModel)
def blog_created_handler(sender, instance, created, **kwargs):
    if created:
        action = 'Blog created'
        description = f"Blog '{instance.title}' was created at {get_current_time()} by '{instance.user}'"
    else:
        action = 'Blog updated'
        description = f"Blog '{instance.title}' was edited at {get_current_time()} by '{instance.user}'"

    activity = ActivityLog.objects.create(
        user=instance.user,
        action=action,
        model_name=sender.__name__,
        instance_id=instance.id,
        description=description
    )
    track_activity(instance.id, activity.id)


# === COMMENT CREATED AND UPDATED ===
@receiver(post_save, sender=BlogPostCommentModel)
def comment_created_handler(sender, instance, created, **kwargs):
    blog = instance.blog
    if created:
        action = 'Comment created'
        description = f"{instance.user}! Commented on blogpost '{blog.title}' at {get_current_time()}"
    else:
        action = 'Comment updated'
        description = f"{instance.user}! Updated comment on blogpost '{blog.title}' at {get_current_time()}"

    activity = ActivityLog.objects.create(
        user=instance.user,
        action=action,
        model_name=sender.__name__,
        instance_id=instance.id,
        description=description
    )
    track_activity(blog.id, activity.id)

# === REPLY CREATED AND UPDATED ===
@receiver(post_save, sender=ReplyCommentModel)
def reply_created_handler(sender, instance, created, **kwargs):
    blog = instance.comment.blog
    if created:
        action = 'Reply created'
        description = f"{instance.user}! Replied to comment on '{blog.title}' at {get_current_time()}"
    else:
        action = 'Reply updated'
        description = f"{instance.user}! Updated reply on '{blog.title}' at {get_current_time()}"

    activity = ActivityLog.objects.create(
        user=instance.user,
        action=action,
        model_name=sender.__name__,
        instance_id=instance.id,
        description=description
    )
    track_activity(blog.id, activity.id)

# === BLOG REACTIONS (LIKE/DISLIKE) ===
@receiver(post_save, sender=BlogReactionModel)
def blog_reaction_handler(sender, instance, created, **kwargs):
    blog = instance.blog
    reaction_type = "liked" if instance.reaction == "like" else "disliked"
    if created:
        action = f'Blog {reaction_type}'
        description = f"{instance.user} {reaction_type} blog '{blog.title}' at {get_current_time()}"
    else:
        action = f'Blog reaction changed'
        description = f"{instance.user} changed reaction to {reaction_type} on '{blog.title}' at {get_current_time()}"

    activity = ActivityLog.objects.create(
        user=instance.user,
        action=action,
        model_name=sender.__name__,
        instance_id=instance.id,
        description=description
    )
    track_activity(blog.id, activity.id)

# === COMMENT REACTIONS ===
@receiver(post_save, sender=CommentReactionModel)
def comment_reaction_handler(sender, instance, created, **kwargs):
    blog = instance.comment.blog
    reaction_type = "liked" if instance.reaction == "like" else "disliked"
    if created:
        action = f'Comment {reaction_type}'
        description = f"{instance.user} {reaction_type} comment on '{blog.title}' at {get_current_time()}"
    else:
        action = f'Comment reaction changed'
        description = f"{instance.user} changed reaction to {reaction_type} on comment at {get_current_time()}"

    activity = ActivityLog.objects.create(
        user=instance.user,
        action=action,
        model_name=sender.__name__,
        instance_id=instance.id,
        description=description
    )
    track_activity(blog.id, activity.id)

# === REPLY REACTIONS ===
@receiver(post_save, sender=ReplyReactionModel)
def reply_reaction_handler(sender, instance, created, **kwargs):
    blog = instance.reply.comment.blog
    reaction_type = "liked" if instance.reaction == "like" else "disliked"
    if created:
        action = f'Reply {reaction_type}'
        description = f"{instance.user} {reaction_type} reply on '{blog.title}' at {get_current_time()}"
    else:
        action = f'Reply reaction changed'
        description = f"{instance.user} changed reaction to {reaction_type} on reply at {get_current_time()}"

    activity = ActivityLog.objects.create(
        user=instance.user,
        action=action,
        model_name=sender.__name__,
        instance_id=instance.id,
        description=description
    )
    track_activity(blog.id, activity.id)

# === BLOG DELETION ONLY CHANGES STATUS TECHNICALLY DOESN'T DELETES THE ACTIVITY ====
@receiver(pre_delete, sender=BlogModel)
def blog_delete_handler(sender, instance, **kwargs):
    blog_id = instance.id
    description = f"Blog '{instance.title}' was deleted at {get_current_time()} by '{instance.user}'"

    # Create deletion log (status = 2)
    activity = ActivityLog.objects.create(
        user=instance.user,
        action='Blog deleted',
        model_name=sender.__name__,
        instance_id=instance.id,
        description=description,
        status=2
    )

    # Track the deletion log for the function to highlight that part
    track_activity(blog_id, activity.id)

    # Just updates status related to that blog, but don't delete from activity log
    try:
        activity_map = BlogActivityMap.objects.get(blog_id=blog_id)
        related_logs = activity_map.activity_logs.exclude(id=activity.id)
        related_logs.update(status=2)
    except BlogActivityMap.DoesNotExist:
        pass  # IF NOTHING FOUND
