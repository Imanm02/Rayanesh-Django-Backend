import secrets

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.translation import gettext_lazy as _
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.core.utils import send_email


class DegreeTypes:
    ST = 'دانش‌ آموز'
    BA = 'کارشناسی'
    MA = 'کارشناسی ارشد'
    DO = 'دکترا'

    TYPES = (
        ('ST', ST),
        ('BA', BA),
        ('MA', MA),
        ('DO', DO)
    )


class User(AbstractUser):

    def send_activation_email(self):
        activate_user_token = ActivateUserToken(
            token=secrets.token_urlsafe(32),
            eid=urlsafe_base64_encode(force_bytes(self.email)),
        )
        activate_user_token.save()

        context = {
            'domain': settings.DOMAIN,
            'eid': activate_user_token.eid,
            'token': activate_user_token.token,
            'first_name': self.profile.firstname_en
        }

        send_email(
            subject='فعالسازی اکانت AIC21',
            context=context,
            template_name='accounts/email/registerifinal.htm',
            receipts=[self.email]
        )

    def send_password_confirm_email(self):
        uid = urlsafe_base64_encode(force_bytes(self.id))
        ResetPasswordToken.objects.filter(uid=uid).delete()
        reset_password_token = ResetPasswordToken(
            uid=uid,
            token=secrets.token_urlsafe(32),
            expiration_date=timezone.now() + timezone.timedelta(hours=24),
        )
        reset_password_token.save()
        context = {
            'domain': settings.DOMAIN,
            'username': self.username,
            'uid': reset_password_token.uid,
            'token': reset_password_token.token,
        }
        send_email(
            subject='تغییر رمز عبور AIC21',
            context=context,
            template_name='accounts/email/user_reset_password.html',
            receipts=[self.email]
        )

    @classmethod
    def activate(cls, eid, token):
        activate_user_token = get_object_or_404(ActivateUserToken,
                                                eid=eid, token=token)

        email = urlsafe_base64_decode(eid).decode('utf-8')
        user = cls.objects.get(email=email)
        user.is_active = True
        activate_user_token.delete()
        user.save()

class Profile(models.Model):
    IMAGE_MAX_SIZE = 1024 * 1024

    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile'
                                )

    # Personal Info
    displayed_name = models.CharField(max_length=64, blank=True, null=True)

    # Academic Info
    university_degree = models.CharField(choices=DegreeTypes.TYPES,
                                         max_length=32, null=True, blank=True)

    # Others
    image = models.ImageField(null=True, blank=True)

    @property
    def is_complete(self):
        return all(
            (
                self.university_degree, self.displayed_name, self.username
            )
        )

    @staticmethod
    def sensitive_fields():
        return ('is_complete')

    def __str__(self):
        return f'username: {self.user.username},' \
               f'name: {self.displayed_name},' \
               f'email: {self.user.email}'


class ActivateUserToken(models.Model):
    token = models.CharField(max_length=100)
    eid = models.CharField(max_length=100, null=True)


class ResetPasswordToken(models.Model):
    uid = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    expiration_date = models.DateTimeField()

class GoogleLogin(models.Model):
    access_token = models.CharField(max_length=1024)
    expires_at = models.PositiveBigIntegerField()
    expires_in = models.PositiveIntegerField()
    id_token = models.TextField()
    scope = models.TextField()
    is_signup = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)