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
            id       = 1,
            email    = "test@test.com",
            password = "test",
            name     = "test name",
            role_id  = 1
        )

        global access_token
        access_token = jwt.encode({'id' : user.id}, SECRET_KEY, ALGORITHM)

    def tearDown(self) :
        User.objects.all().delete()
        Role.objects.all().delete()
    
    def test_success_login(self) :
        client = Client() 

        login_info = {
            "email"    : "test@test.com",
            "password" : "test"
        }

        response = client.post('/users/login', json.dumps(login_info), content_type = 'application/json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            'token' : access_token
        })

    def test_failure_key_error_login(self):
        client = Client()

        login_info = {
            "email"    : "test@test.com",
            "passrd" : "test"
        }

        response = client.post('/users/login', json.dumps(login_info), content_type = 'application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'message' : 'KEY_ERROR'
        })
    
    def test_failure_json_decode_error_login(self):
        client = Client()

        response = client.post('/users/login')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'message' : 'JSON_DECODE_ERROR'
        })
    
    def test_failure_invalid_user_login(self):
        client = Client() 

        login_info = {
            "email"    : "test1234@test.com",
            "password" : "test"
        }

        response = client.post('/users/login', json.dumps(login_info), content_type='application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),{
            'message' : 'INVALID_USER'
        })
        
    def test_failure_invalid_password_login(self):
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