# **Connect2Give: Food Donation & Volunteer Platform** 🍱

A comprehensive web application that connects restaurants, NGOs, and volunteers to facilitate food donation and distribution. Built to reduce food waste and help feed those in need.

## **Overview**

Connect2Give is a full-stack platform that enables:
- **Restaurants** to post surplus food donations
- **Volunteers** to pick up and deliver food donations
- **NGOs** to manage donation camps and track deliveries
- Real-time notifications and route optimization for efficient food distribution

## **Technologies Used**

### **Backend**
- **Django 5.2.7** - Web framework
- **Django REST Framework** - API development
- **MySQL** - Primary database
- **Django Allauth** - Authentication with Google OAuth
- **Channels & Redis** - WebSocket support for real-time features
- **PyWebPush** - Web push notifications

### **Frontend**
- **HTML5, CSS3, JavaScript (ES6+)**
- **Leaflet.js** - Interactive maps
- **Leaflet Routing Machine** - Route planning
- **OpenStreetMap** - Map tiles

### **Additional Tools**
- **GeoPy** - Geocoding and distance calculations
- **Pillow** - Image processing
- **django-cors-headers** - CORS handling
- **django-cleanup** - Automatic file cleanup

**Getting Started**
-------------------

Follow these instructions to get the project set up and running on your local machine for development and testing purposes.

### **Prerequisites**

Before you begin, ensure you have the following software installed on your system:

*   Git: For cloning the repository.
    
*   Python: Version 3.10 or higher.
    
*   MySQL Server: Version 8.0 or higher. Make sure the server is running.
    

### **Setup Instructions**

Follow these steps precisely to set up your development environment.

**1. Clone the Repository**

Open your terminal, navigate to the directory where you want to store the project, and clone the repository.

```bash
git clone https://github.com/Vaibhav0120/Connect2Give.git
cd Connect2Give
```

**2. Create the Environment File**

The project uses environment variables for sensitive configuration. A `.env.example` file is provided as a template.

```bash
# In the project root directory
cp .env.example .env
```

Open the `.env` file and configure the following required settings:

### **Required Environment Variables**

#### **Django Settings**
```bash
SECRET_KEY='your-secret-key-here'  # Generate using: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DEBUG=True  # Set to False in production
ALLOWED_HOSTS='localhost,127.0.0.1'  # Comma-separated list of allowed hosts
```

#### **Database Credentials**
```bash
DB_NAME='connect2give_db'
DB_USER='your_mysql_username'      # e.g., 'root'
DB_PASSWORD='your_mysql_password'  # Your MySQL password
DB_HOST='localhost'
DB_PORT='3306'
```

