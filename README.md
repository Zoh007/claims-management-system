# Claims Management System

A modern, responsive claims management system built with Django, HTMX, and Alpine.js.

## 🚀 Features

### Core Features
- **Claims List View** - Display claims based on user role (assigned claims for reviewers, all claims for admins)
- **HTMX Detail View** - Show claim-specific information (CPT codes, denial reasons, notes) without full page reload
- **Flag & Annotate** - Allow users to flag claims for review and add custom notes stored in your database
- **Search & Filter** - Implement search functionality for claim status or insurer name
- **User Authentication** - Role-based login system with user-specific data access
- **Claim Assignment** - Admins and supervisors can assign claims to specific reviewers
- **Role-Based Dashboard** - Different views and statistics based on user permissions

### Bonus Features
- **Admin Dashboard** - Comprehensive statistics with real-time updates via SSE
- **CSV Re-upload** - Support for data overwrite or append logic
- **Modern UI** - Clean, responsive design with real-time updates
- **Data Export** - JSON and CSV export with role-based access control
- **Claim Assignment** - Assign claims to specific users for review
- **Real-time Notifications** - Live updates for flags and system events
- **Responsive Design** - Mobile-friendly interface with adaptive layouts

## 🛠️ Technology Stack

- **Backend**: Python with Django v4.2+
- **Database**: SQLite (lightweight, no setup required)
- **Frontend**: HTML/CSS with HTMX and Alpine.js
- **Styling**: Tailwind CSS framework (via CDN)
- **JavaScript**: Alpine.js for reactive components
- **Real-time Updates**: Server-Sent Events (SSE) for live data
- **Authentication**: Django's built-in user authentication system

## 🏗️ Project Structure

```
claims-management-system/
├── claims/                    # Main Django app
│   ├── models.py             # Data models with role-based access
│   ├── views.py              # Views with RBAC implementation
│   ├── forms.py              # Forms for user input
│   ├── admin.py              # Django admin interface
│   ├── urls.py               # URL routing
│   └── migrations/           # Database migrations
├── claims_burger/            # Django project settings
│   ├── settings.py           # Project configuration
│   └── urls.py               # Main URL configuration
├── templates/                 # HTML templates
│   ├── base.html             # Base template with navigation
│   ├── index.html            # Claims list view
│   ├── claim_detail.html     # Individual claim view
│   ├── auth/                 # Authentication templates
│   └── partials/             # HTMX partial templates
├── static/                    # Static files
│   └── css/                  # Custom CSS styles
├── bootstrap.py              # One-command setup script
├── manage.py                 # Django management script
└── requirements.txt          # Python dependencies
```

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd claims-management-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Bootstrap (one command)**
   ```bash
   python bootstrap.py               # migrate, import CSV, start server (quiet)
   # clean start
   python bootstrap.py --clear       # clears DB and re-imports your CSVs
   # append-only reupload (skip updates)
   python bootstrap.py --append
   # disable auto-reloader (avoid double-run)
   python bootstrap.py --noreload
   ```

4. **Open your browser**  
   Go to: http://127.0.0.1:8000/

## 🎯 Usage

### Quick Testing Guide

1. **Start the server**: `python manage.py runserver`
2. **Login with different accounts** to test role-based access:
   - **Admin** (`admin`/`admin123`): Full access to everything
   - **Supervisor** (`supervisor1`/`supervisor123`): Can see all claims and assign them
   - **Reviewer** (`reviewer1`/`reviewer123`): Only sees assigned claims

3. **Test different scenarios**:
   - Login as reviewer - you'll only see unassigned claims initially
   - Login as supervisor/admin - assign some claims to the reviewer
   - Login as reviewer again - now you'll see your assigned claims

### Sample User Accounts for Testing

The system includes pre-configured accounts for testing different user roles:

#### Admin Account (Full Access)
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator
- **Access**: All claims, admin dashboard, user management

#### Sample User Accounts
- **Username**: `reviewer1`
- **Password**: `reviewer123`
- **Role**: Claims Reviewer
- **Access**: Only assigned claims

- **Username**: `supervisor1`
- **Password**: `supervisor123`
- **Role**: Supervisor
- **Access**: All claims, claim assignment, basic statistics

#### Create Additional Test Accounts
```bash
# Create a new reviewer account
python manage.py shell -c "
from django.contrib.auth.models import User
from claims.models import UserProfile
user = User.objects.create_user('reviewer2', 'reviewer2@example.com', 'reviewer123')
user.first_name = 'John'
user.last_name = 'Doe'
user.save()
UserProfile.objects.create(user=user, role='reviewer', department='Claims')
print('Created reviewer2 account')
"

# Create a new supervisor account
python manage.py shell -c "
from django.contrib.auth.models import User
from claims.models import UserProfile
user = User.objects.create_user('supervisor2', 'supervisor2@example.com', 'supervisor123')
user.first_name = 'Jane'
user.last_name = 'Smith'
user.save()
UserProfile.objects.create(user=user, role='supervisor', department='Management')
print('Created supervisor2 account')
"
```

### Key Features

#### Claims List
- View all claims in a clean, sortable table
- Search claims by patient name, claim ID, or insurer
- Filter by status or insurer
- Click on any claim to view details

#### Claim Details
- View comprehensive claim information
- See CPT codes and denial reasons
- View user-specific notes and flags
- Add new notes or flag claims for review

#### User Authentication & Management
- Register new accounts with automatic role assignment
- Login with existing credentials
- User-specific annotations and flags
- Profile management with role-based permissions
- Password reset functionality
- Remember me functionality
- Session management

