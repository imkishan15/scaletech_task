from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Comment(models.Model):
    """
    Represents a comment on a blog post.

    Attributes:
        blog (Blog): The blog post to which the comment belongs.
        author (User): The author of the comment.
        content (str): The content of the comment.
        created_at (datetime): The date and time when the comment was created.
        parent (Comment): The parent comment if this is a reply, otherwise None.
        upvotes (int): The number of upvotes the comment has received.
        downvotes (int): The number of downvotes the comment has received.
    """

    blog = models.ForeignKey(
        "blog.Blog", on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # ForeignKey to User model
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.CASCADE, related_name="replies"
    )
    upvotes = models.PositiveIntegerField(default=0)
    downvotes = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Comment by {self.author} on {self.blog}"


class CommentVote(models.Model):
    """
    Represents a vote on a comment (either upvote or downvote).

    Attributes:
        user (User): The user who cast the vote.
        comment (Comment): The comment being voted on.
        vote_type (str): The type of vote, either 'upvote' or 'downvote'.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="votes")
    vote_type = models.CharField(
        max_length=10, choices=[("upvote", "Upvote"), ("downvote", "Downvote")]
    )

    class Meta:
        unique_together = (
            "user",
            "comment",
        )  # Ensure one user can vote only once per comment
