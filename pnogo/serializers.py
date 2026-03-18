from rest_framework import serializers

from .models import Cndr, Picture


class CndrSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cndr
        fields = ["id", "name"]


class PictureSerializer(serializers.ModelSerializer):
    cndr = serializers.CharField(source="cndr.name", read_only=True)

    class Meta:
        model = Picture
        fields = ["id", "file", "description", "points", "sent", "daily_date", "cndr"]


class PictureUploadSerializer(serializers.Serializer):
    picture = serializers.ImageField()
    cndr = serializers.CharField()
    description = serializers.CharField(required=False, default="")


class PictureUpdateSerializer(serializers.Serializer):
    description = serializers.CharField()
