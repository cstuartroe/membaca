from django.shortcuts import render
from django.http import HttpResponseRedirect


def react_index(request):
    if not request.user.is_active:
        r = HttpResponseRedirect("/admin/login/?next=/")
        return r

    return render(request, 'react_index.html', {
        "user_email": request.user.email,
        "is_admin": request.user.is_superuser,
    })