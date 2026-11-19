from getpass import getpass

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from modules.identity.policies import Role

DEMO_USERS = (
    ("inventory_manager", Role.INVENTORY_MANAGER),
    ("warehouse_operator", Role.WAREHOUSE_OPERATOR),
    ("purchasing_officer", Role.PURCHASING_OFFICER),
    ("purchasing_manager", Role.PURCHASING_MANAGER),
    ("auditor", Role.AUDITOR),
)


class Command(BaseCommand):
    help = "Create initial roles; optionally create local demo users."

    def add_arguments(self, parser):
        parser.add_argument(
            "--demo",
            action="store_true",
        )

    def handle(self, *args, **options):
        User = get_user_model()
        password = None

        if options["demo"]:
            if not settings.DEBUG:
                raise CommandError("Demo users require DEBUG=True.")

            password = getpass("Password for NEW demo users: ")

            confirmation = getpass("Confirm password: ")

            if password != confirmation:
                raise CommandError("Passwords do not match.")

            try:
                for username, _ in DEMO_USERS:
                    validate_password(
                        password,
                        user=User(username=username),
                    )

            except ValidationError as error:
                raise CommandError("; ".join(error.messages)) from error

        with transaction.atomic():
            groups = {
                name: Group.objects.get_or_create(
                    name=name,
                )[0]
                for name in Role.ALL
            }

            if options["demo"]:
                for username, role in DEMO_USERS:
                    user, created = User.objects.get_or_create(
                        username=username,
                    )

                    if created:
                        user.set_password(password)
                        user.save(update_fields=["password"])
                        user.groups.add(groups[role])

                        self.stdout.write(f"Created: {username} -> {role}")

                    else:
                        self.stdout.write(f"Unchanged existing user: {username}")

        self.stdout.write(self.style.SUCCESS("Initial identity data ready."))
