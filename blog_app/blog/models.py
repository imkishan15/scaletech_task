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
