from django.urls import path

from .views import RegisterView, UserLoginView, UserLogoutView, AccountView, AccountEditView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),

    path('account/personal_cabinet/<int:pk>/', AccountView.as_view(), name='personal-cabinet'),
    path('account/personal_cabinet/profile_edit/', AccountEditView.as_view(), name='profile-edit')
]
