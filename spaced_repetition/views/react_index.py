from django.shortcuts import render
from django.views import View
from django.http import HttpRequest, HttpResponseRedirect


class ReactIndexView(View):
    def get(self, request: HttpRequest):
        return render(request, 'react_index.html')
