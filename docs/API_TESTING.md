# API Testing Guide

This file contains sample API requests you can use to test the Fresh-Share Platform.

## Using PowerShell (Windows)

### 1. Health Check

```powershell
Invoke-RestMethod -Uri "http://localhost:5000/health" -Method GET
```

### 2. Register a Vendor

```powershell
$body = @{
    email = "bakery@example.com"
    password = "secure123"
    name = "Fresh Bakery"
    role = "vendor"
    phone = "+1234567890"
    address = "123 Main St, New York"
    latitude = 40.7128
    longitude = -74.0060
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/register" -Method POST -Body $body -ContentType "application/json"
```

### 3. Register a Charity

```powershell
$body = @{
    email = "charity@example.com"
    password = "secure123"
    name = "City Food Bank"
    role = "charity"
    phone = "+1234567891"
    address = "456 Oak Ave, New York"
    latitude = 40.7138
    longitude = -74.0070
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/auth/register" -Method POST -Body $body -ContentType "application/json"
```

### 4. Login as Vendor

```powershell
$body = @{
    email = "bakery@example.com"
    password = "secure123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $body -ContentType "application/json"
$token = $response.access_token
Write-Host "Token: $token"
```

### 5. Create a Food Listing

```powershell
# First, get the token from step 4
$headers = @{
    "Authorization" = "Bearer $token"
}

$expiryTime = (Get-Date).AddHours(6).ToString("yyyy-MM-ddTHH:mm:ss")

$body = @{
    title = "Fresh Whole Wheat Bread"
    description = "Baked this morning, still warm!"
    quantity = 20
    unit = "loaves"
    food_type = "bakery"
    expiry_time = $expiryTime
    pickup_address = "123 Main St, New York"
    latitude = 40.7128
    longitude = -74.0060
    special_instructions = "Ring doorbell at back entrance"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/listings/" -Method POST -Headers $headers -Body $body -ContentType "application/json"
```

### 6. Search for Nearby Listings

```powershell
# Login as charity first to get their token
$body = @{
    email = "charity@example.com"
    password = "secure123"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method POST -Body $body -ContentType "application/json"
$charityToken = $response.access_token

# Search for listings
$headers = @{
    "Authorization" = "Bearer $charityToken"
}

$params = @{
    latitude = 40.7138
    longitude = -74.0070
    radius_km = 5
}

Invoke-RestMethod -Uri "http://localhost:5000/api/listings/search" -Method GET -Headers $headers -Body $params
```

### 7. Get My Listings (Vendor)

```powershell
$headers = @{
    "Authorization" = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:5000/api/listings/my-listings" -Method GET -Headers $headers
```

## Using cURL (Alternative)

### 1. Register Vendor
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bakery@example.com",
    "password": "secure123",
    "name": "Fresh Bakery",
    "role": "vendor",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bakery@example.com",
    "password": "secure123"
  }'
```

### 3. Create Listing (replace YOUR_TOKEN)
```bash
curl -X POST http://localhost:5000/api/listings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "title": "Fresh Bread",
    "quantity": 10,
    "unit": "loaves",
    "food_type": "bakery",
    "expiry_time": "2025-12-18T20:00:00",
    "pickup_address": "123 Main St",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

### 4. Search Listings
```bash
curl -X GET "http://localhost:5000/api/listings/search?latitude=40.7128&longitude=-74.0060&radius_km=5" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Using Swagger UI (Recommended for Demo)

1. Start the application
2. Navigate to: http://localhost:5000/api/docs
3. Interactive API documentation with "Try it out" buttons
4. Test all endpoints directly from the browser

## Complete Test Flow

Here's a complete PowerShell script to test the entire flow:

```powershell
# Complete Test Script
$baseUrl = "http://localhost:5000"

Write-Host "=== Testing Fresh-Share Platform ===" -ForegroundColor Green

# 1. Health Check
Write-Host "`n1. Health Check..." -ForegroundColor Yellow
$health = Invoke-RestMethod -Uri "$baseUrl/health"
Write-Host "Status: $($health.status)" -ForegroundColor Green

# 2. Register Vendor
Write-Host "`n2. Registering Vendor..." -ForegroundColor Yellow
$vendorBody = @{
    email = "test.bakery@example.com"
    password = "secure123"
    name = "Test Bakery"
    role = "vendor"
    latitude = 40.7128
    longitude = -74.0060
} | ConvertTo-Json

try {
    $vendor = Invoke-RestMethod -Uri "$baseUrl/api/auth/register" -Method POST -Body $vendorBody -ContentType "application/json"
    Write-Host "Vendor registered: $($vendor.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Vendor might already exist (OK)" -ForegroundColor Yellow
}

