# Project Introduction

## Overview

This project is a comprehensive blogging platform designed to provide users with a seamless experience for creating, managing, and interacting with blogs. It features robust user authentication, blog management, comment handling, and voting functionality. Built using Django Rest Framework (DRF), the platform ensures scalability and security.

## Key Features

### 1. **User Management**

- **Registration**: New users can register to create an account.
- **Authentication**: Secure login with JWT-based token authentication.
- **Profile Management**: Users can view and manage their profile details.

### 2. **Blog Management**

- **Create Blogs**: Authenticated users can create blogs with detailed content, categories, and tags.
- **Drafts**: Users can save unpublished blogs as drafts.
- **View Blogs**: A paginated list of all published blogs with filtering options.
- **Edit/Delete Blogs**: Users can update or delete their blogs.
- **Vote on Blogs**: Users can upvote or downvote blogs.

### 3. **Comment System**

- **Add Comments**: Users can add comments to blogs.
- **Nested Comments**: Supports replies to comments, creating a thread-like structure.
- **Vote on Comments**: Users can upvote or downvote comments.
- **Delete Comments**: Users can delete their own comments.

### 4. **Caching and Pagination**

- **Caching**: Blog listing endpoints are optimized using caching to improve performance.
- **Pagination**: Blogs and comments are paginated to ensure efficient data retrieval.

## Technology Stack

### Backend

- **Django**: Web framework for rapid development.
- **Django Rest Framework (DRF)**: For building RESTful APIs.
- **SQLite**: Default database for development (can be replaced with PostgreSQL/MySQL in production).

### Authentication

- **JWT (JSON Web Tokens)**: Secure user authentication.

### Additional Tools

- **Django Caching**: For optimizing frequently accessed data.
- **DRF Serializers**: For transforming querysets into JSON.
- **DRF Permissions**: To enforce access control.

## Project Structure

### Core Modules

- **Authentication**: Handles user registration, login, and token management.
- **Blogs**: Manages blog creation, listing, and voting.
- **Comments**: Handles comment creation, voting, and deletion.

### File Organization

- `models.py`: Defines the database schema.
- `views.py`: Contains logic for handling API requests.
- `serializers.py`: Converts data between Python objects and JSON.
- `urls.py`: Maps URLs to their respective views.

## API Documentation

Detailed API documentation is available in the `api_endpoints.md` file, which outlines all endpoints, their methods, and expected payloads.

## Database Setup

Detailed API documentation is available in the `database_setup.md` file

## Getting Started

### Prerequisites

- Python 3.8+
- Django 4.0+
- DRF 3.12+


### Installation

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```
2. Create a virtual environment 
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment
   ```bash
   # For mac:
   source venv/bin/activate

   # For Windows:
   venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```bash
   cd ./blog_app
   python manage.py makemigrations
   python manage.py migrate
   ```
5. Run the development server:
   ```bash
   python manage.py runserver
   ```
