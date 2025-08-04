from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from quickstart.models.subscription_models import SubscribeTable, UnsubscribeTable
from quickstart.serializers.subscription_serializers import SubscribeSerializer, UnsubscribeSerializer
from quickstart.signals import log_unsubscribe_activity, log_subscription_activity
from quickstart.utils.response_handler import ResponseHandler


class SubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        current_user = request.user

        try:
            to_be_subscribed = User.objects.get(username=pk)
        except User.DoesNotExist:
            return ResponseHandler.error(
                message="No Blogs written by this Author",
                code=1
            )

        if to_be_subscribed.profile.role.lower() != 'writer':
            return ResponseHandler.error(
                message="You can only subscribe to a writer",
                code=1
            )

        if current_user.username == pk:
            return ResponseHandler.error(
                message="You cannot Subscribe Yourself",
                code=1
            )

        existing_active_subscriber = SubscribeTable.objects.filter(
            subscriber=current_user,
            author=to_be_subscribed,
            is_active=True
        ).first()

        if existing_active_subscriber:
            return ResponseHandler.error(
                message=f'You are already subscribed to {to_be_subscribed.username}',
                code=1
            )

        # Create subscription
        subscription = SubscribeTable.objects.create(
            subscriber=current_user,
            author=to_be_subscribed,
            is_active=True
        )

        log_subscription_activity(current_user, to_be_subscribed.username, subscription.id)

        serializer = SubscribeSerializer(subscription)
        return ResponseHandler.success(
            message=f'Successfully subscribed to {to_be_subscribed.username}',
            data=serializer.data,
            code=0
        )

    def http_method_not_allowed(self, request, *args, **kwargs):
        return ResponseHandler.error(
            message='Only POST method is allowed for subscription.',
            code=-1
        )


class UnsubscribeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        current_user = request.user

        try:
            to_be_unsubscribed = User.objects.get(username=pk)
        except User.DoesNotExist:
            return ResponseHandler.error(
                message="No Blogs written by this Author",
                code=1
            )

        active_subscription = SubscribeTable.objects.filter(
            subscriber=current_user,
            author=to_be_unsubscribed,
            is_active=True
        ).first()

        if not active_subscription:
            return ResponseHandler.error(
                message=f'You are not subscribed to {to_be_unsubscribed.username}. First Subscribe',
                code=1
            )

        with transaction.atomic():
            # Mark old subscription inactive
            active_subscription.is_active = False
            active_subscription.save()

            # Create Unsubscribe record
            unsubscribe_record = UnsubscribeTable.objects.create(
                subscriber=current_user,
                author=to_be_unsubscribed,
                original_subscription=active_subscription,
            )

            log_unsubscribe_activity(current_user, to_be_unsubscribed.username, unsubscribe_record.id)

        serializer = UnsubscribeSerializer(unsubscribe_record)
        return ResponseHandler.success(
            message=f'Successfully unsubscribed from {to_be_unsubscribed.username}.',
            data=serializer.data,
            code=0
        )

    def http_method_not_allowed(self, request, *args, **kwargs):
        return ResponseHandler.error(
            message='Only POST method is allowed for Unsubscription.',
            code=-1
        )