#### **Email Settings (Gmail SMTP)**
For email functionality, you'll need a Gmail account with an App Password:
1. Go to [Google Account App Passwords](https://myaccount.google.com/apppasswords)
2. Generate an app-specific password
3. Use that password in the configuration below:

```bash
EMAIL_BACKEND='django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER='your-email@gmail.com'
EMAIL_HOST_PASSWORD='your-app-password'  # 16-character app password
DEFAULT_FROM_EMAIL='your-email@gmail.com'
```

#### **Google OAuth (Optional)**
For Google social login:
1. Create a project at [Google Cloud Console](https://console.cloud.google.com/)
2. Enable Google+ API
3. Create OAuth 2.0 credentials
4. Add authorized redirect URIs: `http://localhost:8000/accounts/google/login/callback/`

```bash
GOOGLE_OAUTH_CLIENT_ID='your-client-id.apps.googleusercontent.com'
GOOGLE_OAUTH_CLIENT_SECRET='your-client-secret'
```

#### **Web Push Notifications (Optional)**
For browser push notifications, generate VAPID keys:

1.  **Run the script** from your activated virtual environment:

    ```bash
    python generate_keys.py
    ```

2.  **Copy the output** into your `.env` file and add your email:

    ```ini
    VAPID_PUBLIC_KEY='your-generated-public-key'
    VAPID_PRIVATE_KEY='your-generated-private-key'
    VAPID_ADMIN_EMAIL='your-email@example.com'
    ```

**⚠️ Important:** Never commit the `.env` file to version control. It's already included in `.gitignore`.

**3. Create the MySQL Database**

Log into MySQL Workbench or the MySQL command-line client and create the database that Django will use.

```bash
CREATE DATABASE connect2give_db;
```

**4. Create and Activate the Virtual Environment**

From the project root directory, create a Python virtual environment and activate it.

```bash
# For Windows (PowerShell)
python -m venv connect
.\connect\Scripts\activate.bat

# For macOS/Linux
python3 -m venv connect
source connect/bin/activate
```

**5. Install Dependencies**

With your virtual environment active, install all the required Python packages using pip.

```bash
pip install -r requirements.txt
```

**6. Run Database Migrations**

This command will connect to your database and create all the necessary tables.

```bash
python manage.py migrate
```

**7. Create a Superuser (Optional)**

Create an admin account to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin account.

**8. Run the Development Server**

Finally, start the Django development server:

```bash
python manage.py runserver
```

The server will be running at **http://127.0.0.1:8000/**

- **Main site:** http://127.0.0.1:8000/
- **Admin panel:** http://127.0.0.1:8000/admin/

## **Project Structure**

Here is a comprehensive overview of the project's folder and file structure:

```bash
Connect2Give/
├── .env                          # Environment variables (NEVER commit this!)
├── .env.example                  # Template for environment variables
├── .gitignore                    # Files to ignore in version control
├── manage.py                     # Django's command-line utility
├── requirements.txt              # Python package dependencies
├── README.md                     # Project documentation (this file)
│
├── food_donation_project/        # Django project configuration
│   ├── __init__.py
│   ├── settings.py               # Main project settings (uses django-environ)
│   ├── urls.py                   # Main URL routing
│   ├── asgi.py                   # ASGI configuration for async features
│   └── wsgi.py                   # WSGI configuration for deployment
│
├── portal/                       # Main Django application
│   ├── __init__.py
│   ├── admin.py                  # Django admin configuration
│   ├── apps.py                   # App configuration
│   ├── models.py                 # Database models (User, NGO, Restaurant, etc.)
│   ├── serializers.py            # DRF serializers for API
│   ├── forms.py                  # Django forms
│   ├── decorators.py             # Custom decorators (role-based access)
│   ├── urls.py                   # App-specific URL patterns
│   ├── tests.py                  # Test cases
│   ├── migrations/               # Database migration files
│   ├── views/                    # View modules organized by user type
│   │   ├── __init__.py
│   │   ├── auth_views.py         # Authentication views
│   │   ├── ngo_views.py          # NGO-specific views
│   │   ├── restaurant_views.py   # Restaurant-specific views
│   │   ├── volunteer_views.py    # Volunteer-specific views
│   │   └── api_views.py          # API endpoints
│   └── templatetags/             # Custom template tags
│
├── templates/                    # HTML templates
│   ├── base.html                 # Base template
│   ├── index.html                # Landing page
│   ├── auth/                     # Authentication templates
│   ├── ngo/                      # NGO dashboard templates
│   ├── restaurant/               # Restaurant dashboard templates
│   ├── volunteer/                # Volunteer dashboard templates
│   └── components/               # Reusable component templates
│
├── static/                       # Static files (CSS, JS, images)
│   ├── css/                      # Stylesheets
│   ├── js/                       # JavaScript files
│   │   ├── common.js             # Shared utility functions
│   │   ├── volunteer_pickups.js  # Volunteer pickup management
│   │   ├── cropper_map_logic.js  # Image cropping & map utilities
│   │   └── sw.js                 # Service worker for notifications
│   └── images/                   # Image assets
│
├── media/                        # User-uploaded files (created at runtime)
│   ├── profile_pictures/
│   └── banner_images/
│
└── staticfiles/                  # Collected static files (for production)
```

## **Key Features**

### **For Restaurants**
- Post food donations with quantity and pickup details
- Track donation status (pending, accepted, collected, delivered)
- View active donation camps on an interactive map
- Receive notifications when volunteers accept donations

### **For Volunteers**
- Browse and accept available food donations
- View optimal delivery routes to nearest camps
- Manage multiple pickups (up to 10 concurrent)
- Track delivery history and ratings
- Receive real-time push notifications for new donations

### **For NGOs**
- Create and manage donation camps
- Register and manage volunteers
- Verify and approve deliveries
- Rate volunteer performance
- View detailed donation statistics

## **Security Features**

✅ **Environment-based configuration** - All sensitive data in `.env` files  
✅ **Role-based access control** - Custom decorators for view protection  
✅ **CSRF protection** - Built-in Django CSRF middleware  
✅ **Secure password storage** - Django's password hashing  
✅ **OAuth integration** - Google social authentication  
✅ **SQL injection protection** - Django ORM parameterized queries

## **Performance Optimizations**

- **Optimized database queries** with `select_related()` and `prefetch_related()`
- **Database indexing** on frequently queried fields (status, assigned_volunteer, target_camp)
- **Static file serving** optimized for production
- **Lazy loading** of images and maps
- **Cached query results** where appropriate

## **API Endpoints**

Key API endpoints available:

```
POST   /donation/accept/<id>/          # Accept a donation
POST   /donation/deliver/to/<camp_id>/ # Mark donations as delivered
POST   /volunteer/register/ngo/<id>/   # Register with an NGO
POST   /volunteer/unregister/ngo/<id>/ # Unregister from an NGO
GET    /api/donations/                 # List all donations
GET    /api/camps/                     # List all active camps
```

## **Contributing**

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## **Troubleshooting**

### **Common Issues**

**MySQL Connection Error:**
```bash
# Ensure MySQL is running
sudo service mysql start

# Verify credentials in .env file
# Check DB_NAME, DB_USER, DB_PASSWORD
```

**Static Files Not Loading:**
```bash
# Collect static files
python manage.py collectstatic --noinput
```

**Migration Issues:**
```bash
# Reset migrations (⚠️ This will delete all data!)
python manage.py migrate portal zero
python manage.py migrate
```

## **License**

This project is developed for educational and social impact purposes.

## **Contact & Support**

For questions or support, please open an issue on the GitHub repository.

---

**Built with ❤️ to fight food waste and hunger**