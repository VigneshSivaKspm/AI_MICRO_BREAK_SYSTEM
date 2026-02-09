# API Documentation

## Base URL
```
http://localhost:5050/api/v1
```

## Authentication
Currently no authentication required. In production, implement JWT tokens.

---

## Endpoints

### Health Check

#### GET /health
Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-01-27T10:30:00",
  "version": "1.0.0"
}
```

---

### User Management

#### POST /users/register
Register a new user.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePassword123",
  "preferred_break_types": ["eye_exercise", "stretching"]
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "username": "john_doe"
}
```

---

### Monitoring

#### POST /monitoring/start
Start user activity monitoring and fatigue detection.

**Response:**
```json
{
  "message": "Monitoring started",
  "timestamp": "2026-01-27T10:30:00"
}
```

#### POST /monitoring/stop
Stop user activity monitoring and fatigue detection.

**Response:**
```json
{
  "message": "Monitoring stopped",
  "timestamp": "2026-01-27T10:35:00"
}
```

#### GET /activity/current
Get current activity status.

**Response:**
```json
{
  "mouse_clicks": 45,
  "keyboard_presses": 120,
  "idle_time": 25,
  "is_idle": false,
  "activity_level": 0.65,
  "last_activity": "2026-01-27T10:30:45",
  "buffer_size": 150
}
```

---

### Fatigue Detection

#### GET /fatigue/status
Get current fatigue detection status.

**Response:**
```json
{
  "fatigue_score": 0.65,
  "is_fatigued": true,
  "eye_strain_level": 55,
  "eye_strain_high": true,
  "blink_rate": 18.5,
  "posture_score": 0.75,
  "poor_posture": false,
  "facial_expression": "stressed",
  "timestamp": "2026-01-27T10:30:00",
  "alert_generated": true
}
```

#### GET /fatigue/recommendations
Get recommendations based on detected fatigue.

**Response:**
```json
{
  "recommendations": [
    {
      "type": "eye_exercise",
      "description": "Eye strain detected. Do the 20-20-20 exercise.",
      "priority": "high"
    },
    {
      "type": "break",
      "description": "High fatigue detected. Take a break now.",
      "priority": "critical"
    }
  ]
}
```

---

### Break Management

#### POST /breaks/enforce
Enforce a break with specified parameters.

**Request Body:**
```json
{
  "duration": 5,
  "break_type": "micro",
  "lock_screen": false,
  "mute_input": false
}
```

**Response:**
```json
{
  "message": "micro break enforced",
  "duration": 5,
  "timestamp": "2026-01-27T10:30:00"
}
```

#### GET /breaks/status
Get current break enforcement status.

**Response (No Active Break):**
```json
{
  "is_enforcing": false,
  "status": "Not enforcing",
  "elapsed_time": 0
}
```

**Response (Active Break):**
```json
{
  "is_enforcing": true,
  "break_type": "micro",
  "status": "Enforcing break",
  "elapsed_time": 45,
  "remaining_time": 255,
  "total_duration": 300,
  "screen_locked": false,
  "input_muted": false,
  "progress": 15.0
}
```

#### POST /breaks/stop
Stop current break enforcement.

**Response:**
```json
{
  "message": "Break enforcement stopped"
}
```

---

### Recommendations

#### GET /recommendations
Get personalized break recommendations.

**Query Parameters:**
- `user_id` (optional, default: 1): User ID
- `count` (optional, default: 2): Number of recommendations

**Example:** `/recommendations?user_id=1&count=3`

**Response:**
```json
{
  "recommendations": [
    {
      "id": 1,
      "category": "eye_exercise",
      "title": "20-20-20 Rule",
      "description": "Every 20 minutes, look at something 20 feet away for 20 seconds",
      "duration": 1,
      "difficulty": "easy",
      "benefits": "Reduces eye strain and prevents digital eye fatigue",
      "instructions": "1. Stop looking at your screen\n2. Find an object 20 feet away\n3. Stare at it for 20 seconds\n4. Return to work"
    },
    {
      "id": 3,
      "category": "breathing",
      "title": "4-7-8 Breathing",
      "description": "Inhale for 4, hold for 7, exhale for 8",
      "duration": 3,
      "difficulty": "easy",
      "benefits": "Reduces stress and promotes relaxation",
      "instructions": "1. Sit comfortably\n2. Inhale through nose for 4 counts\n3. Hold for 7 counts\n4. Exhale for 8 counts\n5. Repeat 4 times"
    }
  ]
}
```

