🛒 E-commerce Backend
A robust and scalable backend for an E-commerce system built with Django and Django REST Framework (DRF).
This backend handles product management, user authentication, cart and order processing, and payment integration, with support for asynchronous task handling via Celery and Redis.

🚀 Features
Core
RESTful APIs for all resources.

User registration, authentication, and role-based permissions.

JWT-based secure authentication.

PostgreSQL as the primary relational database.

Environment variable management.

Products
Full CRUD operations for products.

Filtering, sorting, and pagination of product listings.

Carts
Add, update, and remove items from user carts.

Support for both authenticated and anonymous sessions.

Orders
Place, update, cancel and track orders.

Orders linked to user accounts.

Dynamic total calculations.

Payments
Payment model to store transaction details.

Integration with asynchronous task queue for payment processing using Celery and Redis.

Users
User profile management.

Role-based permissions (e.g., Admin, Customer).

Secure password hashing and JWT token authentication.

Performance & Reliability
Asynchronous task queue with Celery and Redis for background jobs.

Optimized database schema using Django ORM with indexing.

🛠️ Tech Stack
Backend Framework: Django, Django REST Framework

Database: PostgreSQL

Authentication: JWT (JSON Web Tokens)

Caching & Async Tasks: Redis, Celery

Filtering & Sorting: django-filter

Pagination: DRF built-in pagination

API Documentation: Swagger/OpenAPI

Environment Management: django-environ

Testing: Swagger/OpenAPI

📦 Installation
1️⃣ Clone the Repository
git clone https://github.com/your-username/ecommerce-backend.git
cd ecommerce-backend

2️⃣ Create and Activate a Virtual Environment
Linux/macOS:
python3 -m venv env
source env/bin/activate
Windows:
python -m venv env
env\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables
Create a .env file in the root directory and add your configuration variables such as:

env
DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/your_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your_jwt_secret_key

5️⃣ Run Database Migrations
python manage.py migrate

6️⃣ Create a Superuser
python manage.py createsuperuser

7️⃣ Start Redis Server (if not already running)
redis-server

8️⃣ Start Celery Worker
celery -A your_project_name worker -l info

9️⃣ Run the Development Server
python manage.py runserver

Access the API at: http://127.0.0.1:8000/

📚 API Documentation
Interactive Swagger UI: http://127.0.0.1:8000/api/docs

ReDoc Documentation: http://127.0.0.1:8000/redoc/

🔍 Key Endpoints
Root & Admin
GET / — API home with welcome message

GET /admin/ — Django admin panel

Users & Authentication
POST /api/users/ — User registration and user-related endpoints (see users.urls)

POST /api/token/ — Obtain JWT access and refresh tokens (Login)

POST /api/token/refresh/ — Refresh JWT token

POST /api/token/verify/ — Verify JWT token validity

Products
GET /api/products/ — List all products with filtering, sorting, pagination

Other product management endpoints under /api/products/ (see products.urls)

Orders
GET /api/orders/ — List user orders and order management (see orders.urls)

Cart
GET /api/cart/ — Get current user's cart and manage cart items (see carts.urls)

API Schema & Docs
GET /api/schema/ — OpenAPI schema JSON

GET /api/docs/ — Interactive Swagger UI for API documentation

python manage.py test
🧩 Additional Notes
Ensure Redis server is running for Celery background tasks.

Use Postman or Swagger UI to explore and test API endpoints.

API is secured with JWT, include tokens in Authorization headers for protected routes.
