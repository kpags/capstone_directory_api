from rest_framework.authentication import BaseAuthentication
import jwt, os
from datetime import datetime, timedelta, timezone
from users.models import Users
from rest_framework.exceptions import AuthenticationFailed

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
ENV = os.environ.get("ENVIRONMENT", "dev")


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "").split()
        if len(auth_header) == 2 and auth_header[0].lower() == "bearer":
            token = auth_header[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            user_id = payload["id"]
            expiry_date_str = payload["expires_in"]
            expiry_date_obj = datetime.fromisoformat(expiry_date_str)
            current_date = datetime.now(timezone.utc)

            if ENV.lower() in ["prod", "production"]:
                if current_date.date() == expiry_date_obj.date():
                    raise AuthenticationFailed({"message": "Token already expired"})

            try:
                user = Users.objects.get(id=user_id)

                if not user.is_active:
                    return None

                request.instance = user
                request.token = token

                return {"instance": user, "token": token}
            except Users.DoesNotExist:
                return None

        return None


def encode_tokens(user: Users):
    access_payload = {}
    refresh_payload = {}

    access_payload["id"] = str(user.id)
    access_payload["first_name"] = user.first_name
    access_payload["last_name"] = user.last_name
    access_payload["email"] = user.email
    access_payload["role"] = user.role
    access_payload["is_active"] = user.is_active
    access_payload["expires_in"] = str(datetime.now(timezone.utc) + timedelta(days=1))

    refresh_payload["id"] = str(user.id)
    refresh_payload["expires_in"] = str(datetime.now(timezone.utc) + timedelta(days=7))

    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm="HS256")
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm="HS256")

    return access_token, refresh_token
