from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required(login_url='sign-in')
def index(request):
    ctx = {}
    return render(request, "base.html", ctx)
