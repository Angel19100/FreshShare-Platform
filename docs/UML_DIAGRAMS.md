# UML Diagrams for Fresh-Share Network

## 1. Use Case Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Fresh-Share Platform                          │
│                                                                   │
│  ┌──────────┐                                                   │
│  │  Vendor  │────────►  Post Surplus Food                       │
│  │          │────────►  Update Listing                          │
│  │          │────────►  Delete Listing                          │
│  │          │────────►  View Claims                             │
│  │          │────────►  Confirm Pickup                          │
│  │          │────────►  Rate Receiver                           │
│  └──────────┘                                                   │
│                                                                   │
│  ┌──────────┐                                                   │
│  │ Charity/ │────────►  Browse Listings                         │
│  │Individual│────────►  Search by Location                      │
│  │          │────────►  Claim Food                              │
│  │          │────────►  View My Claims                          │
│  │          │────────►  Rate Vendor                             │
│  │          │────────►  Receive Notifications                   │
│  └──────────┘                                                   │
│                                                                   │
│  ┌──────────┐                                                   │
│  │  Admin   │────────►  Verify Users                            │
│  │          │────────►  View Analytics                          │
│  │          │────────►  Moderate Reports                        │
│  │          │────────►  Manage System Settings                  │
│  └──────────┘                                                   │
└─────────────────────────────────────────────────────────────────┘
```

## 2. Class Diagram

```
┌────────────────────────┐
│       User             │
├────────────────────────┤
│ - id: int              │
│ - email: string        │
│ - password_hash: string│
│ - role: enum           │
│ - name: string         │
│ - phone: string        │
│ - latitude: float      │
│ - longitude: float     │
│ - verified: boolean    │
│ - rating: float        │
│ - created_at: datetime │
├────────────────────────┤
│ + register()           │
│ + login()              │
│ + update_profile()     │
│ + get_location()       │
└────────────────────────┘
         △
         │
    ┌────┴────┬──────────┐
    │         │          │
┌───┴───┐ ┌──┴───┐ ┌────┴────┐
│Vendor │ │Charity│ │Individual│
└───────┘ └──────┘ └─────────┘

┌────────────────────────────┐
│      FoodListing           │
├────────────────────────────┤
│ - id: int                  │
│ - vendor_id: int           │
│ - title: string            │
│ - description: string      │
│ - quantity: float          │
│ - unit: string             │
│ - food_type: enum          │
│ - expiry_time: datetime    │
│ - pickup_address: string   │
│ - latitude: float          │
│ - longitude: float         │
│ - status: enum             │
│ - created_at: datetime     │
├────────────────────────────┤
│ + create_listing()         │
│ + update_listing()         │
│ + delete_listing()         │
│ + notify_observers()       │
│ + mark_as_claimed()        │
└────────────────────────────┘
        │
        │ 1
        │
        │ *
┌────────────────────────────┐
│       Claim                │
├────────────────────────────┤
│ - id: int                  │
│ - listing_id: int          │
│ - claimer_id: int          │
│ - claimed_at: datetime     │
│ - pickup_time: datetime    │
│ - status: enum             │
│ - notes: string            │
├────────────────────────────┤
│ + create_claim()           │
│ + confirm_pickup()         │
│ + cancel_claim()           │
└────────────────────────────┘

┌────────────────────────────┐
│   Observer (Interface)     │
├────────────────────────────┤
│ + update(listing)          │
└────────────────────────────┘
         △
         │
    ┌────┴────┐
    │         │
┌───┴───────────┐ ┌────────────────┐
│EmailNotifier  │ │ SMSNotifier    │
├───────────────┤ ├────────────────┤
│+ update()     │ │+ update()      │
└───────────────┘ └────────────────┘

┌────────────────────────────┐
│    NotificationService     │
├────────────────────────────┤
│ - observers: List          │
├────────────────────────────┤
│ + attach(observer)         │
│ + detach(observer)         │
│ + notify(listing)          │
└────────────────────────────┘

