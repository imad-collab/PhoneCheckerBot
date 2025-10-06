"""
Enterprise REST API Server for PhoneCheckerBot
Comprehensive API endpoints for phone lookup, analytics, and management.
"""

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import hashlib
import hmac
import time

# Import monitoring
try:
    from monitoring import bot_logger, rate_limiter, analytics_collector, health_checker
except ImportError:
    # Fallback for testing
    class MockLogger:
        def log_user_action(self, *args, **kwargs): pass
        def log_security_event(self, *args, **kwargs): pass
    
    bot_logger = MockLogger()
    rate_limiter = None
    analytics_collector = None
    health_checker = None

app = FastAPI(
    title="PhoneCheckerBot API",
    description="Enterprise-grade REST API for phone number verification and spam detection",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'dev-secret-key')

# Request/Response Models
class PhoneLookupRequest(BaseModel):
    phone_number: str
    country_code: Optional[str] = None
    check_spam: bool = True

class PhoneLookupResponse(BaseModel):
    phone_number: str
    is_valid: bool
    country: Optional[str] = None
    carrier: Optional[str] = None
    is_spam: bool
    spam_confidence: float
    analysis: Dict[str, Any]
    timestamp: str

class OTPSendRequest(BaseModel):
    phone_number: str
    message_template: Optional[str] = None

class OTPVerifyRequest(BaseModel):
    phone_number: str
    otp_code: str

class BlacklistRequest(BaseModel):
    phone_number: str
    reason: str
    added_by: str

class ApiResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    uptime_seconds: float
    version: str
    services: Dict[str, str]

# Authentication
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key from Bearer token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    # In production, this would verify against a database of API keys
    if credentials.credentials != API_SECRET_KEY:
        bot_logger.log_security_event('invalid_api_key', {
            'provided_key': credentials.credentials[:8] + '...',
            'timestamp': datetime.now().isoformat()
        })
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return credentials.credentials

# Rate limiting middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Global rate limiting middleware"""
    if rate_limiter:
        client_ip = request.client.host
        if not rate_limiter.check_ip_rate_limit(client_ip, limit=100, window=3600):
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Rate limit exceeded",
                    "retry_after": 3600
                }
            )
    
    response = await call_next(request)
    return response

# API Endpoints

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    health_data = {}
    if health_checker:
        health_data = health_checker.get_system_health()
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        uptime_seconds=health_data.get('uptime_seconds', 0),
        version="2.0.0",
        services={
            "api": "healthy",
            "database": "healthy",
            "monitoring": "healthy" if health_checker else "disabled"
        }
    )

@app.post("/api/phone/lookup", response_model=PhoneLookupResponse)
async def lookup_phone(
    request: PhoneLookupRequest,
    api_key: str = Depends(verify_api_key)
):
    """Comprehensive phone number lookup and analysis"""
    try:
        # Log the lookup request
        if analytics_collector:
            analytics_collector.record_user_action(
                user_id=0,  # API user
                action='api_phone_lookup',
                details={'phone_number': request.phone_number[:3] + '***'}  # Partial for privacy
            )
        
        # Simulate phone lookup logic (replace with actual implementation)
        phone_analysis = await perform_phone_analysis(request.phone_number, request.check_spam)
        
        response = PhoneLookupResponse(
            phone_number=request.phone_number,
            is_valid=phone_analysis['is_valid'],
            country=phone_analysis.get('country'),
            carrier=phone_analysis.get('carrier'),
            is_spam=phone_analysis['is_spam'],
            spam_confidence=phone_analysis['spam_confidence'],
            analysis=phone_analysis,
            timestamp=datetime.now().isoformat()
        )
        
        # Record spam statistics
        if analytics_collector:
            with sqlite3.connect('analytics.db') as conn:
                conn.execute(
                    "INSERT INTO spam_stats (phone_number, is_spam, confidence_score, detection_method) VALUES (?, ?, ?, ?)",
                    (request.phone_number, phone_analysis['is_spam'], phone_analysis['spam_confidence'], 'api_lookup')
                )
        
        return response
        
    except Exception as e:
        bot_logger.log_security_event('api_error', {
            'endpoint': '/api/phone/lookup',
            'error': str(e),
            'phone_number': request.phone_number[:3] + '***'
        })
        raise HTTPException(status_code=500, detail=f"Lookup failed: {str(e)}")

