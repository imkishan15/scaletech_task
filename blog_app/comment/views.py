from rest_framework import permissions
from .models import Comment
from blog.models import Blog
from rest_framework import status
from .serializers import CommentSerializer, CommentVoteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Comment, CommentVote


class CommentCreateView(APIView):
    """
    View to create a comment on a blog post.
    Supports both top-level comments and replies to other comments.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, blog_id):
        """
        Create a new comment or reply to an existing comment.
        """
        try:
            blog = Blog.objects.get(id=blog_id)
        except Blog.DoesNotExist:
            return Response(
                {"error": "Blog not found."}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.data
        data["blog"] = blog.id

        # Check if the comment is a reply to another comment (nested comment)
        if "parent" in data and data["parent"] is not None:
            try:
                parent_comment = Comment.objects.get(id=data["parent"])
            except Comment.DoesNotExist:
                return Response(
                    {"error": "Parent comment not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if parent_comment.blog != blog:
                return Response(
                    {"error": "Parent comment must belong to the same blog."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = CommentSerializer(data=data, context={"request": request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentVoteView(APIView):
    """
    View to upvote or downvote a comment.
    Only authenticated users can vote.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, comment_id):
        """
        Cast a vote (upvote or downvote) for a comment.
        If the user has already voted, the vote will be updated.
        """
        comment = get_object_or_404(Comment, id=comment_id)
        user = request.user

        # Validate the request data
        serializer = CommentVoteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        vote_type = serializer.validated_data["vote_type"]

        # Check if the user has already voted on this comment
        existing_vote = CommentVote.objects.filter(user=user, comment=comment).first()

        if existing_vote:
            if existing_vote.vote_type == vote_type:
                return Response(
                    {"error": "You have already cast this vote."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                # Update the existing vote and adjust counts
                if existing_vote.vote_type == "upvote":
                    comment.upvotes = max(comment.upvotes - 1, 0)
                elif existing_vote.vote_type == "downvote":
                    comment.downvotes = max(comment.downvotes - 1, 0)

                # Update the vote type
                existing_vote.vote_type = vote_type
                existing_vote.save()

                if vote_type == "upvote":
                    comment.upvotes += 1
                elif vote_type == "downvote":
                    comment.downvotes += 1

                comment.save()
                return Response(
                    {"message": f"Your vote has been updated to {vote_type}."}
                )

        # Create a new vote
        CommentVote.objects.create(user=user, comment=comment, vote_type=vote_type)

        # Update the upvote/downvote count
        if vote_type == "upvote":
            comment.upvotes += 1
        elif vote_type == "downvote":
            comment.downvotes += 1

        comment.save()

        return Response({"message": f"You have successfully {vote_type}d the comment."})


class CommentDeleteView(APIView):
    """
    View to delete a comment.
    Only the author of the comment or superuser can delete it.
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        """
        Delete the comment if the user is the author or superuser.
        """
        comment = get_object_or_404(Comment, pk=pk)
        if comment.author == request.user or request.user.is_superuser:
            comment.delete()
            return Response({"message": "Comment deleted successfully"}, status=204)
        return Response(
            {"error": "You do not have permission to delete this comment"}, status=403
        )
