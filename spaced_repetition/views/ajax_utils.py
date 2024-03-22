import json
from django.http import HttpRequest


def parse_post(post_method):
    def parse_post_method(self, request: HttpRequest, *args, **kwargs):
        post_data = json.loads(request.body.decode())
        return post_method(self, request, *args, post_data=post_data, **kwargs)

    return parse_post_method
