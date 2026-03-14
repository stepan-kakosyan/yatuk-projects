from .settings import BACKGROUNDS

class SetTheme:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        default = "linear-gradient(to right, rgb(58, 96, 115), rgb(22, 34, 42))"
        request.session['backgrounds'] = BACKGROUNDS
        if request.user.is_authenticated:
            request.session['background'] = request.user.background or default
        else:
            request.session['background'] = request.session.get('background') or default
        request.session.set_expiry(75686400)
        response = self.get_response(request)
        return response
