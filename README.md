# Transaction Audit Dashboard

A Django-based web application for auditing financial transactions, built as an internship task. This project leverages Django for backend logic, HTMX for dynamic frontend updates, Django REST Framework for API exposure, and Tailwind CSS for styling. 

It includes a transaction dashboard with filtering and pagination, an approval workflow, reporting with charts, and historical change tracking.

## Features

- **Transaction Dashboard**
  - View transactions with pagination (10 per page)
  - Filters: merchant, status, flagged
  - Inline actions: approve, fail, toggle flag

- **Approval Workflow**
  - Staff users can approve or fail pending transactions
  - HTMX for seamless row updates
  - Notifications for unauthorized attempts

- **Reporting**
  - Pie chart: Total amounts by status
  - Bar chart: Totals by merchant (using Chart.js)

- **Historical Tracking**
  - Records all transaction changes (status, flags) with `django-simple-history`
  - View history per transaction

- **API Endpoint**
  - REST API at `/api/transactions/`
  - Includes nested `approved_by` user and history details

- **Bonus Features**
  - Full-text search (by merchant)
  - API integration
  - Historical tracking
  - Chart.js reporting

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd transaction-audit-dashboard
```

### 2. Create a Virtual Environment

It’s recommended to create a virtual environment to manage dependencies.

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Migrations

Apply the database migrations to set up the necessary tables, including history tracking.

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

Create an admin user to access the dashboard and approve transactions.

```bash
python manage.py createsuperuser
```

### 7. Seed the Database (Optional)

Populate the database with sample data (10,000+ transactions) using the custom command.

```bash
python manage.py seed_transactions
```

### 8. Run the Development Server

Start the Django development server to run the application locally.

```bash
python manage.py runserver
```

Access the application at [http://localhost:8000/transaction-audit/](http://localhost:8000/transaction-audit/). 

API endpoint: [http://localhost:8000/api/transactions/](http://localhost:8000/api/transactions/).

## Time Log

### February 21, 2025

- **6:00 PM** – Listed project tasks in Notion.
- **6:30 PM** – Discussed logic and how to add validation rules for transactions.
- **7:00 PM** – Set up Django project, installed dependencies (`django`, `django-htmx`, `django-allauth`, `django-simple-history`).
- **10:30 PM** – Created `Transaction` model, views, and URLs with basic dashboard templates.
- **11:30 PM** – Implemented authentication using `django-allauth`, restricted access to staff users only.

### February 23, 2025

- **2:00 AM** – Set up the report page with Chart.js.
- **4:00 AM** – Added reporting with pie and bar charts.
- **5:00 AM** – Added REST API endpoint to list transaction records.
- **6:00 AM** – Added historical change tracking with `django-simple-history`.
