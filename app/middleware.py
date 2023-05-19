from django.http import HttpResponse
from django.middleware.http import MiddlewareMixin
import jwt


class TokenAuthenticationMiddleware:
    EXCLUDED_VIEWS = ['register', 'login']
    TOKEN_COOKIE_NAME = 'jwt'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = None
        try:
            token = request.COOKIES.get('jwt', None)
        except:
            try:
                auth_header = request.META.get('HTTP_AUTHORIZATION')
                if auth_header is not None and auth_header.startswith('Bearer '):
                    token = auth_header[7:]
            except:
                token = None
        # print(token)
        if token is not None:
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms="HS256")
                print("payload: ")
                print(payload)
            except jwt.exceptions.InvalidSignatureError:
                return HttpResponse({'message': 'Invalid signature!'}, status=403)
            except jwt.exceptions.ExpiredSignatureError:
                return HttpResponse({'message': 'Signature has expired!'}, status=403)
            except jwt.exceptions.DecodeError:
                return HttpResponse({'message': 'Invalid token!'}, status=403)
            except:
                return HttpResponse({'message': 'Unauthenticated!'}, status=403)

        # if token is None:
        #     return False
        # return True

        # if request.resolver_match is not None:
        #     print("request.resolver_match.url_name: ")
        #     print(token)

        if (request.resolver_match is not None
                and request.resolver_match.url_name not in self.EXCLUDED_VIEWS
                and token is None):
            return HttpResponse('Token cookie not found', status=403)

        response = self.get_response(request)
        return response


class MyCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.session['user_id'] = 'new user'
        # print("request: ")
        # print(request)
        # if request.user.is_authenticated:
        #     request.session['user_id'] = request.user.id

    def process_response(self, request, response):
        if request.session.get('user_id'):
            response.set_cookie('user_id', request.session['user_id'])

        return response
