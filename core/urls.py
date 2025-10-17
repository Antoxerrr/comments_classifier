from django.urls import path

from core.views import IndexView, classify_view, fit_view

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('classify/', classify_view, name='classify'),
    path('fit/', fit_view, name='fit'),
]
