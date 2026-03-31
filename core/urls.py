from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('company/upload/', views.company_upload, name='company_upload'),
    path('company/results/', views.company_results, name='company_results'),
    path('annotator/', views.annotator_dashboard, name='annotator_dashboard'),
]
