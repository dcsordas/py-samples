from django.contrib.auth.models import User
from django.shortcuts import render


# TODO as ListView
def index(request):
    status_report = dict.fromkeys(
        ['ADMIN EXISTS', 'ADMIN IS ACTIVE'],
        False)
    try:
        admin_user = User.objects.get(is_superuser=True)
    except User.DoesNotExist:
        pass
    else:
        status_report['ADMIN EXISTS'] = True
        status_report['ADMIN IS ACTIVE'] = admin_user.is_active

    # return response
    context = dict(status_report=status_report)
    return render(request, 'app/index.html', context, request)
