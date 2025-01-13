from rest_framework import serializers
from .models import Blog, Tag, Comment, BlogVote
from django.contrib.auth import get_user_model
from rest_framework.exceptions import PermissionDenied, ValidationError


User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for the Tag model. Converts Tag instances to and from JSON format.
    """

    class Meta:
        model = Tag
        fields = "__all__"


class UpvoteDownvoteSerializer(serializers.ModelSerializer):
    """
    Serializer for BlogVote model. Handles serialization of vote types for upvotes and downvotes.
    """

    class Meta:
        model = BlogVote
        fields = ["vote_type"]


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model. Handles serialization of comments and their replies.

    Fields:
        - parent (PrimaryKeyRelatedField): Reference to the parent comment if this is a reply.
        - author (PrimaryKeyRelatedField): The author of the comment, read-only.
        - replies (SerializerMethodField): A method to retrieve all replies to the comment.

    Methods:
        - get_replies: Retrieves all child comments (replies) for the current comment.
        - create: Automatically sets the author of the comment to the logged-in user.
    """

    parent = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.all(), required=False, allow_null=True
    )
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    replies = serializers.SerializerMethodField()  # Add replies field

    class Meta:
        model = Comment
        fields = [
            "id",
            "content",
            "blog",
            "parent",
            "created_at",
            "author",
            "upvotes",
            "downvotes",
            "replies",
        ]
        read_only_fields = ["author", "created_at", "upvotes", "downvotes", "replies"]

    def get_replies(self, obj):
        """
        Retrieves all replies to the current comment, ordered by creation date.

        Args:
            obj: The current comment instance.

        Returns:
            list: A list of serialized replies.
        """
        # Get all child comments (replies) of the current comment
        replies = Comment.objects.filter(parent=obj).order_by("created_at")
        return CommentSerializer(replies, many=True).data

    def create(self, validated_data):
        """
        Automatically sets the author of the comment to the logged-in user.

        Args:
            validated_data: The validated data for the comment.

        Returns:
            Comment: The newly created comment instance.
        """
        # Automatically set the author from the context
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class CommentVoteSerializer(serializers.Serializer):
    """
    Serializer for handling upvotes and downvotes on comments.
    It validates the vote type (either 'upvote' or 'downvote').
    """

    vote_type = serializers.ChoiceField(
        choices=[("upvote", "Upvote"), ("downvote", "Downvote")]
    )


class BlogSerializer(serializers.ModelSerializer):
    """
    Serializer for the Blog model. Handles serialization of blog details, including comments, upvotes, downvotes, and tags.

    Fields:
        - tags (SlugRelatedField): A list of users associated with the blog, serialized by their username.
        - comments (SerializerMethodField): A method to retrieve all top-level comments for the blog.
        - upvotes (SerializerMethodField): A method to calculate the number of upvotes for the blog.
        - downvotes (SerializerMethodField): A method to calculate the number of downvotes for the blog.
        - comments_count (SerializerMethodField): A method to calculate the total number of comments for the blog.
    """

    tags = serializers.SlugRelatedField(
        many=True, slug_field="username", queryset=User.objects.all()
    )
    comments = serializers.SerializerMethodField()
    upvotes = serializers.SerializerMethodField()
    downvotes = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            "id",
            "title",
            "content",
            "category",
            "author",
            "tags",
            "is_published",
            "comments_count",
            "comments",
            "upvotes",
            "downvotes",
        ]
        read_only_fields = ["author", "upvotes", "downvotes"]

    def get_comments(self, obj):
        """
        Retrieves all top-level comments for the blog, ordered by creation date.

        Args:
            obj: The current blog instance.

        Returns:
            list: A list of serialized top-level comments.
        """
        # Get only top-level comments (comments without a parent)
        top_level_comments = Comment.objects.filter(blog=obj, parent=None).order_by(
            "created_at"
        )
        return CommentSerializer(top_level_comments, many=True).data

    def get_upvotes(self, obj):
        """
        Calculates the number of upvotes for the blog.

        Args:
            obj: The current blog instance.

        Returns:
            int: The total number of upvotes.
        """
        return BlogVote.objects.filter(blog=obj, vote_type="upvote").count()

    def get_downvotes(self, obj):
        """
        Calculates the number of downvotes for the blog.

        Args:
            obj: The current blog instance.

        Returns:
            int: The total number of downvotes.
        """
        return BlogVote.objects.filter(blog=obj, vote_type="downvote").count()

    def get_comments_count(self, obj):
        """
        Calculates the total number of comments for the blog.

        Args:
            obj: The current blog instance.

        Returns:
            int: The total number of comments.
        """
        return Comment.objects.filter(blog=obj).count()

    def create(self, validated_data):
        """
        Creates a new blog and associates it with the logged-in user.

        Args:
            validated_data: The validated data for the blog.

        Returns:
            Blog: The newly created blog instance.
        """
        tags = validated_data.pop("tags", [])
        author = self.context[
            "request"
        ].user  # Get the logged-in user from the request context
        blog = Blog.objects.create(author=author, **validated_data)
        blog.tags.set(tags)
        return blog

    def update(self, instance, validated_data):
        """
        Updates an existing blog with new data, preserving tags.

        Args:
            instance: The existing blog instance to update.
            validated_data: The validated data for the blog.

        Returns:
            Blog: The updated blog instance.
        """
        request_user = self.context["request"].user
        if instance.author != request_user:
            raise PermissionDenied("You are not the author of this blog.")

        # Allowed fields for update
        allowed_fields = {"title", "content", "category", "tags", "is_published"}
        invalid_fields = set(validated_data.keys()) - allowed_fields

        if invalid_fields:
            raise ValidationError(
                {
                    field: "This field is not allowed for update."
                    for field in invalid_fields
                }
            )

        tags = validated_data.pop("tags", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if tags is not None:
            instance.tags.set(tags)
        instance.save()
        return instance

    def validate_tags(self, tags):
        """
        Validates that all tags exist as users.

        Args:
            tags: A list of usernames associated with the blog.

        Returns:
            list: The validated list of tags.

        Raises:
            ValidationError: If any of the tags do not exist as users.
        """
        for username in tags:
            if not User.objects.filter(username=username).exists():
                raise serializers.ValidationError(f"User '{username}' does not exist.")
        return tags
