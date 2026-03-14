class SetTheme:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            request.session['theme'] = request.user.background if request.user.background else "light"
        else:
            request.session['theme'] = request.session.get('theme') or "light"
        request.session.set_expiry(75686400)
        response = self.get_response(request)
        return response
