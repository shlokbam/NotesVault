# NotesVault 📚

NotesVault is a modern web application designed to facilitate academic note sharing among students. It provides a secure and efficient platform for students to upload, download, and search for academic notes across different departments and semesters.

## 🌟 Features

### User Management
- Secure user authentication and registration
- Profile management with customizable settings
- Password reset functionality via email
- User dashboard with activity tracking

### Note Management
- Upload notes in PDF and image formats (PNG, JPG, JPEG)
- Download notes with a credit-based system
- Search notes by:
  - Department
  - Semester
  - Subject
  - Keywords
- View note details and download history
- Preview functionality for uploaded notes

### Credit System
- Earn 5 credits for each note upload
- Spend 2 credits to download/view a note
- Track credit transactions
- View credit history

### Security
- Secure file uploads with size restrictions (16MB max)
- File type validation
- Protected routes with authentication
- Secure password handling

## 🛠️ Tech Stack

### Backend
- Python 3.8+
- Flask (Web Framework)
- SQLAlchemy (ORM)
- SQLite (Database)
- Flask-Login (Authentication)
- Flask-Mail (Email functionality)
- Flask-Migrate (Database migrations)

### Frontend
- Bootstrap 5 (UI Framework)
- Font Awesome (Icons)
- Responsive design for all devices
- Modern and intuitive user interface

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/NotesVault.git
   cd NotesVault
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   Create a `.env` file in the root directory with:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your-secret-key
   DATABASE_URL=sqlite:///notesvault.db
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=True
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-specific-password
   ```

5. **Initialize the database:**
   ```bash
   flask db upgrade
   ```

6. **Run the application:**
   ```bash
   flask run
   ```
   The application will be available at `http://localhost:5000`

## 📁 Project Structure

```
NotesVault/
├── app/
│   ├── models/         # Database models
│   │   ├── user.py
│   │   ├── note.py
│   │   ├── note_view.py
│   │   └── credit_transaction.py
│   ├── routes/         # Application routes
│   │   ├── auth.py
│   │   ├── notes.py
│   │   └── main.py
│   ├── static/         # Static files
│   ├── templates/      # HTML templates
│   └── utils/          # Utility functions
├── migrations/         # Database migrations
├── instance/          # Instance-specific files
├── config.py          # Configuration
├── run.py            # Application entry point
└── requirements.txt   # Dependencies
```

## 🔧 Configuration

The application can be configured through environment variables or the `config.py` file. Key configurations include:

- `SECRET_KEY`: For session security
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `UPLOAD_FOLDER`: Directory for uploaded files
- `MAX_CONTENT_LENGTH`: Maximum file upload size (16MB)
- `ALLOWED_EXTENSIONS`: Permitted file types
- `CREDITS_PER_UPLOAD`: Credits earned per upload (5)
- `CREDITS_TO_VIEW`: Credits required to view a note (2)

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Your Name - Initial work

## 🙏 Acknowledgments

- Flask documentation
- Bootstrap documentation
- SQLAlchemy documentation 