---

### Personalization

#### GET /personalization/profile
Get user's personalization profile.

**Query Parameters:**
- `user_id` (optional, default: 1): User ID

**Response:**
```json
{
  "user_id": 1,
  "created_at": "2026-01-27T10:00:00",
  "preferred_break_types": ["eye_exercise", "stretching", "walking"],
  "optimal_break_time": "10:00-18:00",
  "fatigue_threshold": 0.7,
  "peak_productivity_hours": [10, 14, 16],
  "break_preferences": {},
  "activity_pattern": {},
  "break_compliance_rate": 0.92,
  "average_fatigue_level": 0.45,
  "learning_phase": false,
  "data_points_collected": 250,
  "last_updated": "2026-01-27T10:30:00",
  "personalization_level": "intermediate"
}
```

#### PUT /personalization/preferences
Update user preferences.

**Request Body:**
```json
{
  "user_id": 1,
  "preferences": {
    "preferred_break_types": ["eye_exercise", "meditation"],
    "optimal_break_time": "09:00-17:00",
    "fatigue_threshold": 0.65
  }
}
```

**Response:**
```json
{
  "message": "Preferences updated"
}
```

#### POST /personalization/analyze
Analyze user patterns for personalization.

**Request Body:**
```json
{
  "user_id": 1
}
```

**Response:**
```json
{
  "user_id": 1,
  "analysis_time": "2026-01-27T10:30:00",
  "activity_analysis": {
    "hourly_averages": {
      "9": 0.45,
      "10": 0.72,
      "11": 0.68
    },
    "peak_hours": [10, 11, 14],
    "average_activity_level": 0.62
  },
  "fatigue_analysis": {
    "average_fatigue": 0.48,
    "max_fatigue": 0.85,
    "min_fatigue": 0.2,
    "fatigue_std": 0.15,
    "high_fatigue_periods": [
      {"hour": 15, "count": 5},
      {"hour": 16, "count": 3}
    ]
  },
  "break_patterns": {
    "break_type_frequency": {"micro": 45, "regular": 20},
    "total_breaks": 65,
    "compliance_rate": 0.92
  },
  "recommendations": [
    {
      "type": "optimal_break_time",
      "message": "Peak activity detected during hours: [10, 11, 14]",
      "peak_hours": [10, 11, 14]
    }
  ]
}
```

---

### Analytics

#### GET /analytics/daily
Get daily productivity metrics.

**Query Parameters:**
- `user_id` (optional, default: 1): User ID

**Response:**
```json
{
  "user_id": 1,
  "date": "2026-01-27",
  "total_work_time": 27000,
  "total_break_time": 2700,
  "total_active_time": 29700,
  "productivity_score": 78.5,
  "average_fatigue_level": 0.45,
  "break_compliance_rate": 0.92,
  "focus_score": 85.3,
  "session_count": 12,
  "break_count": 8,
  "fatigue_event_count": 5
}
```

#### GET /analytics/weekly
Get weekly productivity metrics.

**Query Parameters:**
- `user_id` (optional, default: 1): User ID

**Response:**
```json
{
  "user_id": 1,
  "period": "2026-01-21 to 2026-01-27",
  "average_productivity_score": 76.8,
  "average_fatigue_level": 0.48,
  "average_compliance_rate": 0.89,
  "total_work_time": 189000,
  "total_break_time": 18900,
  "daily_breakdown": [...]
}
```

#### GET /analytics/monthly
Get monthly productivity metrics.

**Query Parameters:**
- `user_id` (optional, default: 1): User ID

**Response:**
```json
{
  "user_id": 1,
  "period": "Last 30 days (ending 2026-01-27)",
  "average_productivity_score": 75.4,
  "average_fatigue_level": 0.50,
  "average_compliance_rate": 0.87,
  "total_metrics_days": 30
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields"
}
```

### 404 Not Found
```json
{
  "error": "Endpoint not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting

Default rate limit: 1000 requests per hour

---

## CORS Policy

Enabled for: `http://localhost:3000`, `http://localhost:5000`

---

## Versioning

Current API Version: **v1**

All endpoints use `/api/v1` prefix.

---

**API Documentation Version**: 1.0.0  
**Last Updated**: January 27, 2026
