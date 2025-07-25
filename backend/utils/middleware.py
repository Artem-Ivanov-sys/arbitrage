from django.http import HttpResponseForbidden

class CheckOriginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request, *args, **kwds):
        origin = request.headers.get('Origin')
        return self.get_response(request)