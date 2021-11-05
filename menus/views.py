import json
from enum                   import Enum
from datetime               import datetime
from json.decoder           import JSONDecodeError

from django.views           import View
from django.http.response   import JsonResponse
from django.db.models       import Q
from django.db.models.query import Prefetch

from menus.models           import Badge, Category, Menu, Item, Size
from users.utils            import login_decorator

class RoleId(Enum):
    USER  = 1
    ADMIN = 2

class BadgeId(Enum):
    NEW  = 1
    SALE = 2
    HOT  = 3

class ForbiddenError(Exception):
    def __init__(self):
        super().__init__('FORBIDDEN')

class CheckId():
    def check_role_id(role_id):
        if not role_id == RoleId.ADMIN.value:
            raise ForbiddenError
    
    def check_category_id(category_id):
        if not Category.objects.filter(id = category_id).exists():
            raise Category.DoesNotExist
    
    def check_badge_id(badge_id):
        if not Badge.objects.filter(id = badge_id).exists():
            raise Badge.DoesNotExist
        
    def check_menu_id(menu_id):
        if not Menu.objects.filter(id = menu_id, deleted_at = None).exists():
            raise Menu.DoesNotExist
    
    def check_item_id(item_id):
        if not Item.objects.filter(id = item_id, deleted_at = None).exists():
            raise Item.DoesNotExist
    
    def check_size_id(size_id):
        if not Size.objects.filter(id = size_id).exists():
            raise Size.DoesNotExist
         
# 메뉴 생성, 상품 전체 조회
class MenuView(View):
    @login_decorator
    def post(self, request):
        try:
            user    = request.user
            role_id = user.role_id

            CheckId.check_role_id(role_id)
            
            data = json.loads(request.body)
            category_id = data['category_id']
            badge_id    = data.get('badge_id', BadgeId.NEW.value)

            CheckId.check_category_id(category_id)
            CheckId.check_badge_id(badge_id)

            Menu.objects.create(
                category_id = category_id,
                badge_id    = badge_id,
                name        = data['name'],
                description = data['description'],               
            )

            return JsonResponse({'message' : 'SUCCESS'}, status = 201)
        
        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        
        except ForbiddenError as e:
            return JsonResponse({'message' : str(e) }, status = 403)
        
        except Category.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_CATEGORY_ID'}, status = 400)
        
        except Badge.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_BADGE_ID'}, status = 400)

    @login_decorator
    def get(self, request):
        try:
            category_id = request.GET.get('category_id')
            page        = int(request.GET.get('page', 1))
            page_size   = 5
            limit       = page_size * page
            offset      = limit - page_size
            menu_filter = Q(deleted_at = None)

            if category_id:
                CheckId.check_category_id(category_id)
                menu_filter.add(Q(category_id = category_id), Q.AND)
        
            menus     = Menu.objects.select_related('category', 'badge',).\
                        filter(menu_filter).\
                        prefetch_related(
                            Prefetch('item_set', queryset = Item.objects.filter(deleted_at = None)), 
                             'tags', 
                             'item_set__size')[offset:limit]

            menu_list = [{
                'id'          : menu.id,
                'category'    : menu.category.name,
                'name'        : menu.name,
                'description' : menu.description,
                'isSold'      : menu.is_sold,
                'badge'       : menu.badge.name,
                'items'       : [{
                    'id'     : item.id,
                    'menuId' : menu.id,
                    'name'   : item.size.korean_name,
                    'size'   : item.size.english_name,
                    'price'  : item.price,
                    'isSold' : item.is_sold,
                }for item in menu.item_set.all()],
                'tags'        : [{
                    'id'     : tag.id,
                    'menuId' : menu.id,
                    'type'   : tag.type,
                    'name'   : tag.name,
                }for tag in menu.tags.all()]
            }for menu in menus]         

            return JsonResponse({'menus' : menu_list}, status = 200)
        
        except Category.DoesNotExist :
            return JsonResponse({'message' : 'CATEGORY_DOES_NOT_EXIST'}, status = 404)

