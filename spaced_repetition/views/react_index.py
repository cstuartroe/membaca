from django.shortcuts import render
from django.views import View
from django.http import HttpResponseRedirect


class ReactIndexView(View):
    def get(self, request):
        if not request.user.is_active:
            r = HttpResponseRedirect("/admin/login/?next=/")
            return r

        return render(request, 'react_index.html', {
            "user_email": request.user.email,
            "is_admin": request.user.is_superuser,
        })
