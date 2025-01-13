from django.urls import path
from .views import (
    UserBlogsView,
    BlogCreateView,
    AllBlogsView,
    BlogDetailView,
    BlogVoteView,
    BlogDeleteView,
    CommentCreateView,
    CommentVoteView,
    CommentDeleteView,
)

urlpatterns = [
    path("blogs/add/", BlogCreateView.as_view(), name="blog-list-create"),
    path("blogs/user/", UserBlogsView.as_view(), name="user-blogs"),
    path("blogs/user/draft/", UserBlogsView.as_view(), name="user-draft-blogs"),
    path("blogs/all/", AllBlogsView.as_view(), name="blog-list-view"),
    path("blogs/<int:pk>/", BlogDetailView.as_view(), name="blog-detail"),
    path("blogs/<int:blog_id>/vote/", BlogVoteView.as_view(), name="blog-vote"),
    path("blogs/<int:blog_id>/delete/", BlogDeleteView.as_view(), name="blog-delete"),
    path(
        "blogs/<int:blog_id>/comments/", CommentCreateView.as_view(), name="add_comment"
    ),
    path(
        "comments/<int:comment_id>/vote/",
        CommentVoteView.as_view(),
        name="comment-vote",
    ),
    path(
        "comments/<int:pk>/delete/", CommentDeleteView.as_view(), name="comment-delete"
    ),
]
