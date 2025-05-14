from django.http import HttpResponseRedirect
from django.utils.http import url_has_allowed_host_and_scheme

class AppendSlashMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method == 'POST'
            and not request.path.endswith('/')
            and response.status_code == 500
        ):
            new_url = request.path + '/' + ('?' + request.GET.urlencode() if request.GET else '')
            if url_has_allowed_host_and_scheme(new_url, allowed_hosts=None):
                return HttpResponseRedirect(new_url)
        return response