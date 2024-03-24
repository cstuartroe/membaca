import json
from django.http import HttpRequest, HttpResponse


def parse_post(post_method):
    def parse_post_method(self, request: HttpRequest, *args, **kwargs):
        post_data = json.loads(request.body.decode())
        return post_method(self, request, *args, post_data=post_data, **kwargs)

    return parse_post_method


def admin_only(method):
    def admin_only_method(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponse(403)

        return method(self, request, *args, **kwargs)

    return admin_only_method
