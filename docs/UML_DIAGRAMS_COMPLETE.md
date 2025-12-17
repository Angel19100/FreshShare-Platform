# UML Diagrams for Fresh-Share Platform

---

## 1. Activity Diagram: Food Listing & Notification Flow

```mermaid
graph TD
    A[Vendor Login] --> B[Create Food Listing]
    B --> C[Enter Details: Title, Quantity, Expiry]
    C --> D[Validate Input]
    D --> E{Valid?}
    E -->|No| F[Show Error]
    F --> C
    E -->|Yes| G[Save to Database]
    G --> H[Trigger Observer Pattern]
    H --> I[Find Nearby Users within 5km]
    I --> J{Users Found?}
    J -->|Yes| K[EmailNotifier Sends Alerts]
    K --> L[Charity/Individual Receives Notification]
    J -->|No| M[Log: No nearby users]
    L --> N[User Reviews Listing]
    N --> O{User Interested?}
    O -->|Yes| P[Claim Food Item]
    O -->|No| Q[End]
    P --> R[Vendor Confirms Pickup]
    R --> S[User Collects Food]
    S --> T[Both Rate Each Other]
    T --> Q
```

---

## 2. Data Flow Diagram: System Information Flow

```mermaid
graph LR
    subgraph User["Users"]
        V["Vendor"]
        C["Charity/Individual"]
    end
    
    subgraph API["REST API"]
        Auth["Auth Service<br/>JWT"]
        List["Listing Service<br/>CRUD"]
        Claim["Claim Service"]
    end
    
    subgraph Observer["Observer Pattern"]
        NotifSvc["Notification Service<br/>Subject"]
        EmailNotif["Email Notifier<br/>Observer"]
    end
    
    subgraph Database["Data Layer"]
        DB["PostgreSQL/SQLite<br/>SQLAlchemy ORM"]
    end
    
    subgraph Geospatial["Geospatial"]
        Geo["PostGIS/GeoAlchemy2<br/>Proximity Queries"]
    end
    
    V -->|Register/Login| Auth
    C -->|Register/Login| Auth
    Auth -->|Validate Token| List
    V -->|POST /listings| List
    List -->|Save FoodListing| DB
    List -->|Trigger notify| NotifSvc
    NotifSvc -->|Find Nearby Users| Geo
    Geo -->|ST_DWithin Query| DB
    NotifSvc -->|Update| EmailNotif
    EmailNotif -->|Send Alert| C
    C -->|GET /listings| List
    C -->|POST /claims| Claim
    Claim -->|Save Claim| DB
```

---

## 3. Sequence Diagram: Create Listing & Notify Flow

```mermaid
sequenceDiagram
    participant V as Vendor
    participant API as Flask API
    participant Auth as Auth Service
    participant ListSvc as ListingService
    participant NotifSvc as NotificationService
    participant EmailNotif as EmailNotifier
    participant DB as Database
    participant Geo as Geospatial Query
    participant C as Charity User

    V->>API: POST /api/listings/(title, quantity, expiry)
    API->>Auth: Validate JWT Token
    Auth-->>API: Token Valid ✓
    
    API->>ListSvc: create_listing(vendor_id, data)
    ListSvc->>DB: Save FoodListing Object
    DB-->>ListSvc: listing_id = 123
    
    ListSvc->>NotifSvc: notify(listing_data, users_data)
    
    NotifSvc->>Geo: find_nearby_users(lat, lon, radius=5km)
    Geo->>DB: ST_DWithin Query - Find users within 5km
    DB-->>Geo: [User1, User2, User3]
    Geo-->>NotifSvc: nearby_users_list
    
    NotifSvc->>EmailNotif: update(listing_data, users)
    EmailNotif->>EmailNotif: format_email_message
    EmailNotif-->>NotifSvc: emails_sent = 3 ✓
    
    NotifSvc-->>ListSvc: notification_count = 3
    ListSvc-->>API: listing_created_successfully
    
    API-->>V: 201 Created {listing_id, status}
    
    C->>C: Receives Email Alert
    C->>API: GET /api/listings/123
    API-->>C: {title, quantity, vendor, location}
    C->>API: POST /api/claims (listing_id=123)
    API-->>C: 201 Claim Created
```

