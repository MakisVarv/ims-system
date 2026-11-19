from rest_framework import serializers

from .policies import can_manage_catalog, get_roles


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)

    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
        max_length=1024,
    )


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)

    display_name = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    warehouse_ids = serializers.SerializerMethodField()
    capabilities = serializers.SerializerMethodField()

    def get_display_name(self, user) -> str:
        return user.get_full_name().strip() or user.username

    def get_roles(self, user) -> list[str]:
        return get_roles(user)

    def get_warehouse_ids(self, user) -> list[int]:
        return []

    def get_capabilities(self, user) -> dict[str, bool]:
        return {
            "can_manage_catalog": can_manage_catalog(user),
        }


class CsrfSerializer(serializers.Serializer):
    csrf_token = serializers.CharField(read_only=True)


class LoginResultSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField(read_only=True)
    user = CurrentUserSerializer(read_only=True)
    csrf_token = serializers.CharField(read_only=True)
