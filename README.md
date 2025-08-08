# Claims Management System

A lightweight web application that mimics how we analyze insurance claims at ERISA Recovery, built with robustness features and burger-themed enhancements.

## 🍔 Features

- **Claims Management**: View, search, and filter insurance claims
- **HTMX Integration**: Dynamic content loading without page refreshes
- **Alpine.js**: Lightweight JavaScript framework for interactivity
- **Robustness Features**: Enhanced error handling and user experience
- **Admin Dashboard**: Statistics and overview of claims data
- **Flag & Annotate**: Mark claims for review and add custom notes
- **Search & Filter**: Advanced search functionality for claims
- **Responsive Design**: Modern UI with Tailwind CSS

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package installer)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd claims-management-system
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**
   ```bash
   flask init-db
   ```

5. **Load sample data**
   ```bash
   flask load-sample-data
   ```

6. **Run the application**
   ```bash
   python run.py
   ```

7. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

## 🏗️ Project Structure

```
claims-management-system/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # Database models
│   ├── views.py             # Route handlers
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css    # Custom styles
│   │   └── js/
│   │       └── app.js       # Custom JavaScript
│   └── templates/
│       ├── base.html        # Base template
│       ├── index.html       # Claims list view
│       ├── claim_detail.html # Claim detail view
│       └── admin_dashboard.html # Admin dashboard
├── data/                    # Data files
├── requirements.txt         # Python dependencies
├── run.py                  # Application entry point
└── README.md              # This file
```

## 🎯 Core Features

### Claims List View
- Display all claims with ID, patient name, billed amount, paid amount, status, and insurer name
- Search functionality for claim status or insurer name
- Pagination for large datasets
- Responsive table design

### HTMX Detail View
- Show claim-specific information (CPT codes, denial reasons, notes) without full page reload
- Dynamic content loading
- Modal-based detail views

### Flag & Annotate
- Allow users to flag claims for review
- Add custom notes stored in database
- User-specific annotations
- Timestamp tracking

### Search & Filter
- Search by patient name, claim ID, or insurer
- Filter by status or insurer
- Real-time search results
- Advanced filtering options

### Admin Dashboard
- Statistics like total flagged claims, average underpayment
- Recent activity feed
- Quick action buttons
- Data export functionality

## 🍔 Burger-Themed Enhancements

This application includes special burger-themed features for enhanced robustness:

- Burger-themed color scheme
- Console messages with burger emojis
- Enhanced error handling
- Robust data validation
- User-friendly notifications

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
DATABASE_URL=sqlite:///claims_burger.db
```

### Database Configuration

The application uses SQLite by default for simplicity. For production, you can configure other databases by modifying the `SQLALCHEMY_DATABASE_URI` in `app/__init__.py`.

## 🚀 Deployment

### Development
```bash
python run.py
```

### Production
```bash
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

## 📊 API Endpoints

- `GET /` - Main claims list view
- `GET /claim/<claim_id>` - Claim detail view
- `GET /claim/<claim_id>/details` - HTMX partial for claim details
- `POST /claim/<claim_id>/flag` - Flag a claim for review
- `POST /claim/<claim_id>/note` - Add a note to a claim
- `GET /admin/dashboard` - Admin dashboard
- `GET /api/claims` - API endpoint for claims data

## 🧪 Testing

Run the application and test the following features:

1. **Claims List**: View all claims with search and filter
2. **Claim Details**: Click "View" to see detailed information
3. **Flag Claims**: Use "Review me!" button for denied claims
4. **Add Notes**: Add annotations to claims
5. **Admin Dashboard**: View statistics and recent activity

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🍔 Burger Mode

This application includes special burger-themed features for enhanced robustness and user experience. Look for burger-related console messages and enjoy the enhanced functionality!

---

**Built with ❤️ and 🍔 for robust claims management**
