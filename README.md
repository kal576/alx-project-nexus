🛒 **E-commerce Backend**
A robust and scalable backend for an E-commerce system built with Django and Django REST Framework (DRF).
This backend handles product management, user authentication, cart and order processing, and payment integration, with support for asynchronous task handling via Celery and Redis.

🚀 **Features**
**Core**
  - RESTful APIs for all resources

  - User registration, authentication, and role-based permissions

  - JWT-based secure authentication

  - PostgreSQL as the primary relational database

  - Environment variable management

**Products**
Full CRUD operations for products

Filtering, sorting, and pagination of product listings

**Carts**
Add, update, and remove items from user carts

Support for both authenticated and anonymous sessions

**Orders**
Place, update, cancel, and track orders

Orders linked to user accounts

Dynamic total calculations

**Payments**
Payment model to store transaction details

Integration with asynchronous task queue for payment processing using Celery and Redis

**Users**
User profile management

Role-based permissions (e.g., Admin, Customer)

Secure password hashing and JWT token authentication

**Performance & Reliability**
Asynchronous task queue with Celery and Redis for background jobs

Optimized database schema using Django ORM with indexing

🛠️ **Tech Stack**
  - Backend Framework: Django, Django REST Framework

  - Database: PostgreSQL

  - Authentication: JWT (JSON Web Tokens)

  - Caching & Async Tasks: Redis, Celery

  - Filtering & Sorting: django-filter

  - Pagination: DRF built-in pagination

  - API Documentation: Swagger/OpenAPI

  - Environment Management: django-environ

  - Testing: Swagger/OpenAPI

📦 **Installation**
**Clone the repository**
Run git clone https://github.com/your-username/ecommerce-backend.git
Then move into the project directory by running cd ecommerce-backend.

**Create a virtual environment**

On Linux/macOS, run python3 -m venv env

On Windows, run python -m venv env

**Activate the virtual environment**
On Linux/macOS, run source env/bin/activate

On Windows, run env\Scripts\activate

**Install the project dependencies**
Run pip install -r requirements.txt.

**Set up environment variables**
Create a .env file in the root directory and add your configuration variables, for example:

DEBUG=True
SECRET_KEY=your_secret_key
DATABASE_URL=postgres://user:password@localhost:5432/your_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
JWT_SECRET_KEY=your_jwt_secret_key

**Apply database migrations**
Run python manage.py migrate.

**Create a superuser(optional)**
Run python manage.py createsuperuser and follow the prompts.

**Start the Redis server (if not already running)**
Run redis-server.

**Start the Celery worker for asynchronous tasks**
Run celery -A your_project_name worker -l info.

**Run the Django development server**
Run python manage.py runserver.

The API will be accessible at http://127.0.0.1:8000/.

📚 **API Documentation**
Interactive Swagger UI: http://127.0.0.1:8000/api/docs

ReDoc Documentation: http://127.0.0.1:8000/redoc/

🔍 ****Key Endpoints**
Root & Admin**
GET / — API home with welcome message

GET /admin/ — Django admin panel

**Users & Authentication**
POST /api/users/ — User registration and related endpoints (see users.urls)

POST /api/token/ — Obtain JWT access and refresh tokens (Login)

POST /api/token/refresh/ — Refresh JWT token

POST /api/token/verify/ — Verify JWT token validity

**Products**
GET /api/products/ — List all products with filtering, sorting, pagination

Other product management endpoints under /api/products/ (see products.urls)

**Orders**
GET /api/orders/ — List user orders and manage orders (see orders.urls)

**Cart**
GET /api/cart/ — Get current user's cart and manage cart items (see carts.urls)

**API Schema & Docs**
GET /api/schema/ — OpenAPI schema JSON

GET /api/docs/ — Interactive Swagger UI for API documentation

🧩 **Additional Notes**
Ensure the Redis server is running before starting Celery workers for background tasks.

Use Postman or Swagger UI to explore and test API endpoints.

Include JWT tokens in the Authorization header when accessing protected routes.
