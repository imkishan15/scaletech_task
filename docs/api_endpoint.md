# API Endpoints Documentation

## Authentication Endpoints

**Base Url:** ```http://127.0.0.1:8000/api/users```

### Register
**URL:** `/register/`  
**Method:** `POST`  
**View:** `RegisterUserView`  
**Description:** Register a new user.  
**Request Body:**
```json
{
    "username": "string",
    "password": "string",
    "email": "string"
}
```

---

### Login
**URL:** `/login/`  
**Method:** `POST`  
**View:** `TokenObtainPairView`  
**Description:** Obtain an access and refresh token.  
**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

---

### Token Refresh
**URL:** `/token/refresh/`  
**Method:** `POST`  
**View:** `TokenRefreshView`  
**Description:** Refresh the access token using the refresh token.  
**Request Body:**
```json
{
    "refresh": "string"
}
```

---

### User Profile
**URL:** `/profile/`  
**Method:** `GET`  
**View:** `UserProfileView`  
**Description:** Retrieve the profile details of the logged-in user.  
**Authentication:** Required

### Update User Profile

**URL:** `PUT /profile/`

### Description
This endpoint allows the authenticated user to update their profile details. Partial updates are supported, meaning only the fields provided in the request body will be updated.

### Authentication
- **Required**: Yes
- **Type**: JWT Token (Bearer Authentication)

### Request Body
The request body should include only the fields that need to be updated. All fields are optional, and any combination of the following fields can be included:

| Field            | Type     | Required | Description                           |
|-------------------|----------|----------|---------------------------------------|
| `username`        | `string` | No       | The username of the user.            |
| `email`           | `string` | No       | The email address of the user.       |
| `bio`             | `string` | No       | A brief biography of the user.       |
| `phone_number`    | `string` | No       | The phone number of the user.        |
| `profile_picture` | `string` | No       | Base64-encoded profile picture image.|

#### Note:
- The `profile_picture` field must be in the format:  
  `data:image/png;base64,{base64_string}`

### Responses

#### Success Response
- **Status Code**: `200 OK`
- **Body**:
  ```json
  {
      "username": "updated_username",
      "email": "updated_email@example.com",
      "bio": "Updated bio",
      "phone_number": "1234567890",
      "profile_picture": "data:image/png;base64,base64_encoded_string"
  }

---

## Blog Endpoints

**Base Url:** ```http://127.0.0.1:8000/api/blogs```

### Add Blog
**URL:** `/blogs/add/`  
**Method:** `POST`  
**View:** `BlogCreateView`  
**Description:** Create a new blog post.  
**Authentication:** Required  
**Request Body:**
```json
{
    "title": "string",
    "content": "string",
    "category": "string",
    "tags": ["string", "string"],
    "is_published": "boolean"
}
```
---

### View All Blogs

**URL:** `/blogs/all/`  
**Method:** GET  
**View:** AllBlogsView  
**Description:** Retrieve all published blogs with optional filters (e.g., author, category, tags). The response includes blog details such as comments, upvotes, downvotes, and metadata. Pagination is supported using page and page_size query parameters to limit the number of results per page.  

**Authentication:** Required  

**Query Parameters:**  
- author: Filter by author's username.  
- category: Filter by category.  
- tags: Filter by tags.  
- search_title: Search by blog title.  
- page: The page number for pagination (default: 1).  
- page_size: The number of results per page (default: 10).  

