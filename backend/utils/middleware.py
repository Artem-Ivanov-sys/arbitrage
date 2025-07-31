from django.http import HttpResponseForbidden
import ipaddress
from django.conf import settings
from django.http.response import HttpResponseForbidden

class CheckOriginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    def check_ip(self, ip):
        try:
            ip_addr = ipaddress.ip_address(ip)
            print(ip_addr)
            if any(ip_addr == addr for addr in settings.ALLOWED_HOSTS):
                return True
            return False
        except:
            return False
    def __call__(self, request, *args, **kwds):
        origin = request.headers.get('Origin')
        allowed = self.check_ip(request.META['REMOTE_ADDR'])
        return self.get_response(request)
        return self.get_response(request) if allowed else HttpResponseForbidden(content="Not allowed")