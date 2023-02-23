import requests

from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from .models import User, Profile, ResetPasswordToken, GoogleLogin


class StringListField(serializers.ListField):
    child = serializers.CharField(max_length=256, allow_null=True,
                                  allow_blank=True)


class ProfileSerializer(serializers.ModelSerializer):
    is_complete = serializers.SerializerMethodField('_is_complete')
    email = serializers.SerializerMethodField('_email')
    image_link = serializers.SerializerMethodField('_get_image_link')

    @staticmethod
    def _is_complete(obj: Profile):
        return obj.is_complete

    @staticmethod
    def _email(obj: Profile):
        return obj.user.email

    @staticmethod
    def _get_image_link(obj: Profile):
        if not obj.image:
            return ''
        url = obj.image.url
        if settings.DOMAIN not in url:
            return settings.DOMAIN + url
        return url

    class Meta:
        model = Profile
        exclude = ['user', 'id', 'phone_number']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if self.context.get('limited', False):
            for field in Profile.sensitive_fields():
                data.pop(field)
        return data

    def validate(self, attrs):
        image = attrs.get('image')

        if image and image.size > Profile.IMAGE_MAX_SIZE:
            raise serializers.ValidationError('Maximum file size reached')

        return attrs

    def update(self, instance: Profile, validated_data):
        instance: Profile = super().update(instance, validated_data)
        return instance


class LimitedProfileSerializer(serializers.ModelSerializer):
    is_complete = serializers.SerializerMethodField('_is_complete')
    image_link = serializers.SerializerMethodField('_get_image_link')

    @staticmethod
    def _is_complete(obj: Profile):
        return obj.is_complete

    @staticmethod
    def _get_image_link(obj: Profile):
        if not obj.image:
            return ''
        url = obj.image.url
        if settings.DOMAIN not in url:
            return settings.DOMAIN + url
        return url

    class Meta:
        model = Profile
        exclude = ('id', 'user', 'phone_number', 'hide_profile_info',
                   'can_sponsors_see', 'province', 'resume')


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    phone_number = serializers.CharField(
        max_length=32,
        required=True,
    )
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password_1 = serializers.CharField(
        style={'input_type': 'password'}
    )
    password_2 = serializers.CharField(
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'password_1', 'password_2',
                  'profile']

    def validate(self, attrs):
        if attrs.get('password_1') != attrs.get('password_2'):
            raise ValidationError(_("Passwords not match"))

        return attrs

    def create(self, validated_data):
        validated_data.pop('password_2')
        validated_data['password'] = validated_data.pop('password_1')

        user = User.objects.create_user(
            username=validated_data.get('email'),
            email=validated_data.get('email'),
            password=validated_data.get('password'),
            is_active=False
        )
        profile = Profile.objects.create(
            user=user,
            phone_number=validated_data.get('phone_number')
        )

        return user


class ResetPasswordConfirmSerializer(serializers.ModelSerializer):
    new_password1 = serializers.CharField(max_length=100)
    new_password2 = serializers.CharField(max_length=100)

    class Meta:
        model = ResetPasswordToken
        fields = ['new_password1', 'new_password2', 'uid', 'token']

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError('passwords don\'t match!')
        return data


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password1 = serializers.CharField(style={'input_type': 'password'})
    new_password2 = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        if data['new_password1'] != data['new_password2']:
            raise serializers.ValidationError(_('passwords don\'t match!'))
        if not self.context['request'].user.check_password(
                data['old_password']):
            raise serializers.ValidationError(_('invalid old password'))
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(
            raw_password=self.validated_data['new_password1']
        )
        user.save()

        return user


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class UserViewSerializer(serializers.ModelSerializer):
    profile = LimitedProfileSerializer(context={'limited': True})

    class Meta:
        model = User
        fields = ['profile', 'email', 'id']


class GoogleLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoogleLogin
        exclude = ('id',)

    def create(self, validated_data):
        from apps.core.utils import password_generator

        response = requests.get(
            f'https://www.googleapis.com/oauth2/v3/tokeninfo?id_token='
            f'{validated_data["id_token"]}'
        )

        if response.status_code != 200:
            raise ValidationError("Error occurred with google login")

        data = response.json()
        validated_data['email'] = data['email']

        user = User.objects.filter(email=data['email']).last()
        if user and not user.is_active:
            user.is_active = True
            user.save()
        if not user:
            validated_data['is_signup'] = True
            user = User.objects.create(
                username=data['email'],
                email=data['email'],
                password=password_generator(),
                is_active=True
            )
            profile = Profile.objects.create(
                user=user
            )

        google_login = super().create(validated_data)
        token, created = Token.objects.get_or_create(user=user)
        return token
