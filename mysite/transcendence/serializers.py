from rest_framework import serializers
from .models import Match, SessionHistory

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'

class SessionHistorySerializer(serializers.ModelSerializer):
    match = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = SessionHistory
        fields = '__all__'
