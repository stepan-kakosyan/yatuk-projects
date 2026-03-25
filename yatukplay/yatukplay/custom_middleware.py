from django.shortcuts import redirect


class CustomMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        status_code = getattr(response, 'status_code', None)
        if status_code >= 400:
            return redirect('index', permanent=True)
        return response