# 3. Login Vendor
Write-Host "`n3. Logging in as Vendor..." -ForegroundColor Yellow
$loginBody = @{
    email = "test.bakery@example.com"
    password = "secure123"
} | ConvertTo-Json

$loginResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
$token = $loginResponse.access_token
Write-Host "Logged in successfully" -ForegroundColor Green

# 4. Create Listing
Write-Host "`n4. Creating Food Listing..." -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $token"
}

$expiryTime = (Get-Date).AddHours(6).ToString("yyyy-MM-ddTHH:mm:ss")
$listingBody = @{
    title = "Fresh Sourdough Bread"
    description = "Artisan sourdough, baked today"
    quantity = 15
    unit = "loaves"
    food_type = "bakery"
    expiry_time = $expiryTime
    pickup_address = "123 Main St, New York"
    latitude = 40.7128
    longitude = -74.0060
} | ConvertTo-Json

$listing = Invoke-RestMethod -Uri "$baseUrl/api/listings/" -Method POST -Headers $headers -Body $listingBody -ContentType "application/json"
Write-Host "Listing created: $($listing.listing.title)" -ForegroundColor Green

# 5. Register Charity
Write-Host "`n5. Registering Charity..." -ForegroundColor Yellow
$charityBody = @{
    email = "test.charity@example.com"
    password = "secure123"
    name = "Test Food Bank"
    role = "charity"
    latitude = 40.7138
    longitude = -74.0070
    verified = $true
} | ConvertTo-Json

try {
    $charity = Invoke-RestMethod -Uri "$baseUrl/api/auth/register" -Method POST -Body $charityBody -ContentType "application/json"
    Write-Host "Charity registered: $($charity.user.name)" -ForegroundColor Green
} catch {
    Write-Host "Charity might already exist (OK)" -ForegroundColor Yellow
}

# 6. Login Charity
Write-Host "`n6. Logging in as Charity..." -ForegroundColor Yellow
$charityLoginBody = @{
    email = "test.charity@example.com"
    password = "secure123"
} | ConvertTo-Json

$charityLoginResponse = Invoke-RestMethod -Uri "$baseUrl/api/auth/login" -Method POST -Body $charityLoginBody -ContentType "application/json"
$charityToken = $charityLoginResponse.access_token
Write-Host "Logged in successfully" -ForegroundColor Green

# 7. Search Listings
Write-Host "`n7. Searching for Nearby Listings..." -ForegroundColor Yellow
$charityHeaders = @{
    "Authorization" = "Bearer $charityToken"
}

$searchParams = "latitude=40.7138&longitude=-74.0070&radius_km=5"
$searchResults = Invoke-RestMethod -Uri "$baseUrl/api/listings/search?$searchParams" -Method GET -Headers $charityHeaders
Write-Host "Found $($searchResults.count) listings nearby" -ForegroundColor Green

if ($searchResults.count -gt 0) {
    Write-Host "`nNearby Listings:" -ForegroundColor Cyan
    foreach ($item in $searchResults.listings) {
        Write-Host "  - $($item.title) ($($item.quantity) $($item.unit))" -ForegroundColor White
    }
}

# 8. Get Vendor's Listings
Write-Host "`n8. Getting Vendor's Listings..." -ForegroundColor Yellow
$myListings = Invoke-RestMethod -Uri "$baseUrl/api/listings/my-listings" -Method GET -Headers $headers
Write-Host "Vendor has $($myListings.count) listings" -ForegroundColor Green

Write-Host "`n=== All Tests Completed Successfully! ===" -ForegroundColor Green
```

Save this script as `test-api.ps1` and run it with:
```powershell
.\test-api.ps1
```

## Expected Responses

### Successful Registration
```json
{
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "bakery@example.com",
    "role": "vendor",
    "name": "Fresh Bakery",
    "verified": false,
    "rating": 0.0
  }
}
```

### Successful Login
```json
{
  "message": "Login successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "email": "bakery@example.com",
    "role": "vendor"
  }
}
```

### Successful Listing Creation
```json
{
  "message": "Listing created successfully",
  "listing": {
    "id": 1,
    "title": "Fresh Whole Wheat Bread",
    "quantity": 20,
    "unit": "loaves",
    "food_type": "bakery",
    "status": "available"
  }
}
```

## Troubleshooting

**401 Unauthorized:**
- Token expired or invalid
- Re-login to get new token

**400 Bad Request:**
- Check JSON format
- Ensure all required fields are present

**500 Internal Server Error:**
- Check server logs
- Ensure database is running
- Verify environment variables

## Notes for Demonstration

1. **Show Observer Pattern:** After creating a listing, check the server logs to see notification messages
2. **Test Geospatial:** Create listings at different locations and search with various radii
3. **Demo Authentication:** Show both successful and failed login attempts
4. **API Documentation:** Use Swagger UI for interactive testing during presentation