┌────────────────────────────┐
│       Rating               │
├────────────────────────────┤
│ - id: int                  │
│ - rater_id: int            │
│ - rated_id: int            │
│ - listing_id: int          │
│ - score: int (1-5)         │
│ - comment: string          │
│ - created_at: datetime     │
├────────────────────────────┤
│ + create_rating()          │
│ + update_average()         │
└────────────────────────────┘
```

## 3. Activity Diagram - Posting and Claiming Food

```
Vendor                                    System                                    Receiver
  │                                         │                                         │
  │──Login──────────────────────────────►  │                                         │
  │                                         │                                         │
  │◄──Authentication Success──────────────  │                                         │
  │                                         │                                         │
  │──Click "Post Surplus Food"──────────►  │                                         │
  │                                         │                                         │
  │──Fill Form (title, quantity, etc)───►  │                                         │
  │                                         │                                         │
  │──Submit────────────────────────────►   │                                         │
  │                                         │                                         │
  │                                    ┌────┴────┐                                   │
  │                                    │Validate │                                   │
  │                                    │  Data   │                                   │
  │                                    └────┬────┘                                   │
  │                                         │                                         │
  │                                    ┌────┴────┐                                   │
  │                                    │  Save   │                                   │
  │                                    │Listing  │                                   │
  │                                    └────┬────┘                                   │
  │                                         │                                         │
  │                                    ┌────┴────┐                                   │
  │                                    │  Find   │                                   │
  │                                    │ Nearby  │                                   │
  │                                    │ Users   │                                   │
  │                                    └────┬────┘                                   │
  │                                         │                                         │
  │                                         │──Notify Nearby Users──────────────────► │
  │                                         │                                         │
  │◄──Confirmation──────────────────────   │                                         │
  │                                         │                                         │
  │                                         │                                         │
  │                                         │      ◄──Browse Listings────────────────│
  │                                         │                                         │
  │                                         │──────Return Nearby Listings───────────►│
  │                                         │                                         │
  │                                         │      ◄──Claim Food─────────────────────│
  │                                         │                                         │
  │                                    ┌────┴────┐                                   │
  │                                    │ Verify  │                                   │
  │                                    │Available│                                   │
  │                                    └────┬────┘                                   │
  │                                         │                                         │
  │                                    ┌────┴────┐                                   │
  │                                    │ Create  │                                   │
  │                                    │  Claim  │                                   │
  │                                    └────┬────┘                                   │
  │                                         │                                         │
  │◄──Notify Vendor────────────────────    │                                         │
  │                                         │──────Confirm Claim─────────────────────►│
  │                                         │                                         │
  │──Confirm Pickup After Collection───►   │                                         │
  │                                         │                                         │
  │                                    ┌────┴────┐                                   │
  │                                    │  Close  │                                   │
  │                                    │ Listing │                                   │
  │                                    └────┬────┘                                   │
  │                                         │                                         │
  │◄──Request Rating───────────────────    │──────Request Rating────────────────────►│
  │                                         │                                         │
```

## 4. Sequence Diagram - Creating a Food Listing with Observer Pattern

```
Vendor      VendorController    FoodListing    NotificationService    Observer(Users)
  │                │                  │                 │                    │
  │──POST /listing─►│                 │                 │                    │
  │                │                  │                 │                    │
  │                │──validate_data──►│                 │                    │
  │                │                  │                 │                    │
  │                │◄─────data_ok─────│                 │                    │
  │                │                  │                 │                    │
  │                │──create()───────►│                 │                    │
  │                │                  │                 │                    │
  │                │                  │──save_to_db()   │                    │
  │                │                  │                 │                    │
  │                │                  │──notify_observers(listing)──────────►│
  │                │                  │                 │                    │
  │                │                  │                 │──get_nearby_users()│
  │                │                  │                 │                    │
  │                │                  │                 │──for each observer─►│
  │                │                  │                 │                    │
  │                │                  │                 │       update()     │
  │                │                  │                 │   (send notification)
  │                │                  │                 │                    │
  │                │◄─listing_created─│◄────done────────│                    │
  │                │                  │                 │                    │
  │◄───201 Created─│                  │                 │                    │
  │    (JSON)      │                  │                 │                    │
```

## 5. Data Flow Diagram (Level 0 & Level 1)

### Level 0 - Context Diagram
```
                         ┌─────────────────────────────┐
                         │                             │
    Vendors ────────────►│                             │────────────► Notification
                         │   Fresh-Share Platform      │
    Receivers ──────────►│                             │────────────► Reports
                         │                             │
    Admins ─────────────►│                             │────────────► Analytics
                         │                             │
                         └─────────────────────────────┘
```

### Level 1 - Main Processes
```
┌─────────┐          ┌──────────────────┐          ┌──────────────┐
│ Vendors │          │ 1.0 User         │          │              │
│         │─────────►│ Management       │─────────►│ User Database│
└─────────┘          │                  │          │              │
                     └──────────────────┘          └──────────────┘
                              │
                              ▼
                     ┌──────────────────┐          ┌──────────────┐
                     │ 2.0 Listing      │          │   Listing    │
                     │ Management       │◄────────►│   Database   │
                     │                  │          │              │
                     └──────────────────┘          └──────────────┘
                              │
                              ▼
┌─────────┐          ┌──────────────────┐          ┌──────────────┐
│Receivers│          │ 3.0 Search &     │          │  Geospatial  │
│         │─────────►│ Matching         │─────────►│    Index     │
└─────────┘          │                  │          │              │
                     └──────────────────┘          └──────────────┘
                              │
                              ▼
                     ┌──────────────────┐          ┌──────────────┐
                     │ 4.0 Notification │          │  Claim       │
                     │ System (Observer)│◄────────►│  Database    │
                     │                  │          │              │
                     └──────────────────┘          └──────────────┘
                              │
                              ▼
                     ┌──────────────────┐          ┌──────────────┐
┌────────┐          │ 5.0 Analytics &  │          │  Analytics   │
│ Admins │─────────►│ Reporting        │─────────►│  Database    │
└────────┘          │                  │          │              │
                    └──────────────────┘          └──────────────┘
```

## Design Patterns Used

### Observer Pattern
**Purpose**: Automatically notify nearby users when new food listings are posted.

**Implementation**:
- **Subject**: `FoodListing` - When a new listing is created
- **Observers**: `EmailNotifier`, `SMSNotifier`, `PushNotifier`
- **ConcreteSubject**: `NotificationService` - Manages observer registration and notification

**Benefits**:
- Decouples listing creation from notification logic
- Easy to add new notification channels
- Users are automatically notified based on their preferences and location

### Additional Patterns (Bonus)
- **Repository Pattern**: Data access abstraction
- **Factory Pattern**: Creating different user types (Vendor, Charity, Individual)
- **Strategy Pattern**: Different search/matching algorithms
