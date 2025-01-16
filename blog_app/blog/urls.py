from django.urls import path
from .views import (
    UserBlogsView,
    BlogCreateView,
    AllBlogsView,
    BlogDetailView,
    BlogVoteView,
    BlogDeleteView,
)

urlpatterns = [
    path("add/", BlogCreateView.as_view(), name="blog-list-create"),
    path("user/", UserBlogsView.as_view(), name="user-blogs"),
    path("user/draft/", UserBlogsView.as_view(), name="user-draft-blogs"),
    path("all/", AllBlogsView.as_view(), name="blog-list-view"),
    path("<int:pk>/", BlogDetailView.as_view(), name="blog-detail"),
    path("<int:blog_id>/vote/", BlogVoteView.as_view(), name="blog-vote"),
    path("<int:blog_id>/delete/", BlogDeleteView.as_view(), name="blog-delete"),
]
