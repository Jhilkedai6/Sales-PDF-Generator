# PDF Generator API

![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg) ![FastAPI](https://img.shields.io/badge/FastAPI-0.95%2B-green.svg) ![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A FastAPI-based application for generating, managing, and distributing PDF reports from HTML templates. It integrates Google OAuth authentication, SQLite for data storage, MinIO for file hosting, and email delivery via Gmail SMTP.

## Key Features

- **Authentication**: Secure login with Google OAuth 2.0 and JWT-based sessions.
- **Template Management**: Create, read, update, and delete HTML templates in SQLite.
- **PDF Generation**: Render dynamic PDFs using Jinja2 and WeasyPrint.
- **File Storage**: Store PDFs in MinIO object storage.
- **Email Delivery**: Send PDFs as email attachments using FastAPI-Mail.
- **Audit Logging**: Track user actions in the database.
- **Role-Based Access**: Restrict operations based on user roles.

## Prerequisites

- Python 3.9 or higher
- SQLite (included with Python)
- MinIO server (local or remote)
- Google Cloud OAuth 2.0 credentials
- Gmail account with an App Password

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-generator-api.git
cd pdf-generator-api
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### Sample `requirements.txt`:

```
fastapi==0.95.0
sqlalchemy==2.0.0
jinja2==3.1.2
weasyprint==58.0
python-dotenv==1.0.0
authlib==1.2.0
fastapi-mail==1.2.0
minio==7.1.0
uvicorn==0.21.0
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory:

```
CLIENT_ID=your-google-client-id
CLIENT_SECRET=your-google-client-secret
JWT_SECRET_KEY=your-jwt-secret-key
SECRET_KEY=your-oauth-state-secret
FRONTEND_URL=http://your-frontend-url
REDIRECT_URL=http://127.0.0.1:8000/auth
MAIL_USERNAME=your-gmail-email
MAIL_PASSWORD=your-gmail-app-password
```

### 5. Set Up MinIO

Run MinIO locally with Docker:

```bash
docker run -p 9000:9000 -p 9001:9001 minio/minio server /data --console-address ":9001"
```

Create a bucket named `pdf` via the MinIO console (http://127.0.0.1:9001).

## Usage

### Run the Application

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### API Endpoints

- **Login**: `GET /login` - Redirects to Google OAuth login.
- **Auth**: `GET /auth` - Handles OAuth callback and sets JWT cookie.
- **Logout**: `GET /logout` - Clears session and cookie.
- **Add Template**: `PUT /admin/Add_Template/` - Adds an HTML template (requires authentication).
- **View Templates**: `GET /admin/see` - Lists all templates.
- **Generate PDF**: `POST /admin/Make_PDF/` - Creates and emails a PDF from a template.
- **Delete Template**: `DELETE /admin/delete/` - Removes a template by ID.
- **Audit Logs**: `GET /admin/See_Audit_Logs/` - Retrieves audit logs with pagination.

### Example Request (Generate PDF)

```bash
curl -X POST "http://127.0.0.1:8000/admin/Make_PDF/" \
-H "Content-Type: application/json" \
-H "Cookie: access_token=your-jwt-token" \
-d '{
    "template_id": 1,
    "report_title": "Monthly Sales Report",
    "total_sales": 50000,
    "top_product": "Smartphone X",
    "sales_data": [
        {"product_name": "Smartphone X", "units_sold": 500, "revenue": 25000, "sales_rep": "Alice"},
        {"product_name": "Laptop Z", "units_sold": 200, "revenue": 20000, "sales_rep": "Bob"}
    ]
}'
```

## Project Structure

```
pdf-generator-api/
├── database.py       # Database setup (SQLite)
├── model.py          # SQLAlchemy models
├── main.py           # FastAPI app initialization
├── Router/           # API route modules
│   ├── auth.py       # Authentication routes
│   ├── admin.py      # Admin routes
│   ├── crud.py       # CRUD operations
│   └── delete.py     # Delete operations
├── minio.py          # MinIO integration
├── email.py          # Email configuration
├── audit.py          # Audit logging
├── .env              # Environment variables (not tracked)
└── README.md         # This file
```

## Contributing

1. **Fork** the repository.
2. **Create** a feature branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. **Commit** changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. **Push** to the branch:
   ```bash
   git push origin feature/your-feature
   ```
5. **Open** a Pull Request.

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Contact

For questions or support, open an issue on GitHub or contact 'gajurlsijan@gmail.com'

