from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from spaced_repetition.models.language import Language


def react_index(request):
    if not request.user.is_active:
        r = HttpResponseRedirect("/admin/login/?next=/")
        return r

    return render(request, 'react_index.html', {
        "user_email": request.user.email,
        "is_admin": request.user.is_superuser,
    })


def languages(request):
    if request.method == "GET":
        return JsonResponse(
            data=[
                language.to_json()
                for language in Language.objects.all()
            ],
            safe=False,
        )