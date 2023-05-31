from django.contrib.auth.models import BaseUserManager

# Create a custom user manager that defines the behavior to be followed when user is being created


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, email, password=None, **extra_fields):
        # create a new user with the given phone_number, email, and password
        if not phone_number:
            raise ValueError('The Phone number field must be set')
        if not email:
            raise ValueError('The Email field must be set')

        user = self.model(
            phone_number=phone_number,
            email=self.normalize_email(email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, email, password=None, **extra_fields):
        # create a new superuser with the given phone_number, email, and password
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone_number, email, password, **extra_fields)
