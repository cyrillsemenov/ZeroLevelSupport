from django.urls import path
from .views import add_article, edit_article, article_list, article_detail, similar_articles_view

urlpatterns = [
    path('add/', add_article, name='add_article'),
    path('edit/<int:pk>/', edit_article, name='edit_article'),
    path('', article_list, name='article_list'),
    path('<int:pk>/', article_detail, name='article_detail'),
    path('similar/', similar_articles_view, name='similar_articles'),
]
