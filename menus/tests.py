import json
import jwt

from django.test  import TestCase, Client
from django.conf  import settings

from menus.models import Category, Badge, Item, Menu, Size, Tag
from users.models import Role, User

class MenuViewTest(TestCase):
    def setUp(self):
        global headers1, headers2
        access_token  = jwt.encode({'id' : 1}, settings.SECRET_KEY, settings.ALGORITHM)
        access_token2 = jwt.encode({'id' : 2}, settings.SECRET_KEY, settings.ALGORITHM)
        headers1      = {'HTTP_Authorization': access_token}
        headers2      = {'HTTP_Authorization': access_token2}

        role1    = Role.objects.create(id = 1, name = 'USER')
        role2    = Role.objects.create(id = 2, name = 'ADMIN')
        user1    = User.objects.create(id = 1, email = 'user@freshcode.me', password = 'user', name = '김유저', role = role1)
        user2    = User.objects.create(id = 2, email = 'admin@freshcode.me', password = 'admin', name = '관리자', role = role2)
        category = Category.objects.create(id = 1, name = 'SALAD')
        badge    = Badge.objects.create(id = 1, name = 'NEW' )
        tag      = Tag.objects.create(id = 1, name = '페스코베지테리언', type = 'vegetarianism')
        menu1    = Menu.objects.create(id = 1, category = category, badge = badge, name = 'menu1', description = 'abcd')
        menu2    = Menu.objects.create(id = 2, category = category, badge = badge, name = 'menu2', description = 'abcd')
        size     = Size.objects.create(id = 1, english_name = 'L', korean_name = '라지')
        item1    = Item.objects.create(id = 1, size = size, menu = menu1, price = 9000)
        item2    = Item.objects.create(id = 2, size = size, menu = menu2, price = 9000)

        menu1.tags.add(tag)
        menu2.tags.add(tag)
    
    def tearDown(self):
        Role.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()
        Badge.objects.all().delete()
        Tag.objects.all().delete()
        Menu.objects.all().delete()
        Size.objects.all().delete()
        Item.objects.all().delete()

    def test_menu_post_success(self):
        client = Client()
        data   = {
            'category_id' : '1',
            'badge_id'    : '1',
            'tag_id'      : '1',
            'name'        : '야채샐러드',
            'description' : 'abcd'
        }

        response = client.post('/menus', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),
            {
                "message" : "SUCCESS"
            }
        )
    
    def test_menu_post_json_decode_error(self):
        client = Client()

        response = client.post('/menus', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "JSON_DECODE_ERROR"
            }
        )
    
    def test_menu_post_forbidden_error(self):
        client = Client()
        data   = {
            'category_id' : '1',
            'badge_id'    : '1',
            'tag_id'      : '1',
            'name'        : '야채샐러드',
            'description' : 'abcd'
        }

        response = client.post('/menus', json.dumps(data), content_type = 'application/json', **headers1)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(),
            {
                "message" : "FORBIDDEN"
            }
        )
    
    def test_menu_post_invalid_category_error(self):
        client = Client()
        data   = {
            'category_id' : '2',
            'badge_id'    : '1',
            'tag_id'      : '1',
            'name'        : '야채샐러드',
            'description' : 'abcd'
        }

        response = client.post('/menus', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_CATEGORY_ID"
            }
        )
    
    def test_menu_post_invalid_badge_error(self):
        client = Client()
        data   = {
            'category_id' : '1',
            'badge_id'    : '2',
            'tag_id'      : '1',
            'name'        : '야채샐러드',
            'description' : 'abcd'
        }

        response = client.post('/menus', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_BADGE_ID"
            }
        )

    def test_menu_post_invalid_tag_error(self):
        client = Client()
        data   = {
            'category_id' : '1',
            'badge_id'    : '1',
            'tag_id'      : '2',
            'name'        : '야채샐러드',
            'description' : 'abcd'
        }

        response = client.post('/menus', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_TAG_ID"
            }
        )

    def test_menu_post_key_error(self):
        client = Client()
        data   = {
            'category_id' : '1',
            'badge_id'    : '1',
            'tag_idd'     : '1',
            'name'        : '야채샐러드',
            'description' : 'abcd'
        }

        response = client.post('/menus', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "KEY_ERROR"
            }
        )

    def test_menu_post_unauthorized_error(self):
        client = Client()
        data   = {
            'category_id' : '1',
            'badge_id'    : '1',
            'tag_id'      : '1',
            'name'        : '야채샐러드',
            'description' : 'abcd'
        }

        response = client.post('/menus', json.dumps(data), content_type = 'application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                "message" : "UNAUTHORIZED"
            }
        )
    
    def test_menu_get_success(self):
        client = Client()

        response = client.get('/menus', **headers1)

        menu_list = [{
                'id'          : 1,
                'category'    : 'SALAD',
                'name'        : 'menu1',
                'description' : 'abcd',
                'isSold'      : False,
                'badge'       : 'NEW',
                'items'       : [{
                    'id'     : 1,
                    'menuId' : 1,
                    'name'   : '라지',
                    'size'   : 'L',
                    'price'  : 9000,
                    'isSold' : False,
                }],
                'tags'        : [{
                    'id'     : 1,
                    'menuId' : 1,
                    'type'   : 'vegetarianism',
                    'name'   : '페스코베지테리언',
                }]
            },
            {
                'id'          : 2,
                'category'    : 'SALAD',
                'name'        : 'menu2',
                'description' : 'abcd',
                'isSold'      : False,
                'badge'       : 'NEW',
                'items'       : [{
                    'id'     : 2,
                    'menuId' : 2,
                    'name'   : '라지',
                    'size'   : 'L',
                    'price'  : 9000,
                    'isSold' : False,
                }],
                'tags'        : [{
                    'id'     : 1,
                    'menuId' : 2,
                    'type'   : 'vegetarianism',
                    'name'   : '페스코베지테리언',
                }]
            }]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "menus" : menu_list
            }
        )

    def test_menu_get_category_does_not_exist_error(self):
        client = Client()

        response = client.get('/menus?category_id=2', **headers1)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                'message' : 'CATEGORY_DOES_NOT_EXIST'
            }
        )
    
    def test_menu_get_unauthorized_error(self):
        client = Client()

        response = client.get('/menus')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                'message' : "UNAUTHORIZED"
            }
        )
    
    def test_menu_detail_get_success(self):
        client = Client()

        response = client.get('/menus/1', **headers1)

        menu_info =  {
            "id"          : 1,
            "category"    : "SALAD",
            "name"        : "menu1",
            "description" : "abcd",
            "isSold"      : False,
            "badge"       : "NEW",
            "items"       : [
                {
                    "id"     : 1,
                    "menuId" : 1,
                    "name"   : "라지",
                    "size"   : "L",
                    "price"  : 9000,
                    "isSold" : False
                },
            ],
            "tags" : [
                {
                    "id"     : 1,
                    "menuID" : 1,
                    "type"   : "vegetarianism",
                    "name"   : "페스코베지테리언"
                }
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "menu" : menu_info
            }
        )
    
    def test_menu_detail_get_menu_does_not_exist_error(self):
        client = Client()

        response = client.get('/menus/3', **headers1)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : "MENU_DOES_NOT_EXIST"
            }
        )
    
    def test_menu_detail_get_menu_unauthorized_error(self):
        client = Client()

        response = client.get('/menus/1')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                'message' : "UNAUTHORIZED"
            }
        )
    
    def test_menu_detail_patch_success(self):
        client = Client()

        data = {
            "name"        : "이름 수정",
            "description" : '설명 수정'
        }

        response = client.patch('/menus/1', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),
            {
                "message" : 'SUCCESS'
            }
        )
    
    def test_menu_detail_patch_menu_does_not_exist_error(self):
        client = Client()

        data = {
            "name"        : "이름 수정",
            "description" : '설명 수정'
        }

        response = client.patch('/menus/3', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : 'MENU_DOES_NOT_EXIST'
            }
        )

    def test_menu_detail_patch_forbidden_error(self):
        client = Client()

        data = {
            "name"        : "이름 수정",
            "description" : '설명 수정'
        }

        response = client.patch('/menus/1', json.dumps(data), content_type = 'application/json', **headers1)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(),
            {
                "message" : 'FORBIDDEN'
            }
        )
    
    def test_menu_detail_patch_json_decode_error(self):
        client = Client()

        response = client.patch('/menus/1', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : 'JSON_DECODE_ERROR'
            }
        )

    def test_menu_detail_delete_success(self):
        client = Client()

        response = client.delete('/menus/1', **headers2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "message" : 'SUCCESS'
            }
        )

    def test_menu_detail_delete_menu_does_not_exist_error(self):
        client = Client()

        response = client.delete('/menus/3', **headers2)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : 'MENU_DOES_NOT_EXIST'
            }
        )

    def test_menu_detail_delete_menu_forbidden_error(self):
        client = Client()

        response = client.delete('/menus/1', **headers1)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(),
            {
                "message" : 'FORBIDDEN'
            }
        )

