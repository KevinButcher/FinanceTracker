from . import views
from django.urls import path

app_name = 'finances'
urlpatterns = [
    #/finances/
    path('home', views.home, name="home"),
    path('add', views.create_transaction, name="create_transaction"),
    path('update/<int:id>', views.update_transaction, name="update_transaction"),
    path('view', views.view_transaction, name="view_transaction"),
    path('detail/<int:id>', views.detail_transaction, name="detail_transaction"),
    path('delete/<int:id>', views.delete_transaction, name="delete_transaction"),
]