#### KPIs & Real-time Updates
- Live counts for total claims, flagged claims, total billed, and underpayment
- Real-time updates via Server-Sent Events (SSE) when flags are added/removed
- Role-based statistics (reviewers see only their assigned claims stats)
- Live dashboard updates for admin users
- Toast notifications for system events

## 🔌 API Endpoints

### Authentication Required Endpoints
- `GET /` - Main claims list (role-based access)
- `GET /claim/<id>/` - Claim details (role-based access)
- `POST /claim/<id>/flag/` - Flag a claim for review
- `DELETE /flag/<id>/remove/` - Remove a flag
- `POST /claim/<id>/note/` - Add a note to a claim
- `DELETE /note/<id>/remove/` - Remove a note
- `POST /claim/<id>/assign/` - Assign claim to user (admin/supervisor only)
- `GET /export/claims/json/` - Export claims as JSON
- `GET /export/claims/csv/` - Export claims as CSV

### Admin Only Endpoints
- `GET /admin/dashboard/` - Admin dashboard with statistics
- `GET /api/admin/stats/` - Admin statistics API
- `GET /events` - Server-Sent Events for real-time updates

### Public Endpoints
- `GET /auth/login/` - Login page
- `GET /auth/register/` - Registration page
- `POST /auth/login/` - Login form submission
- `POST /auth/register/` - Registration form submission
- `GET /auth/logout/` - Logout

## 🔧 Management Commands

### Load Sample Data
```bash
# Import CSVs (also ensures default admin exists)
python manage.py load_sample_data

# Clear existing data and reload
python manage.py load_sample_data --clear

# Load with sample flags and notes
python manage.py load_sample_data --samples

# Append-only mode (skip updates)
python manage.py load_sample_data --append
```

### User Management
```bash
# Create a new user with specific role
python manage.py shell -c "
from django.contrib.auth.models import User
from claims.models import UserProfile
user = User.objects.create_user('username', 'email@example.com', 'password')
user.first_name = 'First'
user.last_name = 'Last'
user.save()
UserProfile.objects.create(user=user, role='reviewer', department='Claims')
"
```

### Export Data
```bash
# Export claims as JSON (role-based access)
python manage.py shell -c "from claims.views import export_claims_json; print('Use the export button in the UI')"

# Export claims as CSV (role-based access)
python manage.py shell -c "from claims.views import export_claims_csv; print('Use the export button in the UI')"

# Export via API endpoints (requires authentication)
curl -H "Cookie: sessionid=YOUR_SESSION_ID" http://localhost:8000/export/claims/json/
curl -H "Cookie: sessionid=YOUR_SESSION_ID" http://localhost:8000/export/claims/csv/
```

## 🎨 UI Features

### Modern Design
- Clean, professional interface with medical-themed styling
- Responsive design for all devices (mobile-first approach)
- Real-time updates with HTMX for seamless user experience
- Interactive components with Alpine.js for reactive UI
- Toast notifications for user feedback
- Modal dialogs for forms and actions
- Custom scrollbars and smooth animations

### User Experience
- Intuitive navigation with role-based menu items
- Quick actions for common tasks (flag, note, assign)
- Modal dialogs for forms and actions
- Success/error notifications with toast messages
- Keyboard shortcuts and accessibility features
- Progressive disclosure of information
- Consistent design patterns throughout

## 🔒 Security & Access Control

### Role-Based Access Control (RBAC)
The system implements HIPAA-compliant access control where users only see the minimum necessary data:

- **Claims Reviewers**: Can only access claims assigned to them
- **Supervisors**: Can see all claims and assign claims to reviewers
- **Administrators**: Full system access with admin dashboard

### Security Features
- User authentication and authorization
- CSRF protection
- Secure form handling
- User-specific data isolation
- Role-based permission checks
- Audit trail for all operations

## 📊 Data Management

### Supported Formats
- CSV import/export with custom delimiter (|)
- JSON export with nested claim details
- Database backup/restore (SQLite)
- Real-time data streaming via Server-Sent Events
- HTMX partial responses for dynamic updates

### Data Validation
- Input validation and sanitization
- Error handling and user feedback
- Data integrity checks
- CSRF protection on all forms
- SQL injection prevention
- XSS protection
- Role-based data access validation

## 🚀 Deployment

### Production Setup
1. Set `DEBUG = False` in settings
2. Configure your database (PostgreSQL recommended for production)
3. Set up static file serving with proper caching
4. Configure your web server (nginx + gunicorn)
5. Set up proper logging and monitoring
6. Configure HTTPS with SSL certificates
7. Set up backup and disaster recovery procedures

### Environment Variables
```bash
export SECRET_KEY='your-secret-key'
export DEBUG=False
export ALLOWED_HOSTS='your-domain.com'
export DATABASE_URL='postgresql://user:pass@localhost/dbname'
export STATIC_ROOT='/path/to/static/files'
export MEDIA_ROOT='/path/to/media/files'
export LOG_LEVEL='INFO'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support & Troubleshooting

### Common Issues

#### Database Migration Errors
```bash
# If you encounter migration issues, reset the database:
rm db.sqlite3
python bootstrap.py --no-runserver
```

#### Permission Issues
- Ensure users have proper role assignments
- Check if UserProfile exists for each user
- Verify role permissions in admin interface

#### Real-time Updates Not Working
- Check if user has admin privileges for SSE events
- Verify browser supports Server-Sent Events
- Check console for JavaScript errors

#### Export Issues
- Ensure user is authenticated
- Check if user has access to the claims being exported
- Verify file permissions for download directory

### Getting Help

For support and questions:
1. Check this documentation thoroughly
2. Review the Django logs for error details
3. Search existing issues in the repository
4. Create a new issue with:
   - Django version
   - Python version
   - Error messages
   - Steps to reproduce
   - User role and permissions

---

Built with Django, HTMX, and Alpine.js.
