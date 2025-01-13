from rest_framework import generics, permissions
from .models import Blog, Comment
from rest_framework import status
from rest_framework.generics import ListAPIView
from .serializers import BlogSerializer, CommentSerializer, CommentVoteSerializer
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Comment, CommentVote, BlogVote
from django.core.cache import cache
from django.utils.hashable import make_hashable

class BlogCreateView(generics.CreateAPIView):
    """
    View to create a new blog post.
    Only authenticated users can create a blog post.
    """

    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        """
        Provide the request context to the serializer.
        """
        return {"request": self.request}


class BlogDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a blog post.
    Only authenticated users can update or delete their own blog posts.
    """

    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def put(self, request, *args, **kwargs):
        """
        Updates the details of an existing blog instance.

        This method allows partial updates to the blog instance, meaning only the
        fields provided in the request body will be updated. The logged-in user
        must be the author of the blog to perform the update.

        Args:
        request (Request): The HTTP request object containing the updated data.
        pk (int): The primary key of the blog instance to be updated.
        """

        blog = self.get_object()  # Retrieve the blog instance
        serializer = BlogSerializer(
            blog, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_context(self):
        """
        Provide the comments for the blog in the serializer context.
        """
        context = super().get_serializer_context()
        blog = self.get_object()
        comments = Comment.objects.filter(
            blog=blog, parent=None
        )  # Only top-level comments
        context["comments"] = CommentSerializer(comments, many=True).data
        return context


class UserBlogsView(APIView):
    """
    View to list all blogs created by the authenticated user.
    Supports filtering by draft status (published or unpublished blogs).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Retrieve all blogs of the authenticated user, optionally filtered by draft status.
        """
        user = request.user
        is_draft = self.request.path.endswith("draft/")
        if is_draft:
            # Fetch only unpublished blogs for drafts
            user_blogs = Blog.objects.filter(author=user, is_published=False)
        else:
            # Fetch all blogs for the user
            user_blogs = Blog.objects.filter(author=user)

        serializer = BlogSerializer(user_blogs, many=True)
        return Response(serializer.data)


class AllBlogsPagination(PageNumberPagination):
    page_size = 10  # Number of blogs per page
    page_size_query_param = "page_size"
    max_page_size = 50


class AllBlogsView(ListAPIView):
    """
    View to list all published blogs with optional filtering by author, category, tags, or title.
    Supports pagination and caching of the response.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlogSerializer
    pagination_class = AllBlogsPagination

    def get(self, request, *args, **kwargs):
        """
        Retrieve a paginated list of blogs, optionally filtered by query parameters.
        The response is cached for 1 minute.
        """
        query_params = request.query_params.dict()
        tags = request.query_params.getlist("tags")
        query_params["tags"] = tags  # Include tags in cache key
        cache_key = f"all_blogs_{hash(make_hashable(query_params))}"

        # Check if data is cached
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)

        # Generate queryset and paginate
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serialized_data = self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )
            cache.set(
                cache_key, serialized_data.data, timeout=60
            )  # Cache the paginated response
            return serialized_data

        serialized_data = self.get_serializer(queryset, many=True).data
        return Response(serialized_data)

    def get_queryset(self):
        """
        Retrieve a queryset of all published blogs, optionally filtered by author, category, tags, or title.
        """
        queryset = Blog.objects.filter(is_published=True).order_by("id")

        # Filters from query parameters
        author = self.request.query_params.get("author")
        category = self.request.query_params.get("category")
        tags = self.request.query_params.getlist("tags")
        search_title = self.request.query_params.get("search_title")

        if author:
            queryset = queryset.filter(author__username=author)
        if category:
            queryset = queryset.filter(category__icontains=category)
        if tags:
            queryset = queryset.filter(tags__username__in=tags).distinct()
        if search_title:
            queryset = queryset.filter(title__icontains=search_title)

        return queryset


class BlogVoteView(APIView):
    """
    View to upvote or downvote a blog post.
    Only authenticated users can vote.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, blog_id):
        """
        Cast a vote (upvote or downvote) for a blog post.
        If the user has already voted, the vote will be updated.
        """
        blog = Blog.objects.get(id=blog_id)
        vote_type = request.data.get("vote_type")

        if vote_type not in ["upvote", "downvote"]:
            return Response(
                {"error": "Invalid vote type."}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check if the user has already voted
        existing_vote = BlogVote.objects.filter(user=request.user, blog=blog).first()
        if existing_vote:
            # Update the existing vote
            if existing_vote.vote_type != vote_type:
                # Decrement the previous vote type
                if existing_vote.vote_type == "upvote":
                    blog.upvote_count -= 1
                else:
                    blog.downvote_count -= 1

                # Increment the new vote type
                if vote_type == "upvote":
                    blog.upvote_count += 1
                else:
                    blog.downvote_count += 1

                existing_vote.vote_type = vote_type
                existing_vote.save()
                blog.save()
        else:
            # Create a new vote
            BlogVote.objects.create(user=request.user, blog=blog, vote_type=vote_type)
            if vote_type == "upvote":
                blog.upvote_count += 1
            else:
                blog.downvote_count += 1
            blog.save()

        return Response(
            {"upvotes": blog.upvote_count, "downvotes": blog.downvote_count}
        )


class BlogDeleteView(APIView):
    """
    View to delete a blog post.
    Only the author of the blog can delete the blog.
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, blog_id):
        """
        Delete the blog post if the user is the author.
        """
        blog = Blog.objects.get(id=blog_id)

        # Check if the user is the author of the blog
        if blog.author == request.user:
            blog.delete()
            return Response(
                {"message": "Blog deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        return Response(
            {"error": "You do not have permission to delete this blog."},
            status=status.HTTP_403_FORBIDDEN,
        )


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
    Only the author of the comment can delete it.
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        """
        Delete the comment if the user is the author.
        """
        comment = get_object_or_404(Comment, pk=pk)
        if comment.author == request.user:
            comment.delete()
            return Response({"message": "Comment deleted successfully"}, status=204)
        return Response(
            {"error": "You do not have permission to delete this comment"}, status=403
        )