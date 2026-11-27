import logging

from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework.views import APIView

from .authentication import SessionAuthentication401
from .serializers import (
    CsrfSerializer,
    CurrentUserSerializer,
    LoginResultSerializer,
    LoginSerializer,
)

logger = logging.getLogger(__name__)

CSRF_HEADER = OpenApiParameter(
    name="X-CSRFToken",
    location=OpenApiParameter.HEADER,
    required=True,
    type=str,
    description=("Token from /auth/csrf/ or the latest successful login."),
)


class AuthAPIView(APIView):
    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(
            request,
            response,
            *args,
            **kwargs,
        )

        response["Cache-Control"] = "no-store"
        return response


class LoginThrottle(AnonRateThrottle):
    scope = "login"
    rate = "10/min"


class CsrfView(AuthAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: CsrfSerializer},
        auth=[],
    )
    def get(self, request):
        return Response(
            {
                "csrf_token": get_token(request._request),
            }
        )


class LoginView(AuthAPIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [LoginThrottle]

    @extend_schema(
        request=LoginSerializer,
        parameters=[CSRF_HEADER],
        responses={
            200: LoginResultSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
            429: OpenApiTypes.OBJECT,
        },
        auth=[],
    )
    def post(self, request):
        # Ελέγχουμε CSRF ακόμη και πριν συνδεθεί ο χρήστης.
        SessionAuthentication401().enforce_csrf(request)

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request._request,
            credentials=serializer.validated_data,
        )

        if user is None:
            logger.warning("IMS login rejected")

            return Response(
                {
                    "code": "INVALID_CREDENTIALS",
                    "detail": "Invalid username or password.",
                },
                status=401,
                headers={
                    "WWW-Authenticate": "Session",
                },
            )

        login(request._request, user)

        return Response(
            {
                "authenticated": True,
                "user": CurrentUserSerializer(user).data,
                "csrf_token": get_token(request._request),
            }
        )


class MeView(AuthAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: CurrentUserSerializer,
            401: OpenApiTypes.OBJECT,
        },
    )
    def get(self, request):
        return Response(CurrentUserSerializer(request.user).data)


class LogoutView(AuthAPIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=None,
        parameters=[CSRF_HEADER],
        responses={
            204: None,
            401: OpenApiTypes.OBJECT,
            403: OpenApiTypes.OBJECT,
        },
    )
    def post(self, request):
        logout(request._request)
        return Response(status=204)