#메뉴 개별 조회, 메뉴 수정, 메뉴 삭제
class MenuDetailView(View):
    @login_decorator
    def get(self, request, menu_id):
        try:
            CheckId.check_menu_id(menu_id)

            menu = Menu.objects.select_related('category', 'badge').\
                   prefetch_related(
                       Prefetch('item_set', queryset = Item.objects.filter(deleted_at = None)), 
                       'item_set__size', 
                       'tags').\
                    get(id = menu_id)

            menu_info = {
                'id'          : menu.id,
                'category'    : menu.category.name,
                'name'        : menu.name,
                'description' : menu.description,
                'isSold'      : menu.is_sold,
                'badge'       : menu.badge.name,
                'items'       : [{
                    'id'     : item.id,
                    'menuId' : menu.id,
                    'name'   : item.size.korean_name,
                    'size'   : item.size.english_name,
                    'price'  : item.price,
                    'isSold' : item.is_sold,
                }for item in menu.item_set.all()],
                'tags'        : [{
                    'id'     : tag.id,
                    'menuID' : menu.id,
                    'type'   : tag.type,
                    'name'   : tag.name,
                }for tag in menu.tags.all()]
                }

            return JsonResponse({'menu' : menu_info}, status = 200)
        
        except Menu.DoesNotExist :
            return JsonResponse({'message' : 'MENU_DOES_NOT_EXIST'}, status=404)
        
    @login_decorator
    def patch(self, request, menu_id):
        try:
            CheckId.check_menu_id(menu_id)
            user    = request.user
            role_id = user.role_id
            
            CheckId.check_role_id(role_id)

            data = json.loads(request.body)

            menu = Menu.objects.get(id = menu_id)

            menu.name        = data.get('name', menu.name)
            menu.description = data.get('description', menu.description)
            menu.save()

            return JsonResponse({'message' : 'SUCCESS'}, status = 201)
        
        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        
        except Menu.DoesNotExist:
            return JsonResponse({'message' : 'MENU_DOES_NOT_EXIST'}, status = 404)
        
        except ForbiddenError as e:
            return JsonResponse({'message' : str(e) }, status = 403)
    
    @login_decorator
    def delete(self, request, menu_id):
        try:
            CheckId.check_menu_id(menu_id)

            user    = request.user
            role_id = user.role_id
            
            CheckId.check_role_id(role_id)

            menu = Menu.objects.get(id = menu_id)
            
            menu.deleted_at = datetime.now()
            menu.save()

            return JsonResponse({'message' : 'SUCCESS'}, status = 200)
        
        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        
        except Menu.DoesNotExist:
            return JsonResponse({'message' : 'MENU_DOES_NOT_EXIST'}, status = 404)
        
        except ForbiddenError as e:
            return JsonResponse({'message' : str(e) }, status = 403)

# 아이템 생성, 수정, 삭제
class ItemView(View):
    @login_decorator
    def post(self, request):
        try:
            user    = request.user
            role_id = user.role_id
            
            CheckId.check_role_id(role_id)

            data = json.loads(request.body)
            menu_id = data['menu_id']
            size_id = data['size_id']

            CheckId.check_menu_id(menu_id)
            CheckId.check_size_id(size_id)

            Item.objects.create(
                menu_id = menu_id,
                size_id = size_id,
                price   = data['price'],
            )

            return JsonResponse({'message' : 'SUCCESS'}, status = 201)

        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)

        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)

        except ForbiddenError as e:
            return JsonResponse({'message' : str(e)}, status = 403)
        
        except Menu.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_MENU_ID'}, status = 400)
        
        except Size.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_SIZE_ID'}, status = 400)
    
    @login_decorator
    def patch(self, request, item_id):
        try:
            CheckId.check_item_id(item_id)

            user    = request.user
            role_id = user.role_id

            CheckId.check_role_id(role_id)

            data    = json.loads(request.body)
            item    = Item.objects.get(id = item_id)
            size_id = data.get('size_id', item.size.id)

            CheckId.check_size_id(size_id)

            item.size.id = size_id
            item.price   = data.get('price', item.price)
            item.is_sold = data.get('is_sold', item.is_sold)
            item.save()

            menu = item.menu
            
            if not Item.objects.filter(menu = menu, is_sold = False).exists():
                menu.is_sold = True
                menu.save()
            
            return JsonResponse({'message' : 'SUCCESS'}, status = 201)
        
        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        
        except Item.DoesNotExist:
            return JsonResponse({'message' : 'ITEM_DOES_NOT_EXIST'}, status = 404)
        
        except ForbiddenError as e:
            return JsonResponse({'message' : str(e) }, status = 403)
        
        except Size.DoesNotExist:
            return JsonResponse({'message' : 'INVALID_SIZE_ID'}, status = 400)

    @login_decorator
    def delete(self, request, item_id):
        try:
            CheckId.check_item_id(item_id)

            user    = request.user
            role_id = user.role_id

            CheckId.check_role_id(role_id)

            item = Item.objects.get(id = item_id)
            
            item.deleted_at = datetime.now()
            item.save()
            
            return JsonResponse({'message' : 'SUCCESS'}, status = 200)
        
        except JSONDecodeError:
            return JsonResponse({'message' : 'JSON_DECODE_ERROR'}, status = 400)
        
        except KeyError:
            return JsonResponse({'message' : 'KEY_ERROR'}, status = 400)
        
        except Item.DoesNotExist:
            return JsonResponse({'message' : "ITEM_DOES_NOT_EXIST"}, status = 404)
        
        except ForbiddenError as e:
            return JsonResponse({'message' : str(e) }, status = 403)