**Response Example:**  
```json 
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Tech Innovations in 2025",
            "content": "This blog discusses the latest technological innovations in 2025.",
            "category": "Technology",
            "author": 2,
            "tags": [
                "techguru",
                "innovator"
            ],
            "is_published": true,
            "comments_count": 2,
            "comments": [
                {
                    "id": 101,
                    "content": "Great insights on technology!",
                    "blog": 1,
                    "parent": null,
                    "created_at": "2025-01-10T14:20:00Z",
                    "author": 3,
                    "upvotes": 5,
                    "downvotes": 0,
                    "replies": [
                        {
                            "id": 102,
                            "content": "Thanks! Glad you liked it.",
                            "blog": 1,
                            "parent": 101,
                            "created_at": "2025-01-10T15:00:00Z",
                            "author": 2,
                            "upvotes": 2,
                            "downvotes": 0,
                            "replies": []
                        }
                    ]
                },
                {
                    "id": 103,
                    "content": "Looking forward to more posts like this.",
                    "blog": 1,
                    "parent": null,
                    "created_at": "2025-01-11T10:00:00Z",
                    "author": 4,
                    "upvotes": 3,
                    "downvotes": 2,
                    "replies": []
                }
            ],
            "upvotes": 15,
            "downvotes": 1
        },
        {
            "id": 2,
            "title": "The Art of Minimalism",
            "content": "This blog explores how minimalism can simplify life and enhance productivity.",
            "category": "Lifestyle",
            "author": 4,
            "tags": [
                "minimalist",
                "lifestyle"
            ],
            "is_published": true,
            "comments_count": 1,
            "comments": [
                {
                    "id": 201,
                    "content": "This resonates with me. Thanks for sharing!",
                    "blog": 2,
                    "parent": null,
                    "created_at": "2025-01-12T08:30:00Z",
                    "author": 5,
                    "upvotes": 4,
                    "downvotes": 0,
                    "replies": []
                }
            ],
            "upvotes": 8,
            "downvotes": 0
        }
    ]
}
```

---

### View User Blogs
**URL:** `/blogs/user/`  
**Method:** `GET`  
**View:** `UserBlogsView`  
**Description:** Retrieve blogs authored by the logged-in user.  
**Authentication:** Required  

---

### View Specific Blog
**URL:** `/blogs/<int:blog_id>/`  
**Method:** `GET`  
**View:** `UserBlogsView`  
**Description:** Retrieve specific blogs by given id.  
**Authentication:** Required  

---

### User Draft Blogs
**URL:** `/blogs/user/draft/`  
**Method:** `GET`  
**View:** `UserBlogsView`  
**Description:** Retrieve draft blogs authored by the logged-in user.  
**Authentication:** Required  

---

### Edit Blog
**URL:** `/blogs/<int:blog_id>/`  
**Method:** `PUT`  
**View:** `UserBlogsView`  
**Description:** Updates an existing blog with new data by passing only fields that are allowed.  
**Allowed fields:** `["title", "content", "category", "tags", "is_published"]`  
**Authentication:** Required  
**Request Body:**
```json
{
    "is_published": "true",
    "content": "This content has been edited!"
}
``` 

---

### Blog Voting
**URL:** `/comments/<int:comment_id>/vote/`  
**Method:** `POST`  
**View:** `BlogVoteView`  
**Description:** Upvote or downvote a blog.  
**Authentication:** Required  
**Request Body:**
```json
{
    "vote_type": "upvote" | "downvote"
}
```

---

### Blog Deletion
**URL:** `/blogs/<int:blog_id>/delete/`  
**Method:** `DELETE`  
**View:** `BlogDeleteView`  
**Description:** Delete a blog authored by the logged-in user.  
**Authentication:** Required  

---

### Add Comment
**URL:** `/blogs/<int:blog_id>/comments/`  
**Method:** `POST`  
**View:** `CommentCreateView`  
**Description:** Add a comment to a blog.  
**Authentication:** Required  
**Request Body:**
```json
{
    "content": "string",
    "parent": "integer | null"
}
```

---

### Comment Voting
**URL:** `/comments/<int:comment_id>/vote/`  
**Method:** `POST`  
**View:** `CommentVoteView`  
**Description:** Upvote or downvote a comment.  
**Authentication:** Required  
**Request Body:**
```json
{
    "vote_type": "upvote" | "downvote"
}
```

---

### Comment Deletion
**URL:** `/comments/<int:pk>/delete/`  
**Method:** `DELETE`  
**View:** `CommentDeleteView`  
**Description:** Delete a comment authored by the logged-in user.  
**Authentication:** Required  

---

