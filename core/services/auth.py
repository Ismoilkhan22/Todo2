import random
from contextlib import closing
from datetime import datetime
from django.contrib.auth import login as django_login, logout, authenticate
import pytz
from django.db import connection
from django.shortcuts import render, redirect
from methodism import generate_key, code_decoder

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
        otp = OtpToken.objects.create(key=token, by=2, extra={"user_id": user.id})
        request.session['otp_token'] = otp.key
        request.session['user_id'] = user.id
        request.session['code'] = code
        return redirect('otp')

    return render(request, 'auth/login.html', ctx)


def sign_up(request):
    ctx = {}
    if request.POST:
        password = request.POST.get('pass')
        repassword = request.POST.get('re-pass')
        username = request.POST.get('username')
        email = request.POST.get('email')
        # user check
        user_sql = f"""
        select id from core_user
        WHERE email='{email}' or username = '{username}'
        """
        with closing(connection.cursor()) as cursor:
            cursor.execute(user_sql)
            user = cursor.fetchone()
            print(user)
        if user:
            return render(request, 'auth/register.html', {'error': 'ushbu user yoki email allaqachon bazada mavjud'})
        if password != repassword:
            return render(request, 'auth/register.html', {'error': 'parollar mos kelmadi'})
        # otp
        code = random.randint(100_000, 999_999)
        # sms chqiib ketadi user.email ga
        token = generate_key(20) + "#" + str(code) + "#" + generate_key(20)
        otp = OtpToken.objects.create(key=token, by=1,
                                      extra={
                                          "username": username, "email": email, "password": password
                                      })
        request.session['otp_token'] = otp.key
        request.session['code'] = code
        return redirect('otp')

    return render(request, 'auth/register.html')


def otp(request):
    token = request.session.get('otp_token')

    if not token:
        return redirect('login')
    if request.POST:

        kod = request.POST.get('code')
        otp = OtpToken.objects.filter(key=token).first()

        if not otp:
            return redirect('login')
        if otp.is_expired or otp.is_verified:
            return render(request, 'auth/otp.html', {'error': 'ushbu token eskirgan'})
        now = datetime.now(pytz.UTC)
        if (now - otp.created).total_seconds() > 120:
            return render(request, 'auth/otp.html', {'error': 'ushbu tokenga ajratilgan vaqt tugadi'})
        code = token.split('#')[1]
        if str(code) != str(kod):
            otp.tries += 1
            otp.save()
            return render(request, 'auth/otp.html', {'error': 'Xato kod'})
        if otp.by == 2:
            if str(otp.extra['user_id']) != str(request.session.get('user_id')):
                return redirect('login')
            user = User.objects.filter(id=int(request.session.get('user_id'))).first()
            if not user:
                return redirect('login')
            django_login(request, user)
            otp.is_expired = True
            otp.is_verified = True
            otp.save()
            try:
                del request.session['otp_token']
                del request.session['user_id']
                del request.session['code']
            except:
                pass
            return redirect('home')
        elif otp.by == 1:
            user = User.objects.create_user(**otp.extra)
            django_login(request, user)
            authenticate(request)
            otp.is_expired = True
            otp.is_verified = True
            otp.extra = {}
            otp.save()
            try:
                del request.session['otp_token']
                del request.session['code']
            except:
                pass
            return redirect('home')

    return render(request, 'auth/otp.html')


def re_otp(request):
    old_token = request.session.get('otp_token')

    if not old_token:
        return redirect('login')
    old_otp = OtpToken.objects.filter(key=old_token).first()
    if not old_otp:
        return redirect('login')
    old_otp.is_expired = True
    old_otp.save()
    code = random.randint(100_000, 999_999)
    # sms user.email ga chiqib ketadi
    new_token = generate_key(20) + "#" + str(code) + "#" + generate_key(20)
    otp = OtpToken.objects.create(key=new_token, by=old_otp.by, extra=old_otp.extra)
    request.session['otp_token'] = otp.key
    if otp.by == 2:
        request.session['user_id'] = old_otp.extra['user_id']
        otp.extra = {}
        otp.save()
    request.session['code'] = code
    return redirect('otp')


def sign_out(request):
    logout(request)
    return redirect('sign-in')

# def step_two(request):
#     return render(request, 'auth/otp.html')
