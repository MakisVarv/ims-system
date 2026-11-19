from drf_spectacular.authentication import SessionScheme
from rest_framework.authentication import SessionAuthentication


class SessionAuthentication401(SessionAuthentication):
    def authenticate_header(self, request):
        return "Session"


class IMSCookieScheme(SessionScheme):
    target_class = "modules.identity.authentication.SessionAuthentication401"
