from django.urls import path
from .views import (
    CommentCreateView,
    CommentVoteView,
    CommentDeleteView,
)

urlpatterns = [
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
