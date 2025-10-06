# PhoneCheckerBot API Documentation

## Overview

The PhoneCheckerBot REST API provides enterprise-grade endpoints for phone number verification, spam detection, OTP services, and analytics. This API is designed for high-performance, secure integration with external systems.

**Base URL:** `http://localhost:8000` (Development) | `https://your-domain.com` (Production)

**API Version:** 2.0.0

**Authentication:** Bearer Token (API Key required for all endpoints)

## Authentication

All API endpoints require authentication using a Bearer token in the Authorization header:

```bash
Authorization: Bearer your-api-key-here
```

## Rate Limiting

- **IP-based:** 100 requests per hour per IP address
- **Global:** 10,000 requests per hour across all endpoints
- **Headers:** Rate limit status included in response headers

## API Endpoints

### 1. Health Check

**GET** `/api/health`

Check API service health and status.

**No authentication required**

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "uptime_seconds": 86400.5,
  "version": "2.0.0",
  "services": {
    "api": "healthy",
    "database": "healthy",
    "monitoring": "healthy"
  }
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/health"
```

---

### 2. Phone Number Lookup

**POST** `/api/phone/lookup`

Comprehensive phone number analysis including spam detection, carrier information, and validation.

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "country_code": "US",
  "check_spam": true
}
```

**Response:**
```json
{
  "phone_number": "+1234567890",
  "is_valid": true,
  "country": "United States",
  "carrier": "Verizon",
  "is_spam": false,
  "spam_confidence": 0.1,
  "analysis": {
    "line_type": "mobile",
    "location": "New York, NY",
    "risk_score": 2.5,
    "last_checked": "2024-01-15T10:30:00Z"
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/phone/lookup" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "check_spam": true
  }'
```

---

### 3. Send OTP

**POST** `/api/otp/send`

Send one-time password to specified phone number via SMS.

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "message_template": "Your verification code is: {otp}"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "otp_sent": true,
    "expires_in": 300
  },
  "message": "OTP sent successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/otp/send" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890"
  }'
```

---

### 4. Verify OTP

**POST** `/api/otp/verify`

Verify one-time password for phone number authentication.

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "otp_code": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "verified": true
  },
  "message": "OTP verified successfully",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/otp/verify" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "otp_code": "123456"
  }'
```

---

### 5. Add to Blacklist

**POST** `/api/blacklist/add`

Add phone number to spam/fraud blacklist.

**Request Body:**
```json
{
  "phone_number": "+1234567890",
  "reason": "Confirmed spam caller",
  "added_by": "admin_user"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "blacklisted": true
  },
  "message": "Phone number added to blacklist",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/blacklist/add" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "reason": "Confirmed spam caller",
    "added_by": "security_team"
  }'
```

---

### 6. Check Blacklist

**GET** `/api/blacklist/check/{phone_number}`

Check if phone number is in the blacklist.

**Path Parameters:**
- `phone_number`: Phone number to check (URL encoded)

**Response:**
```json
{
  "success": true,
  "data": {
    "is_blacklisted": false
  },
  "message": "Blacklist check completed",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/blacklist/check/%2B1234567890" \
  -H "Authorization: Bearer your-api-key"
```

---

### 7. Analytics Summary

**GET** `/api/stats/summary`

Get comprehensive analytics summary for specified time period.

**Query Parameters:**
- `hours`: Time period in hours (default: 24, max: 720)

**Response:**
```json
{
  "success": true,
  "data": {
    "period_hours": 24,
    "user_activity": {
      "phone_lookup": 150,
      "otp_verification": 89,
      "spam_reports": 12
    },
    "performance": {
      "avg_lookup_time": 245.5,
      "avg_otp_time": 189.2
    },
    "system_health": {
      "avg_cpu_usage": 23.4,
      "avg_memory_usage": 67.8,
      "peak_concurrent_users": 45
    }
  },
  "message": "Analytics summary for last 24 hours",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/stats/summary?hours=48" \
  -H "Authorization: Bearer your-api-key"
```

---

### 8. Performance Statistics

**GET** `/api/stats/performance`

Get detailed performance metrics and trends.

**Response:**
```json
{
  "success": true,
  "data": {
    "averages": [
      {
        "operation": "phone_lookup",
        "avg_duration_ms": 245.67,
        "count": 1250
      },
      {
        "operation": "otp_send",
        "avg_duration_ms": 189.23,
        "count": 890
      }
    ],
    "recent_measurements": 100,
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "message": "Performance statistics retrieved",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Example:**
```bash
curl -X GET "http://localhost:8000/api/stats/performance" \
  -H "Authorization: Bearer your-api-key"
