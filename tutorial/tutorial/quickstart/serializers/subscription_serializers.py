from rest_framework import serializers
from quickstart.models.subscription_models import SubscribeTable, UnsubscribeTable


class SubscribeSerializer(serializers.ModelSerializer):
    subscriber = serializers.ReadOnlyField(source='subscriber.username')
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = SubscribeTable
        fields = ['id', 'subscriber', 'author', 'subscribed_at', 'is_active']


class UnsubscribeSerializer(serializers.ModelSerializer):
    subscriber = serializers.ReadOnlyField(source='subscriber.username')
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = UnsubscribeTable
        fields = ['id', 'subscriber', 'author', 'unsubscribed_at']
