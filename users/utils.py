import jwt

from django.http        import JsonResponse

from users.models       import User
from freshcode.settings import SECRET_KEY, ALGORITHM

def login_decorator(func) :
    def wrapper(self, request, *args, **kwargs) :
        try :
            access_token = request.headers.get('Authorization')
            payload      = jwt.decode(access_token, SECRET_KEY, ALGORITHM)
            user         = User.objects.get(id=payload['id'])
            request.user = user

        except User.DoesNotExist :
            return JsonResponse({'message' : 'USER_DOES_NOT_EXIST'}, status=400)

        except jwt.exceptions.DecodeError :
            return JsonResponse({'message' : 'DECODE_ERROR'}, status=401)

        return func(self, request, *args, **kwargs)

    return wrapper