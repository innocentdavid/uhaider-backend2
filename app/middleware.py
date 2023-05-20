from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from django.middleware.http import MiddlewareMixin
import jwt


class TokenAuthenticationMiddleware:
    EXCLUDED_VIEWS = ['register', 'login']
    TOKEN_COOKIE_NAME = 'jwt'

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.COOKIES.get('jwt', None)
        print("mw_token: ")
        print(token)

        print("mw_request.COOKIES: ")
        print(request.COOKIES)

        print("mw_request.META.get('HTTP_COOKIE'): ")
        print(request.META.get('HTTP_COOKIE'))
        # print(request.META.get('HTTP_AUTHORIZATION'))

        if not token:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header is not None and auth_header.startswith('Bearer '):
                if auth_header[7:] != 'undefined':
                    token = auth_header[7:]
            else:
                auth_cookie = request.META.get('HTTP_COOKIE')
                if auth_cookie is not None and auth_cookie.startswith('jwt'):
                    if auth_cookie[4:] != 'undefined':
                        token = auth_cookie[4:]
                        
        print("mw_final token: ")
        print(token)
        # print(token)
        if token is None:
            return JsonResponse({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)
            
        if token is not None:            
            try:
                payload = jwt.decode(
                    token, settings.SECRET_KEY, algorithms="HS256")
                print("mw_payload: ")
                print(payload)
            except jwt.exceptions.InvalidSignatureError:
                print('Invalid signature!')
                return JsonResponse({'message': 'Invalid signature!'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.exceptions.ExpiredSignatureError:
                print('Signature has expired!')
                return JsonResponse({'message': 'Signature has expired!'}, status=status.HTTP_401_UNAUTHORIZED)
            except jwt.exceptions.DecodeError:
                print('Invalid token!')
                return JsonResponse({'message': 'Invalid token!'}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                print('Unauthenticated!')
                return JsonResponse({'message': 'Unauthenticated!'}, status=status.HTTP_401_UNAUTHORIZED)

        # if request.resolver_match is not None:
        #     print("mw_request.resolver_match.url_name: ")
        #     print(token)

        if (request.resolver_match is not None
                and request.resolver_match.url_name not in self.EXCLUDED_VIEWS
                and token is None):
            return JsonResponse({'message': 'Token cookie not found'}, status=status.HTTP_401_UNAUTHORIZED)
        print('t')
        print(token)
        response = self.get_response(request)
        return response


class MyCookieMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.session['user_id'] = 'new user'
        # print("mw_request: ")
        # print(request)
        # if request.user.is_authenticated:
        #     request.session['user_id'] = request.user.id

    def process_response(self, request, response):
        if request.session.get('user_id'):
            response.set_cookie('user_id', request.session['user_id'])

        return response
