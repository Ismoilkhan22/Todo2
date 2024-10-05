from django.shortcuts import render

from core.models import Task


def task_list(request):
    ctx = {
        "roots": Task.objects.all()

    }
    return render(request, 'pages/task/list.html', ctx)
