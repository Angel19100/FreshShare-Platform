# Fresh-Share Network: Hyperlocal Food Waste Exchange Platform

## Case Study
**"The Fresh-Share Network: Designing a System to Connect Local Food Businesses with Charities and Individuals for Immediate Surplus Redistribution."**

## Problem Statement
Food waste is a critical global issue. Small to medium-sized food vendors (bakeries, restaurants, grocery stores) often have surplus food at the end of the day that goes to waste. Meanwhile, charities, food banks, and individuals in need could benefit from this food if there was an efficient way to connect supply with demand in real-time.

## Solution
A hyperlocal, location-based platform that enables:
- Food vendors to post surplus food details in real-time
- Charities and vetted individuals to claim and collect food before it spoils
- Immediate notifications based on geographical proximity
- Waste tracking and impact metrics

## Key Features
1. **Real-time Listing Management**: Vendors can quickly post surplus food items
2. **Location-based Matching**: Automatic proximity-based notifications
3. **User Verification System**: Role-based access (Vendor, Charity, Individual)
4. **Claim & Collection Workflow**: Streamlined process from listing to pickup
5. **Impact Dashboard**: Track food saved, meals provided, environmental impact
6. **Rating & Review System**: Build trust in the community
7. **Notification System**: Real-time alerts for nearby available food

## Technology Stack
- **Backend**: Python (Flask/FastAPI)
- **Database**: PostgreSQL with PostGIS for geospatial queries
- **Authentication**: JWT-based authentication
- **Testing**: pytest
- **Version Control**: Git
- **Containerization**: Docker
- **API Documentation**: OpenAPI/Swagger

## Design Pattern
**Observer Pattern** - Used for the notification system where registered users (observers) are automatically notified when new food listings (subjects) become available in their area.

## Software Design Approach
Using **Object-Oriented Design** with UML diagrams:
- Use Case Diagram
- Class Diagram
- Activity Diagram
- Data Flow Diagram
- Sequence Diagram

## Project Structure
```
FreshShare-Platform/
├── src/
│   ├── models/          # Database models
│   ├── controllers/     # Business logic
│   ├── routes/          # API endpoints
│   ├── services/        # Core services
│   ├── observers/       # Observer pattern implementation
│   └── utils/           # Helper functions
├── tests/               # Test cases
├── docs/                # Documentation and diagrams
├── docker/              # Docker configuration
├── requirements.txt     # Python dependencies
├── .gitignore
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- PostgreSQL 14+
- Git
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd FreshShare-Platform
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Initialize database:
```bash
python src/db/init_db.py
```

6. Run the application:
```bash
python src/app.py
```

You can customize the host and port with environment variables. Examples:

- Run on a different port (Linux/macOS):
```bash
PORT=8000 python src/app.py
```
- Run on a different port (Windows PowerShell):
```powershell
$env:PORT = "8000"; python src/app.py
```
- Explicitly set host and debug mode:
```bash
HOST=127.0.0.1 PORT=8000 FLASK_DEBUG=False python src/app.py
```

### Using Docker

```bash
docker-compose up --build
```

## Testing

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=src --cov-report=html
```

## API Documentation

Once the application is running, access the API documentation at:
- Swagger UI: http://localhost:5000/api/docs
- ReDoc: http://localhost:5000/api/redoc

## Contributors
[Your Name] - Final Exam Project

## License
MIT License - Educational Project
