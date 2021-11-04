import json
import jwt

from django.http  import JsonResponse
from django.views import View

from users.models       import User
from freshcode.settings import SECRET_KEY, ALGORITHM

class LoginView(View) :
    def post(self, request) :
        try :
            data = json.loads(request.body)

            if not User.objects.filter(email=data['email']).exists() :
                return JsonResponse({'message' : 'USER_DOES_NOT_EXISTS'}, status=401)
            
            user = User.objects.get(email=data['email'])
            
            if not User.objects.filter(password=data['password']).exists() :
                return JsonResponse({'message' : 'INVALID_PASSWORD'}, status=401)
            
            token = jwt.encode({'id' : user.id}, SECRET_KEY, ALGORITHM)

            return JsonResponse({'token':token}, status=201)
        
        except KeyError :
            return JsonResponse({'message' : 'KEY_ERROR'}, status=400)