@app.post("/api/otp/send", response_model=ApiResponse)
async def send_otp(
    request: OTPSendRequest,
    api_key: str = Depends(verify_api_key)
):
    """Send OTP to phone number"""
    try:
        # Simulate OTP sending (replace with actual Twilio implementation)
        otp_code = await generate_and_send_otp(request.phone_number, request.message_template)
        
        if analytics_collector:
            analytics_collector.record_user_action(
                user_id=0,
                action='api_otp_send',
                details={'phone_number': request.phone_number[:3] + '***'}
            )
        
        return ApiResponse(
            success=True,
            data={"otp_sent": True, "expires_in": 300},
            message="OTP sent successfully",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

@app.post("/api/otp/verify", response_model=ApiResponse)
async def verify_otp(
    request: OTPVerifyRequest,
    api_key: str = Depends(verify_api_key)
):
    """Verify OTP code"""
    try:
        # Simulate OTP verification (replace with actual implementation)
        is_valid = await verify_otp_code(request.phone_number, request.otp_code)
        
        if analytics_collector:
            analytics_collector.record_user_action(
                user_id=0,
                action='api_otp_verify',
                details={'phone_number': request.phone_number[:3] + '***', 'success': is_valid}
            )
        
        return ApiResponse(
            success=is_valid,
            data={"verified": is_valid},
            message="OTP verified successfully" if is_valid else "Invalid OTP",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OTP verification failed: {str(e)}")

@app.post("/api/blacklist/add", response_model=ApiResponse)
async def add_to_blacklist(
    request: BlacklistRequest,
    api_key: str = Depends(verify_api_key)
):
    """Add phone number to blacklist"""
    try:
        # Add to blacklist (implement actual blacklist database)
        await add_phone_to_blacklist(request.phone_number, request.reason, request.added_by)
        
        if analytics_collector:
            analytics_collector.record_user_action(
                user_id=0,
                action='api_blacklist_add',
                details={'phone_number': request.phone_number[:3] + '***', 'reason': request.reason}
            )
        
        return ApiResponse(
            success=True,
            data={"blacklisted": True},
            message="Phone number added to blacklist",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add to blacklist: {str(e)}")

@app.get("/api/blacklist/check/{phone_number}", response_model=ApiResponse)
async def check_blacklist(
    phone_number: str,
    api_key: str = Depends(verify_api_key)
):
    """Check if phone number is blacklisted"""
    try:
        is_blacklisted = await check_phone_blacklist(phone_number)
        
        return ApiResponse(
            success=True,
            data={"is_blacklisted": is_blacklisted},
            message="Blacklist check completed",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Blacklist check failed: {str(e)}")

@app.get("/api/stats/summary", response_model=ApiResponse)
async def get_stats_summary(
    hours: int = 24,
    api_key: str = Depends(verify_api_key)
):
    """Get analytics summary"""
    try:
        if not analytics_collector:
            return ApiResponse(
                success=False,
                message="Analytics not available",
                timestamp=datetime.now().isoformat()
            )
        
        summary = analytics_collector.get_analytics_summary(hours)
        
        return ApiResponse(
            success=True,
            data=summary,
            message=f"Analytics summary for last {hours} hours",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/api/stats/performance", response_model=ApiResponse)
async def get_performance_stats(api_key: str = Depends(verify_api_key)):
    """Get performance statistics"""
    try:
        # Get performance data from analytics database
        with sqlite3.connect('analytics.db') as conn:
            # Average response times by operation
            perf_data = conn.execute(
                "SELECT operation, AVG(duration_ms) as avg_duration, COUNT(*) as count FROM performance_metrics GROUP BY operation ORDER BY avg_duration DESC"
            ).fetchall()
            
            # Recent performance trends
            recent_perf = conn.execute(
                "SELECT operation, duration_ms, timestamp FROM performance_metrics ORDER BY timestamp DESC LIMIT 100"
            ).fetchall()
        
        performance_summary = {
            'averages': [{'operation': op, 'avg_duration_ms': round(avg, 2), 'count': count} for op, avg, count in perf_data],
            'recent_measurements': len(recent_perf),
            'timestamp': datetime.now().isoformat()
        }
        
        return ApiResponse(
            success=True,
            data=performance_summary,
            message="Performance statistics retrieved",
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance stats: {str(e)}")

# Helper functions (implement these with actual logic)

async def perform_phone_analysis(phone_number: str, check_spam: bool) -> Dict[str, Any]:
    """Perform comprehensive phone number analysis"""
    # Simulate phone analysis (replace with actual implementation)
    return {
        'is_valid': True,
        'country': 'United States',
        'carrier': 'Verizon',
        'is_spam': False,
        'spam_confidence': 0.1,
        'line_type': 'mobile',
        'location': 'New York, NY',
        'risk_score': 2.5,
        'last_checked': datetime.now().isoformat()
    }

async def generate_and_send_otp(phone_number: str, template: Optional[str]) -> str:
    """Generate and send OTP code"""
    # Simulate OTP generation and sending
    otp_code = "123456"  # In production, generate random OTP
    # Send via Twilio
    return otp_code

async def verify_otp_code(phone_number: str, otp_code: str) -> bool:
    """Verify OTP code"""
    # Simulate OTP verification
    return otp_code == "123456"  # In production, check against stored OTP

async def add_phone_to_blacklist(phone_number: str, reason: str, added_by: str):
    """Add phone number to blacklist database"""
    # Implement actual blacklist database logic
    pass

async def check_phone_blacklist(phone_number: str) -> bool:
    """Check if phone number is in blacklist"""
    # Implement actual blacklist check
    return False

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "timestamp": datetime.now().isoformat()
        }
    )

if __name__ == "__main__":
    port = int(os.getenv('API_PORT', 8000))
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv('DEBUG', 'false').lower() == 'true'
    )