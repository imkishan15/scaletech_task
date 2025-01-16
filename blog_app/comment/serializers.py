from rest_framework import serializers
from .models import Comment
from django.contrib.auth import get_user_model

User = get_user_model()


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
