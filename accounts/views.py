from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.http import urlsafe_base64_decode
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password

from rest_framework import status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import GenericAPIView

from rest_framework.parsers import FormParser, MultiPartParser, JSONParser

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .paginations import UsersPagination
from .permissions import ProfileComplete
from .models import Profile, User, ResetPasswordToken
from .serializer import (
    UserSerializer, ProfileSerializer, EmailSerializer,
    UserViewSerializer, ChangePasswordSerializer,
    ResetPasswordConfirmSerializer, GoogleLoginSerializer)

__all__ = (
    'LoginAPIView', 'SignUpAPIView', 'ActivateAPIView', 'LogoutAPIView',
    'ResendActivationEmailAPIView', 'ProfileAPIView',
    'ChangePasswordAPIView', 'ResetPasswordAPIView',
    'ResetPasswordConfirmAPIView',
    'GoogleLoginAPIView', 'IsActivatedAPIView'
)


class GoogleLoginAPIView(GenericAPIView):
    serializer_class = GoogleLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()

        return Response(
            data={'token': token.key},
            status=status.HTTP_200_OK
        )


LoginAPIView = ObtainAuthToken


class IsActivatedAPIView(GenericAPIView):
    serializer_class = EmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        user = get_object_or_404(User, username=data['email'])

        return Response(
            data={'is_active': user.is_active},
            status=status.HTTP_200_OK
        )


class SignUpAPIView(GenericAPIView):
    queryset = Profile.objects.all()
    serializer_class = UserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.send_activation_email()

        return Response(
            data={'detail': _('Check your email for confirmation link')},
            status=200
        )


class ActivateAPIView(GenericAPIView):

    def get(self, request, eid, token):
        User.activate(eid, token)
        return Response(data={'detail': _('Account Activated')},
                        status=status.HTTP_200_OK)


class LogoutAPIView(GenericAPIView):
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class ResendActivationEmailAPIView(GenericAPIView):
    serializer_class = EmailSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = get_object_or_404(User,
                                     email=serializer.validated_data['email'])
            user.send_activation_email()
            return Response(
                data={'detail': _('Check your email for confirmation link')},
                status=200
            )


class ProfileAPIView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get(self, request):
        user = request.user
        data = self.get_serializer(instance=user.profile).data
        return Response(data={'data': data}, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(instance=user.profile,
                                       data=request.data,
                                       partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={'data': serializer.data},
            status=status.HTTP_200_OK
        )

    def delete(self, request):
        to_be_deleted = self.request.query_params.get('file')
        if not to_be_deleted or to_be_deleted not in ('image', 'resume'):
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if to_be_deleted == 'image':
            self.request.user.profile.image = None
        else:
            self.request.user.profile.resume = None

        self.request.user.profile.save()

        return Response(status=status.HTTP_200_OK)


class ChangePasswordAPIView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            data={'detail': _('password changed successfully')},
            status=200
        )


class ResetPasswordAPIView(GenericAPIView):
    serializer_class = EmailSerializer

    def post(self, request):
        data = self.get_serializer(request.data).data

        user = get_object_or_404(User, email=data['email'])
        user.send_password_confirm_email()

        return Response(
            {'detail': _('Successfully Sent Reset Password Email')},
            status=200)


class ResetPasswordConfirmAPIView(GenericAPIView):
    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        rs_token = get_object_or_404(ResetPasswordToken, uid=data['uid'],
                                     token=data['token'])
        if (
                timezone.now() - rs_token.expiration_date).total_seconds() > 24 * 60 * 60:
            return Response({'error': 'Token Expired'}, status=400)

        user = get_object_or_404(User,
                                 id=urlsafe_base64_decode(data['uid']).decode(
                                     'utf-8'))
        rs_token.delete()
        user.password = make_password(data['new_password1'])
        user.save()
        return Response(data={'detail': _('Successfully Changed Password')},
                        status=200)


class ProfileInfoAPIView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = []

    def get(self, request, userid):
        user = get_object_or_404(User, id=userid)
        data = self.get_serializer(user.profile).data
        return Response(data={'data': data}, status=status.HTTP_200_OK)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['limited'] = True
        return context