---

## Observer Pattern Class Diagram

```mermaid
classDiagram
    class Subject {
        <<interface>>
        +attach(Observer)*
        +detach(Observer)*
        +notify()*
    }
    
    class NotificationService {
        -observers: List~Observer~
        -pending_notifications: Queue
        +attach(observer: Observer)
        +detach(observer: Observer)
        +notify(listing_data, users_data): int
        +get_observer_count(): int
    }
    
    class Observer {
        <<interface>>
        +update(subject)*
    }
    
    class EmailNotifier {
        -smtp_config: Dict
        +update(listing_data, users_data): bool
        +send_email(user, subject, body): bool
        +format_message(listing): str
    }
    
    class SMSNotifier {
        -twilio_config: Dict
        +update(listing_data, users_data): bool
        +send_sms(user_phone, message): bool
    }
    
    Subject <|.. NotificationService
    Subject --> Observer
    Observer <|.. EmailNotifier
    Observer <|.. SMSNotifier
    NotificationService --> EmailNotifier: uses
    NotificationService --> SMSNotifier: uses (extensible)
```

---

## Database Entity Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ FOOD_LISTING : posts
    USER ||--o{ CLAIM : makes
    USER ||--o{ RATING : gives
    FOOD_LISTING ||--o{ CLAIM : receives
    USER ||--o{ RATING : receives
    
    USER {
        int id PK
        string email UK
        string password_hash
        enum role "vendor|charity|individual|admin"
        string name
        string phone
        float latitude
        float longitude
        text location "POINT(lon lat)"
        boolean verified
        float rating "0-5 stars"
        int rating_count
        datetime created_at
        datetime updated_at
    }
    
    FOOD_LISTING {
        int id PK
        int vendor_id FK
        string title
        text description
        float quantity
        string unit "kg, pieces, servings"
        enum food_type "bakery|produce|dairy|prepared|canned|frozen|other"
        datetime expiry_time
        string pickup_address
        text location "POINT(lon lat)"
        float latitude
        float longitude
        enum status "available|claimed|completed|expired|cancelled"
        datetime created_at
        datetime updated_at
    }
    
    CLAIM {
        int id PK
        int listing_id FK
        int claimer_id FK
        enum status "pending|confirmed|picked_up|cancelled"
        text notes
        datetime claimed_at
        datetime confirmed_at
        datetime picked_up_at
        datetime cancelled_at
    }
    
    RATING {
        int id PK
        int rater_id FK
        int rated_id FK
        int listing_id FK "optional"
        int score "1-5"
        text comment
        datetime created_at
    }
```

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fresh-Share Platform                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              REST API Layer (Flask)                       │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │  │
│  │  │Auth      │ │Listing   │ │Claim     │ │User Routes│  │  │
│  │  │Routes    │ │Routes    │ │Routes    │ │           │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                      │
│  ┌────────────────────────▼──────────────────────────────────┐  │
│  │            Service Layer                                   │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │ListingService                                        │ │  │
│  │  │ - create_listing()  ──►  Trigger Observer Pattern   │ │  │
│  │  │ - update_listing()                                  │ │  │
│  │  │ - search_listings()  ──►  Geospatial Queries        │ │  │
│  │  │ - notify_nearby_users()                             │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  └────────────────────────▲──────────────────────────────────┘  │
│                           │                                      │
│  ┌────────────────────────┼──────────────────────────────────┐  │
│  │      Observer Pattern Implementation                      │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │NotificationService (Subject)                         │ │  │
│  │  │  - observers: [EmailNotifier, ...]                  │ │  │
│  │  │  - notify(listing, users)                           │ │  │
│  │  │      └─► For each user: EmailNotifier.update()      │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                           │                                      │
│  ┌────────────────────────▼──────────────────────────────────┐  │
│  │            Data Layer (ORM)                               │  │
│  │  ┌──────────────────────────────────────────────────────┐ │  │
│  │  │SQLAlchemy Models                                     │ │  │
│  │  │ - User, FoodListing, Claim, Rating                  │ │  │
│  │  │ - GeoAlchemy2 for geospatial queries                │ │  │
│  │  └──────────────────────────────────────────────────────┘ │  │
│  └────────────────────────▲──────────────────────────────────┘  │
│                           │                                      │
│  ┌────────────────────────┼──────────────────────────────────┐  │
│  │        Database (PostgreSQL / SQLite)                     │  │
│  │  - users, food_listings, claims, ratings                │  │
│  │  - PostGIS extension for proximity queries              │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack Overview

```
┌─────────────────────────────────────────────┐
│         Fresh-Share Platform Stack          │
├─────────────────────────────────────────────┤
│                                             │
│  Frontend: (Future) React/Vue.js            │
│  ├─ Components & State Management           │
│  └─ REST API Consumer                       │
│                                             │
│  Backend: Python + Flask 3.0                │
│  ├─ REST API (Blueprint routing)            │
│  ├─ JWT Authentication                      │
│  └─ Observer Pattern (Notifications)        │
│                                             │
│  Database: PostgreSQL 14 + PostGIS          │
│  ├─ Relational Data (SQLAlchemy ORM)        │
│  └─ Geospatial Queries (ST_DWithin)        │
│                                             │
│  Cache: Redis (optional)                    │
│  └─ Notification queuing                    │
│                                             │
│  API Documentation: Swagger/Flasgger        │
│  └─ Auto-generated from Flask route docs    │
│                                             │
│  Testing: pytest (10 test cases)            │
│  ├─ Unit tests (Models, Services)           │
│  ├─ Integration tests (API endpoints)       │
│  └─ Observer pattern tests                  │
│                                             │
│  Deployment: Docker                         │
│  ├─ Multi-stage build (test + prod)         │
│  ├─ docker-compose.yml (app + db + redis)   │
│  └─ Environment-configurable                │
│                                             │
│  Version Control: Git + GitHub              │
│  └─ Clean commit history                    │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 8. CI/CD Workflow Pipeline

```mermaid
graph LR
    A["Developer<br/>Push to GitHub"] --> B["GitHub<br/>Webhook Trigger"]
    B --> C["Checkout<br/>Code"]
    C --> D["Setup Python<br/>Environment"]
    D --> E["Install<br/>Dependencies"]
    E --> F["Run<br/>Unit Tests<br/>pytest"]
    F --> G{Tests<br/>Pass?}
    
    G -->|No| H["Notify Developer<br/>Build Failed"]
    H --> I[" Halt Pipeline"]
    
    G -->|Yes| J["Code Quality<br/>Checks"]
    J --> K["Build Docker<br/>Image"]
    K --> L["Push to<br/>Docker Registry"]
    L --> M["Deploy to<br/>Staging"]
    M --> N["Run<br/>Integration Tests"]
    N --> O{Staging<br/>Tests Pass?}
    
    O -->|No| P["Rollback<br/>Staging"]
    P --> H
    
    O -->|Yes| Q["Manual Approval"]
    Q --> R["Deploy to<br/>Production"]
    R --> S["Run Health<br/>Checks"]
    S --> T{Health<br/>OK?}
    
    T -->|No| U["Auto Rollback<br/>to Previous"]
    U --> H
    
    T -->|Yes| V[" Deployment<br/>Complete"]
    
    style V fill:#90EE90
    style I fill:#FFB6C6
    style U fill:#FFB6C6
```

**CI/CD Pipeline Stages:**

1. **Trigger:** Developer pushes code to GitHub
2. **Build:** Checkout, setup Python, install dependencies
3. **Test:** Run pytest (10 test cases)
4. **Quality:** Code quality checks
5. **Docker:** Build and push Docker image
6. **Staging:** Deploy to staging environment with integration tests
7. **Approval:** Manual gate for production deployment
8. **Production:** Deploy to production with health checks
9. **Rollback:** Automatic rollback if health checks fail

**Tools:**
- **Version Control:** GitHub
- **CI/CD:** GitHub Actions (configurable)
- **Testing:** pytest
- **Container Registry:** Docker Hub or private registry
- **Monitoring:** Health check endpoints
