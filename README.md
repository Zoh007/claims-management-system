# Claims Management System

A modern, responsive claims management system built with Django, HTMX, and Alpine.js.

## 🚀 Features

### Core Features
- **Claims List View** - Display all claims with ID, patient name, billed amount, paid amount, status, and insurer name
- **HTMX Detail View** - Show claim-specific information (CPT codes, denial reasons, notes) without full page reload
- **Flag & Annotate** - Allow users to flag claims for review and add custom notes stored in your database
- **Search & Filter** - Implement search functionality for claim status or insurer name
- **User Authentication** - Simple login system with user-specific annotations

### Bonus Features
- **Admin Dashboard** - Stats like total flagged claims, average underpayment
- **CSV Re-upload** - Support for data overwrite or append logic
- **Modern UI** - Clean, responsive design with real-time updates

## 🛠️ Technology Stack

- **Backend**: Python with Django v4+
- **Database**: SQLite (lightweight, no setup required)
- **Frontend**: HTML/CSS with HTMX and Alpine.js
- **Styling**: Tailwind CSS framework

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

### Default Admin Account
The loader ensures a working admin on each run:
- **Username**: `admin`
- **Password**: `admin123`

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

#### User Authentication
- Register new accounts
- Login with existing credentials
- User-specific annotations and flags
- Profile management

#### KPIs (on Claims page)
- Live counts for total claims, flagged claims, total billed, and underpayment
- Realtime updates via SSE when flags are added/removed

## 🔧 Management Commands

### Load Sample Data
```bash
# Import CSVs (also ensures default admin exists)
python manage.py load_sample_data

# Clear existing data and reload
python manage.py load_sample_data --clear
```

### Export Data
```bash
# Export claims as JSON (also available in UI)
python manage.py shell -c "from claims.views import export_claims_json; print('Use the export button in the UI')"

# Export claims as CSV
python manage.py shell -c "from claims.views import export_claims_csv; print('Use the export button in the UI')"
```

## 🎨 UI Features

### Modern Design
- Clean, professional interface
- Responsive design for all devices
- Real-time updates with HTMX
- Interactive components with Alpine.js

### User Experience
- Intuitive navigation
- Quick actions for common tasks
- Modal dialogs for forms
- Success/error notifications

## 🔒 Security

- User authentication and authorization
- CSRF protection
- Secure form handling
- User-specific data isolation

## 📊 Data Management

### Supported Formats
- CSV import/export
- JSON export
- Database backup/restore

### Data Validation
- Input validation and sanitization
- Error handling and user feedback
- Data integrity checks

## 🚀 Deployment

### Production Setup
1. Set `DEBUG = False` in settings
2. Configure your database (PostgreSQL recommended)
3. Set up static file serving
4. Configure your web server (nginx + gunicorn)

### Environment Variables
```bash
export SECRET_KEY='your-secret-key'
export DEBUG=False
export ALLOWED_HOSTS='your-domain.com'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
1. Check the documentation
2. Search existing issues
3. Create a new issue with details

---

Built with Django, HTMX, and Alpine.js.
