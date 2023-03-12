from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from .forms import RegistrationForm, UserEditForm, UserLoginForm
from .tokens import account_activation_token
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
# from .serializers import UserSerializer
import json

@csrf_exempt
@login_required
def profile(request):
    # return render(request,
    #               'accounts/profile.html',
    #               {'section': 'profile'})
    return HttpResponse(json.dumps({"token": "something"}), content_type="application/json")

@csrf_exempt
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        if user_form.is_valid():
            user_form.save()
    else:
        user_form = UserEditForm(instance=request.user)
    # return render(request,
    #               'accounts/update.html',
    #               {'user_form': user_form})
    return HttpResponse(json.dumps({"token": "something"}), content_type="application/json")

@csrf_exempt
@login_required
def delete_user(request):

    if request.method == 'POST':
        user = User.objects.get(username=request.user)
        user.is_active = False
        user.save()
        return redirect('accounts:login')

    # return render(request, 'accounts/delete.html')
    return HttpResponse(json.dumps({"token": "something"}), content_type="application/json")

@csrf_exempt
def post_search(request):
    form = PostSearchForm()
    q = ''
    c = ''
    results = []
    query = Q()

    if 'q' in request.GET:
        form = PostSearchForm(request.GET)
        if form.is_valid():
            q = form.cleaned_data['q']
            c = form.cleaned_data['c']

            if c is not None:
                query &= Q(category=c)
            if q is not None:
                query &= Q(title__contains=q)

            results = Post.objects.filter(query)

    # return render(request, 'blog/search.html',
    #               {'form': form,
    #                'q': q,
    #                'results': results})
    return HttpResponse(json.dumps({"token": "something"}), content_type="application/json")

@csrf_exempt
def accounts_register(request):
    if request.method == 'POST':
        formdata = json.loads(request.body.decode())
        registerForm = RegistrationForm(formdata)
        # print(registerForm.errors)
        if registerForm.is_valid():
            user = registerForm.save(commit=False)
            user.email = registerForm.cleaned_data['email']
            email = user.email
            user.set_password(registerForm.cleaned_data['password'])
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Activate your Account'
            # render_to_string('registration/account_activation_email.html'
            message = HttpResponse(json.dumps({"token": "something"}), content_type="application/json"), {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            }
            #user.email_user(subject=subject, message=message)
            return HttpResponse('registered succesfully and activation sent')
    else:
        registerForm = RegistrationForm()
    # return render(request, 'registration/register.html', {'form': registerForm})
    return HttpResponse(json.dumps({"email"}), content_type="application/json")

@csrf_exempt
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('login')
    else:
        # return render(request, 'registration/activation_invalid.html')
        return HttpResponse(json.dumps({"token": "something"}), content_type="application/json")

@csrf_exempt
def login(request):
    if request.method == 'POST':
        formdata = json.loads(request.body.decode())
        loginForm = UserLoginForm(formdata)
        user = loginForm.save(commit=False)
        user.username = loginForm.cleaned_data['username']
        user.password = loginForm.cleaned_data['password']
        # username = request.data['username']
        # password = request.data['password']
        user = User.objects.filter(username=user.username).first()
        if loginForm.is_valid():
            if user is None:
                raise AuthenticationFailed('User not found!')
            if not user.check_password(user.password):
                raise AuthenticationFailed('Incorrect password!')
            user = authenticate(username= user.username, password= user.password)
            login(request, user)
            return HttpResponse('logged in succesfully')
    else:
        loginForm = UserLoginForm()
    return HttpResponse(json.dumps({"email"}), content_type="application/json")

def getProfile(request):
    if request.method == "GET":
        id = request.GET.get('id', '')
        user = User.objects.get(pk=id)
        return HttpResponse(json.dumps({user.username}), content_type="application/json")
