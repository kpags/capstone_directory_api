from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Users, CapstoneGroups, UserProfile

class CSVFileSerializer(serializers.Serializer): # For bulk creation of users throgh upload
    file = serializers.FileField()

class EmailAndPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()
    
class ChangeCurrentPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField()


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        exclude = ["password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        http_method = self.context.get("request", None)

        if http_method and http_method.lower() in ["put", "patch"]:
            self.fields.pop("email", None)
            self.fields.pop("password", None)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = "__all__"
        depth = 1
        
class CapstoneGroupsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CapstoneGroups
        fields = "__all__"