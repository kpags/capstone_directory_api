from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Users, CapstoneGroups, UserProfile


class EmailAndPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class ChangeCurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        http_method = self.context.get("request")

        if http_method in ["put", "patch"]:
            self.fields.pop("email", None)
            self.fields.pop("password", None)
