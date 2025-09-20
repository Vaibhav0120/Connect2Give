# **Connect2Give: Food Donation & Volunteer Platform**

This is the central backend repository for the Connect2Give platform, a web application designed to connect NGOs with donors and volunteers. This project is built with Django and Django REST Framework.

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

Create a .env file in the root directory (Connect2Give/). This file will store your database credentials and secret keys. Copy the contents of .env.example (if it exists) or use the template below.

```bash
# In the project root directory
touch .env
```

Open the new .env file and add the following content. You must replace the placeholder values with your actual MySQL credentials.

```bash
# .env file

# Django Settings - You can leave the default for local development
SECRET_KEY='django-insecure-your-own-secret-key-for-dev'
DEBUG=True

# Database Credentials
DB_NAME='connect2give_db'
DB_USER='your_mysql_username'   # e.g., 'root'   {ADD YOURS!}
DB_PASSWORD='your_mysql_password' # The password you set for MySQL   {ADD YOURS!}
DB_HOST='localhost'
DB_PORT='3306'
```

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

**7. Run the Development Server**

Finally, start the Django development server.

```bash
python manage.py runserver
```

The server will be running at http://127.0.0.1:8000/. You can open this address in your web browser to see the project's welcome page.

**Project Structure**
---------------------

Here is a high-level overview of the project's folder and file structure.

```bash
Connect2Give/
├── .env                       # Stores secret keys and database credentials (NEVER commit this)
├── .gitignore                 # Specifies files for Git to ignore
├── manage.py                  # Django's command-line utility for running tasks
├── requirements.txt           # Lists all Python package dependencies
|
├── food_donation_project/     # The Django project configuration folder
│   ├── __init__.py            # Configures PyMySQL driver
│   ├── settings.py            # Main project settings
│   ├── urls.py                # Main URL routing for the project
│   ├── asgi.py                # For asynchronous features (chat)
│   └── wsgi.py                # For standard web server deployment
|
├── portal/                    # The main Django app for your project's logic
│   ├── models.py              # Defines your database tables (User, NGO, etc.)
│   ├── serializers.py         # Converts models to JSON for the API
│   ├── urls.py                # API-specific URL endpoints
│   ├── views.py               # Logic for API endpoints
│   └── migrations/            # Stores database schema changes
|
└── frontend/                  # Contains all frontend HTML files and static assets
    ├── index.html
    └── assets/
        ├── css/
        ├── js/
        └── images/

```