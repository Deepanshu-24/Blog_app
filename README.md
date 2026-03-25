# Blog_app
BlogApp is a fully functional blog platform built from scratch using FastAPI and SQLite. It allows users to register, create/edit posts, comment, like posts, and includes admin controls for managing content.

It also supports image uploads via Cloudinary, demonstrating cloud integration along with secure authentication and clean architecture—all implemented entirely by me.

Key Features:
- User authentication with hashed passwords & JWT
- Create, read, update, delete posts
- Upload images in posts with title and content
- Cloudinary integration for image uploads
- Comment and like system with duplicate prevention
- Admin capabilities for managing posts, comments, and users
- Clear API responses with proper validation

Tech Stack:
- Backend: FastAPI
- Database: SQLite with SQLAlchemy ORM, PostgreSQL(Future deployment)
- Authentication: OAuth2 + JWT
- Testing: Pytest
- Image Hosting: Cloudinary
- Python Libraries: Pydantic, Passlib, UUID, Python-Multipart

Installation:
git clone https://github.com/yourusername/blogapp.git
cd blogapp
python -m venv .venv

# Activate virtual environment:
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate

pip install -r requirements.txt
uvicorn app.main:app --reload

Open http://127.0.0.1:8000/docs to access interactive API documentation.

Database Models:
- User: id, username, email, hashed_password, is_admin
- Post: id, title, content, image_url, posted_at, user_id
- Comment: id, content, user_id, post_id, created_at, updated_at
- Like: user_id + post_id (composite key)

Future Enhancements:
- OAuth login via Google/Facebook
- Enhanced search with post title(dedicated search button)
- Speech to text search integration
