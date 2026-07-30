from django.urls import path
from . import views

urlpatterns = [
    path('faq/', views.FAQListCreateView.as_view()),
    path('faq/<int:pk>/', views.FAQDetailView.as_view()),
    path('testimonials/', views.TestimonialListCreateView.as_view()),
    path('testimonials/<int:pk>/', views.TestimonialDetailView.as_view()),
    path('social-feed/', views.SocialFeedPostListCreateView.as_view()),
    path('social-feed/<int:pk>/', views.SocialFeedPostDetailView.as_view()),
    path('pages/', views.StaticPageListCreateView.as_view()),
    path('pages/<int:pk>/', views.StaticPageDetailView.as_view()),
    path('pages/by-slug/<slug:slug>/', views.StaticPageDetailView.as_view()),
    path('files/', views.FileManagerFileListCreateView.as_view()),
    path('files/<int:pk>/', views.FileManagerFileDetailView.as_view()),
    path('notes/', views.NoteListCreateView.as_view()),
    path('notes/<int:pk>/', views.NoteDetailView.as_view()),
]