```

---

## Error Handling

All API endpoints return consistent error responses:

### HTTP Status Codes

- `200` - Success
- `400` - Bad Request (invalid parameters)
- `401` - Unauthorized (missing or invalid API key)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (endpoint does not exist)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

### Error Response Format

```json
{
  "success": false,
  "message": "Error description",
  "timestamp": "2024-01-15T10:30:00Z",
  "error_code": "RATE_LIMIT_EXCEEDED"
}
```

### Common Error Examples

**Rate Limit Exceeded (429):**
```json
{
  "success": false,
  "message": "Rate limit exceeded",
  "retry_after": 3600
}
```

**Invalid API Key (401):**
```json
{
  "success": false,
  "message": "Invalid API key",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Invalid Phone Number (400):**
```json
{
  "success": false,
  "message": "Invalid phone number format",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

---

## Integration Examples

### Python Integration

```python
import requests
import json

class PhoneCheckerAPI:
    def __init__(self, api_key, base_url="http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def lookup_phone(self, phone_number, check_spam=True):
        url = f"{self.base_url}/api/phone/lookup"
        data = {
            "phone_number": phone_number,
            "check_spam": check_spam
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def send_otp(self, phone_number):
        url = f"{self.base_url}/api/otp/send"
        data = {"phone_number": phone_number}
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()
    
    def verify_otp(self, phone_number, otp_code):
        url = f"{self.base_url}/api/otp/verify"
        data = {
            "phone_number": phone_number,
            "otp_code": otp_code
        }
        response = requests.post(url, headers=self.headers, json=data)
        return response.json()

# Usage
api = PhoneCheckerAPI("your-api-key")
result = api.lookup_phone("+1234567890")
print(result)
```

### JavaScript Integration

```javascript
class PhoneCheckerAPI {
    constructor(apiKey, baseUrl = 'http://localhost:8000') {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async lookupPhone(phoneNumber, checkSpam = true) {
        const response = await fetch(`${this.baseUrl}/api/phone/lookup`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                phone_number: phoneNumber,
                check_spam: checkSpam
            })
        });
        return await response.json();
    }
    
    async sendOTP(phoneNumber) {
        const response = await fetch(`${this.baseUrl}/api/otp/send`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                phone_number: phoneNumber
            })
        });
        return await response.json();
    }
    
    async verifyOTP(phoneNumber, otpCode) {
        const response = await fetch(`${this.baseUrl}/api/otp/verify`, {
            method: 'POST',
            headers: this.headers,
            body: JSON.stringify({
                phone_number: phoneNumber,
                otp_code: otpCode
            })
        });
        return await response.json();
    }
}

// Usage
const api = new PhoneCheckerAPI('your-api-key');
api.lookupPhone('+1234567890').then(result => {
    console.log(result);
});
```

### cURL Examples

**Complete Phone Verification Flow:**

```bash
#!/bin/bash

API_KEY="your-api-key"
BASE_URL="http://localhost:8000"
PHONE="+1234567890"

# 1. Lookup phone number
echo "Looking up phone number..."
curl -X POST "$BASE_URL/api/phone/lookup" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\": \"$PHONE\", \"check_spam\": true}"

echo -e "\n\n"

# 2. Send OTP
echo "Sending OTP..."
curl -X POST "$BASE_URL/api/otp/send" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\": \"$PHONE\"}"

echo -e "\n\n"

# 3. Verify OTP (you would get the actual OTP from SMS)
echo "Verifying OTP..."
curl -X POST "$BASE_URL/api/otp/verify" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\": \"$PHONE\", \"otp_code\": \"123456\"}"
```

---

## Production Configuration

### Environment Variables

Required environment variables for production deployment:

```bash
# API Configuration
API_SECRET_KEY=your-production-api-key
API_PORT=8000

# Database
ORACLE_USER=your_oracle_username
ORACLE_PASSWORD=your_oracle_password
ORACLE_DSN=your_oracle_connection_string

# Twilio (for OTP)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number

# OpenAI (for spam detection)
OPENAI_API_KEY=your_openai_key

# Security
JWT_SECRET_KEY=your_jwt_secret
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=3600

# Monitoring
LOG_LEVEL=INFO
METRICS_ENABLED=true
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "api_server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Health Monitoring

The API includes built-in health monitoring accessible at:

- **Health Check:** `GET /api/health`
- **Metrics:** `GET /api/stats/performance`
- **Dashboard:** Access the web dashboard at `http://localhost:5000/admin/dashboard`

---

## Support

For technical support or API questions:

- **Documentation:** This file and inline API docs at `/api/docs`
- **Issues:** GitHub repository issues
- **Status Page:** Monitor API status and uptime

---

**API Version:** 2.0.0  
**Last Updated:** January 2024  
**Compatibility:** Python 3.8+, REST API Standards