class ItemViewTest(TestCase):
    def setUp(self):
        global headers1, headers2
        access_token  = jwt.encode({'id' : 1}, settings.SECRET_KEY, settings.ALGORITHM)
        access_token2 = jwt.encode({'id' : 2}, settings.SECRET_KEY, settings.ALGORITHM)
        headers1      = {'HTTP_Authorization': access_token}
        headers2      = {'HTTP_Authorization': access_token2}

        role1    = Role.objects.create(id = 1, name = 'USER')
        role2    = Role.objects.create(id = 2, name = 'ADMIN')
        user1    = User.objects.create(id = 1, email = 'user@freshcode.me', password = 'user', name = '김유저', role = role1)
        user2    = User.objects.create(id = 2, email = 'admin@freshcode.me', password = 'admin', name = '관리자', role = role2)
        category = Category.objects.create(id = 1, name = 'SALAD')
        badge    = Badge.objects.create(id = 1, name = 'NEW' )
        tag      = Tag.objects.create(id = 1, name = '페스코베지테리언', type = 'vegetarianism')
        menu1    = Menu.objects.create(id = 1, category = category, badge = badge, name = 'menu1', description = 'abcd')
        menu2    = Menu.objects.create(id = 2, category = category, badge = badge, name = 'menu2', description = 'abcd')
        size     = Size.objects.create(id = 1, english_name = 'L', korean_name = '라지')
        item1    = Item.objects.create(id = 1, size = size, menu = menu1, price = 9000)
        item2    = Item.objects.create(id = 2, size = size, menu = menu2, price = 9000)

        menu1.tags.add(tag)
        menu2.tags.add(tag)
    
    def tearDown(self):
        Role.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()
        Badge.objects.all().delete()
        Tag.objects.all().delete()
        Menu.objects.all().delete()
        Size.objects.all().delete()
        Item.objects.all().delete()
    
    def test_item_post_success(self):
        client = Client()

        data = {
            'menu_id' : 1,
            'size_id' : 1,
            'price'   : 9000
        }

        response = client.post('/menus/items', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),
            {
                "message" : 'SUCCESS'
            }
        )
 
    def test_item_post_forbidden_error(self):
        client = Client()

        data = {
            'menu_id' : 1,
            'size_id' : 1,
            'price'   : 9000
        }

        response = client.post('/menus/items', json.dumps(data), content_type = 'application/json', **headers1)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(),
            {
                "message" : 'FORBIDDEN'
            }
        )

    def test_item_post_unauthorized_error(self):
        client = Client()

        data = {
            'menu_id' : 1,
            'size_id' : 1,
            'price'   : 9000
        }

        response = client.post('/menus/items', json.dumps(data), content_type = 'application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                "message" : "UNAUTHORIZED"
            }
        )

    def test_item_post_json_decode_error(self):
        client = Client()

        response = client.post('/menus/items', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "JSON_DECODE_ERROR"
            }
        )

    def test_item_post_invalid_menu_error(self):
        client = Client()

        data = {
            'menu_id' : 3,
            'size_id' : 1,
            'price'   : 9000
        }

        response = client.post('/menus/items', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_MENU_ID"
            }
        )
    
    def test_item_post_invalid_size_error(self):
        client = Client()

        data = {
            'menu_id' : 1,
            'size_id' : 2,
            'price'   : 9000
        }

        response = client.post('/menus/items', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_SIZE_ID"
            }
        )

    def test_item_post_key_error(self):
        client = Client()

        data = {
            'menu_id'  : 1,
            'size_idd' : 1,
            'price'    : 9000
        }

        response = client.post('/menus/items', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "KEY_ERROR"
            }
        )

    def test_item_patch_success(self):
        client = Client()

        data = {
            'size_id'  : 1,
            'price'    : 5000,
            'is_sold'  : True,
        }

        response = client.patch('/menus/items/1', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),
            {
                "message" : "SUCCESS"
            }
        )

    def test_item_patch_unauthorized_error(self):
        client = Client()

        data = {
            'size_id'  : 1,
            'price'    : 5000,
            'is_sold'  : True,
        }

        response = client.patch('/menus/items/1', json.dumps(data), content_type = 'application/json')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                "message" : "UNAUTHORIZED"
            }
        )

    def test_item_patch_forbidden_error(self):
        client = Client()

        data = {
            'size_id'  : 1,
            'price'    : 5000,
            'is_sold'  : True,
        }

        response = client.patch('/menus/items/1', json.dumps(data), content_type = 'application/json', **headers1)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(),
            {
                "message" : "FORBIDDEN"
            }
        )

    def test_item_patch_json_decode_error(self):
        client = Client()

        response = client.patch('/menus/items/1', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "JSON_DECODE_ERROR"
            }
        )

    def test_item_patch_invalid_size_error(self):
        client = Client()

        data = {
            'size_id'  : 3,
            'price'    : 5000,
            'is_sold'  : True,
        }

        response = client.patch('/menus/items/1', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
            {
                "message" : "INVALID_SIZE_ID"
            }
        )

    def test_item_patch_item_does_not_exist_error(self):
        client = Client()

        data = {
            'size_id'  : 1,
            'price'    : 5000,
            'is_sold'  : True,
        }

        response = client.patch('/menus/items/3', json.dumps(data), content_type = 'application/json', **headers2)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : "ITEM_DOES_NOT_EXIST"
            }
        )

    def test_item_delete_success(self):
        client = Client()

        response = client.delete('/menus/items/1', **headers2)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),
            {
                "message" : "SUCCESS"
            }
        )

    def test_item_delete_unauthorized_error(self):
        client = Client()

        response = client.delete('/menus/items/1')

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),
            {
                "message" : "UNAUTHORIZED"
            }
        )

    def test_item_delete_forbidden_error(self):
        client = Client()

        response = client.delete('/menus/items/1', **headers1)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json(),
            {
                "message" : "FORBIDDEN"
            }
        )
    
    def test_item_delete_item_does_not_exist(self):
        client = Client()

        response = client.delete('/menus/items/3', **headers2)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(),
            {
                "message" : "ITEM_DOES_NOT_EXIST"
            }
        )