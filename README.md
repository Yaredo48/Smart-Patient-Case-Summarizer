# Smart Patient Case Summarizer

An AI-powered healthcare application that automates the summarization of patient medical records, lab reports, and clinical notes using advanced OCR and GPT-4 technology.

## Features

- 🔐 **Secure Authentication**: JWT-based user authentication
- 👥 **Patient Management**: Create, view, and search patient records
- 📄 **Document Processing**: Upload PDFs, images, and Word documents with automatic OCR
- 🤖 **AI Summarization**: GPT-4-powered clinical summaries with red flag detection
- 🚩 **Red Flag Detection**: Automatic highlighting of critical values and abnormalities
- 📊 **Lab Results Extraction**: Structured extraction of laboratory values
- 💊 **Medication Tracking**: Automatic medication list generation
- 📱 **Responsive UI**: Modern Material-UI interface

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **PostgreSQL**: Relational database
- **SQLAlchemy**: ORM for database operations
- **Tesseract OCR**: Text extraction from images and PDFs
- **OpenAI GPT-4**: AI-powered summarization
- **Redis**: Caching and background tasks
- **Docker**: Containerization

### Frontend
- **React 18**: UI library
- **TypeScript**: Type-safe JavaScript
- **Material-UI**: Component library
- **React Router**: Client-side routing
- **React Query**: Data fetching and caching
- **Axios**: HTTP client
- **Vite**: Build tool

## Prerequisites

- Docker and Docker Compose
- OpenAI API key
- (Optional) Node.js 18+ and Python 3.11+ for local development

## Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Smart-Patient-Case-Summarizer
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   ```

3. **Edit backend/.env and add your OpenAI API key**
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

4. **Start all services with Docker Compose**
   ```bash
   docker-compose up --build
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## Local Development (Without Docker)

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Tesseract OCR**
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr poppler-utils`
   - macOS: `brew install tesseract poppler`
   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

5. **Set up PostgreSQL database**
   ```bash
   # Create database
   createdb patient_summarizer
   ```

6. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

7. **Run the backend**
   ```bash
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set API URL (optional)**
   ```bash
   echo "VITE_API_URL=http://localhost:8000" > .env
   ```

4. **Start development server**
   ```bash
   npm run dev
   ```

## Usage

### 1. Register an Account
- Navigate to http://localhost:5173/register
- Create a doctor account

### 2. Create a Patient
- Click "New Patient" on the dashboard
- Fill in patient information (MRN, name, DOB, etc.)

### 3. Upload Documents
- Click on a patient to view details
- Drag and drop medical documents (PDFs, images, Word docs)
- Wait for OCR processing (status will change to "completed")

### 4. Generate Summary
- Once documents are processed, click "Generate" button
- AI will analyze documents and create a clinical summary
- Red flags and abnormal values will be highlighted

### 5. Review Summary
- View comprehensive clinical summary
- Check red flags and critical findings
- Review structured lab results and medications

## API Documentation

Once the backend is running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login
- `GET /api/patients/` - List patients
- `POST /api/patients/` - Create patient
- `POST /api/documents/upload/{patient_id}` - Upload document
- `POST /api/summaries/generate/{patient_id}` - Generate summary

## Project Structure

```
Smart-Patient-Case-Summarizer/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   ├── core/          # Configuration, security, database
│   │   ├── models/        # Database models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic (OCR, AI, storage)
│   │   └── main.py        # FastAPI application
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API client
│   │   ├── contexts/      # React contexts (Auth)
│   │   ├── types/         # TypeScript types
│   │   └── main.tsx       # Entry point
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Configuration

### Environment Variables

**Backend (.env)**:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `OPENAI_API_KEY`: Your OpenAI API key
- `OPENAI_MODEL`: GPT model to use (default: gpt-4-turbo-preview)
- `UPLOAD_DIR`: Directory for uploaded files
- `REDIS_URL`: Redis connection string

**Frontend (.env)**:
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## Security Considerations

⚠️ **Important for Production**:

1. **Change the SECRET_KEY** in backend/.env to a strong random string
2. **Use HTTPS** for both frontend and backend
3. **Configure CORS** properly for your domain
4. **Set up proper firewall rules**
5. **Enable database encryption**
6. **Implement rate limiting**
7. **Regular security audits**
8. **HIPAA compliance** if handling real patient data

## Troubleshooting

### OCR not working
- Ensure Tesseract is installed: `tesseract --version`
- Check Tesseract is in PATH
- For Docker, rebuild image: `docker-compose build backend`

### Database connection errors
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

### API authentication errors
- Check if token is expired (30 min default)
- Verify SECRET_KEY matches between sessions
- Clear browser localStorage and re-login

### File upload failures
- Check MAX_UPLOAD_SIZE setting
- Verify UPLOAD_DIR exists and is writable
- Check file format is supported

## Development

### Running Tests
```bash
cd backend
pytest
```

### Code Formatting
```bash
# Backend
black app/
flake8 app/

# Frontend
npm run lint
```

## License

This project is for educational and demonstration purposes.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please open an issue on GitHub.

---

**Note**: This is an MVP (Minimum Viable Product) implementation. For production use, additional features like:
- Complete HIPAA compliance
- Advanced security measures
- EMR/EHR integration
- Mobile applications
- Advanced analytics
- Multi-language support

should be implemented as outlined in the system design document.