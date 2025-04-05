# books/urls.py
from django.urls import path
from . import views

app_name = 'books'  # এই app_name ব্যবহার করতে হবে {% url 'books:home' %} এর মত

urlpatterns = [
    path('', views.home, name='home'),
    path('book_list/', views.book_list, name='book_list'),
    path('book_detail/<int:book_id>/', views.book_detail, name='book_detail'),
    path('add_book/', views.add_book, name='add_book'),
    path('update_book/<int:book_id>/', views.update_book, name='update_book'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
]
