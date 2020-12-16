from django.urls import path

from . import views


urlpatterns = [

    path('', views.index, name='index'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('register', views.register, name='register'),

    # VueJs paths
    path('dataset/<int:id>', views.index),
    path('editor/<int:id>', views.index),
    path('editor/<str:id>', views.index),

]
