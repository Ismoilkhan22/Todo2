import random

from django.shortcuts import render, redirect
from methodism import generate_key

from core.models import User, OtpToken


def sign_in(request):
    ctx = {}
    if request.POST:
        username = request.POST.get('username')
        pas = request.POST.get('pass')
        # user check
        user = User.objects.filter(username=username).first()
        if not user:
            return render(request, "auth/login.html", {"error": "Login yoki parpl xato"})

        if not user.is_active:
            return render(request, "auth/login.html", {"error": "User is ban "})
        if not user.check_password(str(pas)):
            return render(request, "auth/login.html", {"error": "Login yoki parpl xato"})
        # otp
        code = random.randint(100_000, 999_999)
        # sms user.email ga chiqib ketadi
        token = generate_key(20) + "#" + str(code) + "#" + generate_key(20)
        # shifirlanadi
        otp = OtpToken.objects.create(key=token, by=2, extra={"user_id": user.id})
        request.session['otp_token'] = otp.key
        request.session['user_id'] = user.id
        request.session['code'] = code
        return redirect('otp')

    return render(request, 'auth/login.html', ctx)


def sign_up(request):
    return render(request, 'auth/register.html')


def sign_out(request):
    return redirect('sign-in')


def step_two(request):
    return render(request, 'auth/otp.html')
