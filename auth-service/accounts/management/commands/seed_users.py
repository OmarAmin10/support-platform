from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):

    def handle(self, *args, **options):
        for i in range(1,51):
            user,created = User.objects.get_or_create(
                username=f"customer{i}",
                defaults={
                "email": f"customer{i}@test.com",
                "role":User.Role.CUSTOMER,
                }
            )


            if created: 
                user.set_password("Customer123!")
                user.save()


        for i in range(1,51):
                    user,created = User.objects.get_or_create(
                        username=f"agent{i}",
                        defaults={
                        "email": f"agent{i}@test.com",
                        "role":User.Role.AGENT,
                        }
                    )
                    if created: 
                        user.set_password("Agent123!")
                        user.save()

        for i in range(1,51):
                     user,created = User.objects.get_or_create(
                         username=f"admin{i}",
                         defaults={
                         "email": f"Admin{i}@test.com",
                         "role":User.Role.ADMIN,
                         }
                     )
                     if created: 
                         user.set_password("Admin123!")
                         user.save()                           
            
