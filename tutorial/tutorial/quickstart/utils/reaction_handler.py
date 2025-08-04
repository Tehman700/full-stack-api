from django.db.models import Count, Q
from quickstart.utils.response_handler import ResponseHandler
"""
Below is my Custom Logic for the Likes, Dislikes,of every blog, comment or reply
This handles all the logic very efficiently and A simple correct POST request handles it very easily

                /api/blog_or_comment_or_reply/like_or_dislike/id_of_specific

"""

def handle_reaction_logic(current_user, target_object, action, reaction_model, reaction_field_name, object_name):
    # Check if user is trying to dislike their own content
    if action == 'dislike' and target_object.user == current_user:
        return ResponseHandler.error(
            message=f'You cannot dislike your own {object_name}',
            code=2
        )
    # Get or create the reaction record
    reaction_filter = {
        'user': current_user,
        reaction_field_name: target_object
    }

    reaction, created = reaction_model.objects.get_or_create(
        **reaction_filter,
        defaults={'reaction': action}
    )


    if not created:
        if reaction.reaction == action:
            # User is removing their reaction
            reaction.delete()
            message = f"Your {action} has been removed from this {object_name}."
        else:
            # User is changing their reaction
            reaction.reaction = action
            reaction.save()
            message = f"Your reaction has been changed to {action} for this {object_name}."
    else:
        message = f"You have {action}d this {object_name}."

    # Update the target object's like/dislike counts
    update_reaction_counts(target_object, reaction_model, reaction_field_name)

    return ResponseHandler.success(
        message=message,
        code=0
    )


def update_reaction_counts(target_object, reaction_model, reaction_field_name):
    """
    Update the like/dislike counts on the target object based on actual reactions
    """
    # Count actual reactions
    reaction_filter = {reaction_field_name: target_object}

    reaction_counts = reaction_model.objects.filter(**reaction_filter).aggregate(
        likes=Count('id', filter=Q(reaction='like')),
        dislikes=Count('id', filter=Q(reaction='dislike'))
    )

    # Update the target object
    target_object.likes = reaction_counts['likes'] or 0
    target_object.dislikes = reaction_counts['dislikes'] or 0
    target_object.save(update_fields=['likes', 'dislikes'])



def extract_action_from_path(request_path):
    parts = request_path.strip('/').split('/')
    return parts[2]  # index 2 corresponds to 'like' or 'dislike'