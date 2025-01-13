from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Blog(models.Model):
    """
    Represents a blog post.

    Attributes:
        title (str): The title of the blog post.
        publication_date (datetime): The date and time when the blog was published.
        author (User): The author of the blog post, linked to the User model.
        content (str): The content of the blog post.
        category (str): The category to which the blog post belongs.
        tags (ManyToManyField): Tags related to the blog post, represented by users.
        is_published (bool): Whether the blog post is published or not.
        upvote_count (int): The number of upvotes the blog post has received.
        downvote_count (int): The number of downvotes the blog post has received.
    """

    title = models.CharField(max_length=255)
    publication_date = models.DateTimeField(null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blogs")
    content = models.TextField()
    category = models.CharField(max_length=100)
    tags = models.ManyToManyField(User, related_name="Tags", blank=True)
    is_published = models.BooleanField(default=False)
    upvote_count = models.PositiveIntegerField(default=0)
    downvote_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Tag(models.Model):
    """
    Represents a tag that can be associated with blogs.

    Attributes:
        name (str): The name of the tag.
    """

    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


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

    blog = models.ForeignKey("Blog", on_delete=models.CASCADE, related_name="comments")
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
    comment = models.ForeignKey(
        "Comment", on_delete=models.CASCADE, related_name="votes"
    )
    vote_type = models.CharField(
        max_length=10, choices=[("upvote", "Upvote"), ("downvote", "Downvote")]
    )

    class Meta:
        unique_together = (
            "user",
            "comment",
        )  # Ensure one user can vote only once per comment


class BlogVote(models.Model):
    """
    Represents a vote on a blog post (either upvote or downvote).

    Attributes:
        user (User): The user who cast the vote.
        blog (Blog): The blog post being voted on.
        vote_type (str): The type of vote, either 'upvote' or 'downvote'.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    vote_type = models.CharField(
        max_length=10, choices=[("upvote", "Upvote"), ("downvote", "Downvote")]
    )

    class Meta:
        unique_together = ("user", "blog")  # Ensure one vote per user per blog

    def __str__(self):
        return f"{self.user.username} {self.vote_type} for {self.blog.title}"
