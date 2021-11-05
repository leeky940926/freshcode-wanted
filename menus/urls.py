from django.urls import path

from menus.views import MenuView, MenuDetailView, ItemView

urlpatterns = [
    path('', MenuView.as_view()),
    path('/<int:menu_id>', MenuDetailView.as_view()),
    path('/items', ItemView.as_view()),
    path('/items/<int:item_id>', ItemView.as_view()),
]
