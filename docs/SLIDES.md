# Fresh-Share Platform: Hyperlocal Food Waste Exchange
## Final Exam Presentation

---

## Slide 1: Project Overview

**Fresh-Share Platform**

A hyperlocal, location-based platform connecting food vendors with surplus food to charities and individuals in need.

### Key Metrics:
- **Language:** Python 3.9+ with Flask 3.0
- **Tests:** 10 comprehensive test cases ✅
- **Design Pattern:** Observer Pattern
- **Architecture:** REST API with JWT authentication
- **Database:** SQLAlchemy with PostGIS for geospatial queries
- **Containerization:** Docker multi-stage build

### Real-Life Problem:
Food waste is a critical global issue. Over 1.3 billion tons of food is wasted annually while millions go hungry. Small to medium-sized food vendors often have surplus at the end of the day with no efficient way to redistribute it.

---

## Slide 2: Problem Statement & Solution

### The Problem:
1. **Surplus waste:** Vendors discard perfectly good food at day's end
2. **Unmet needs:** Charities and individuals lack access to available food
3. **No coordination:** No real-time, location-aware system to connect supply with demand
4. **Lost opportunity:** Environmental and social impact

### The Solution:
**Fresh-Share Platform** enables:
- ✅ Real-time food listing creation by vendors
- ✅ Location-based matching and notifications
- ✅ Verified user roles (Vendor, Charity, Individual)
- ✅ Streamlined claim and pickup workflow
- ✅ Impact tracking and community ratings

---

## Slide 3: Architecture & Design Pattern

### Observer Pattern Implementation:
The platform uses the **Observer Design Pattern** for notifications:

**Subject:** `FoodListing` (newly created food items)  
**Observers:** `NotificationService` → `EmailNotifier` (sends alerts to nearby users)

### How It Works:
1. Vendor creates a food listing
2. `ListingService.create_listing()` triggers observer notifications
3. `NotificationService.notify()` finds nearby users within 5km
4. `EmailNotifier.update()` sends alerts to each observer
5. Charities/individuals receive notification and can claim food

### Benefits:
- **Loose coupling:** Notification system independent of listing service
- **Scalability:** Easy to add SMS, Push, Slack notifiers
- **Maintainability:** Changes to notifications don't affect core listing logic
- **Testability:** Each component tested in isolation
FoodListing created
    ↓
ListingService._notify_nearby_users()
    ↓
NotificationService.notify(listing, nearby_users)
    ↓
EmailNotifier.update() [sends email alerts]
```

### Core Components:
- **Models:** User, FoodListing, Claim, Rating
- **Routes:** auth_routes, listing_routes, claim_routes, user_routes
- **Services:** ListingService (business logic)
- **Observers:** NotificationService, EmailNotifier

### Technology Stack:
| Component | Technology |
|-----------|-----------|
| Backend | Flask 3.0 |
| Database | SQLAlchemy + PostGIS |
| Authentication | JWT (Flask-JWT-Extended) |
| API Docs | Flasgger (Swagger UI) |
| Testing | pytest |
| Containerization | Docker |

---

## Slide 4: Implementation Highlights

### REST API Endpoints:
- **Auth:** POST `/api/auth/register`, `/api/auth/login`
- **Listings:** GET/POST/PUT/DELETE `/api/listings/`
- **Claims:** POST `/api/claims/`, GET `/api/claims/<id>`
- **Users:** GET `/api/users/<id>`, PUT `/api/users/<id>`
- **Health:** GET `/health`
- **Docs:** GET `/api/docs`

### Code Quality:
✅ Timezone-aware datetime handling (removed UTC deprecation warnings)  
✅ Environment-configurable app (HOST, PORT, FLASK_CONFIG via env vars)  
✅ Clean dependencies (7 core packages in requirements.txt)  
✅ Comprehensive test coverage (10 tests, 100% pass rate)  
✅ Multi-stage Docker build (test stage validates before production)

### Geospatial Features:
- Users and listings stored with lat/lon coordinates
- GeoAlchemy2 for PostGIS spatial queries
- Find nearby users within configurable radius (default 5km)
- Search available listings by location

---

## Slide 5: Testing, Deployment & Results

### Test Coverage:
```
10 tests passing ✅
- 3 Authentication tests (register, login, errors)
- 2 Observer pattern tests (attach, detach, notify)
- 5 Model tests (password hashing, to_dict methods)
```

### Deployment:
**Docker:**
- Multi-stage Dockerfile (test stage + production stage)
- docker-compose.yml with PostgreSQL + Redis + Flask app
- Health checks and non-root user for security

**Git & Version Control:**
- Repository: https://github.com/Angel19100/FreshShare-Platform
- 29 files committed
- Master branch → main branch

**Running the App:**
```bash
# Development (testing mode, in-memory DB)
python -u -c "from src.app import create_app; app=create_app('testing'); app.run(host='127.0.0.1', port=5000)"

# Or via Docker
docker build -t freshshare:latest .
docker-compose up
```

### Results:
✅ **All 8 assignment requirements met:**
1. ✅ Real-life problem (food waste redistribution)
2. ✅ Software design (Observer pattern + OOP)
3. ✅ Programming language (Python)
4. ✅ Clean code (Google standards, timezone-aware, env-configurable)
5. ✅ Version control (Git/GitHub)
6. ✅ Design pattern (Observer)
7. ✅ Testing (10 tests, 100% pass)
8. ✅ Dockerization (multi-stage build + compose)

---
