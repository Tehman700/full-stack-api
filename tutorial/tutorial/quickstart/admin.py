from django.contrib import admin
from quickstart.models.blog_models import BlogModel, BlogPostCommentModel, ReplyCommentModel
from quickstart.models.authentication_models import User_Data, LoginModel
from quickstart.models.reaction_models import BlogReactionModel, CommentReactionModel, ReplyReactionModel
from quickstart.models.signals_model import ActivityLog, BlogActivityMap
from quickstart.models.subscription_models import SubscribeTable, UnsubscribeTable

admin.site.register(User_Data)
admin.site.register(BlogModel)
admin.site.register(ReplyCommentModel)
admin.site.register(BlogReactionModel)
admin.site.register(CommentReactionModel)
admin.site.register(ReplyReactionModel)
admin.site.register(LoginModel)
admin.site.register(BlogPostCommentModel)
admin.site.register(SubscribeTable)
admin.site.register(UnsubscribeTable)
admin.site.register(ActivityLog)
admin.site.register(BlogActivityMap)
