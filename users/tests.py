import json
import jwt

from django.test        import TestCase, Client, client

from users.models       import Role, User
from freshcode.settings import SECRET_KEY, ALGORITHM

class UserTest(TestCase) :
    def setUp(self) :
        Role.objects.create(
            id   = 1,
            name = 'user'
        )

        user = User.objects.create(
            id       = 3,
            email    = "test@test.com",
            password = "test",
            name     = "test name",
            role_id  = Role.objects.get(id=1).id
        )

        global headers
        access_token = jwt.encode({'id' : user.id}, SECRET_KEY, ALGORITHM)
        headers      = {'HTTP_Authorization': access_token}

    def tearDown(self) :
        User.objects.all().delete()
        Role.objects.all().delete()
    
    def test_success_login(self) :
        client = Client() 

        login_info = {
            "email"    : "test@test.com",
            "password" : "test"
        }

        response = client.post('/users/login', json.dumps(login_info), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),{
            'token' : 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6M30.J9893j66hAExVsXvLT_Hl7JlJFwsSyrCM2W0BEeKIwk'
        })

    def test_failure_key_error_login(self) :
        client = Client()

        login_info = {
            "email"    : "test@test.com",
            "passrd" : "test"
        }

        response = client.post('/users/login', json.dumps(login_info), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'message' : 'KEY_ERROR'
        })
    
    def test_failure_user_does_not_exist_login(self) :
        client = Client() 

        login_info = {
            "email"    : "test1234@test.com",
            "password" : "test"
        }

        response = client.post('/users/login', json.dumps(login_info), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),{
            'message' : 'USER_DOES_NOT_EXISTS'
        })
        
    def test_failure_invalid_password_login(self) :
        client = Client()
        
        login_info = {
            "email"    : "test@test.com",
            "password" : "test12312"
        }

        response = client.post('/users/login', json.dumps(login_info), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),{
            'message' : 'INVALID_PASSWORD'
        })