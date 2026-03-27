# Email Calendar Notifier

A Python-based automation system that monitors your Outlook emails, extracts calendar events and dates, stores them in a database, and sends push notifications to your device before important events occur.

## 🎯 Features

- **Email Integration**: Connects to Microsoft 365/Outlook via OAuth 2.0
- **Intelligent Date Extraction**: Uses NLP (spaCy) and pattern matching to extract dates and events from email content
- **Event Management**: SQLite database for storing detected events with confidence scores
- **Push Notifications**: Firebase Cloud Messaging (FCM) integration for real-time alerts
- **Scheduled Processing**: Automatically checks emails at configurable intervals
- **Logging**: Comprehensive logging for debugging and monitoring
- **Notification Tracking**: Prevents duplicate notifications with `is_notified` flag

## 🏗️ Architecture

```
EmailCalendarNotifier (Main Orchestrator)
├── EmailReader (Outlook Integration)
├── DateExtractor (NLP & Pattern Matching)
├── EventManager (SQLite Database)
└── NotificationSystem (Firebase Cloud Messaging)
```

## 📋 Prerequisites

- Python 3.8+
- Microsoft 365/Outlook account
- Firebase project with Cloud Messaging enabled
- Internet connection

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd email_notifier
```

### 2. Set Up Virtual Environment

#### Windows (PowerShell)
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get an execution policy error, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### Windows (Command Prompt)
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

#### macOS/Linux (Bash/Zsh)
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install python-dotenv
pip install sqlalchemy
pip install firebase-admin
pip install spacy
pip install dateparser
pip install schedule
pip install requests
```

### 4. Download spaCy NLP Model

```bash
python -m spacy download en_core_web_sm
```

## 🔧 Configuration

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```env
# Microsoft 365 / Outlook Configuration
TENANT_ID=your_tenant_id
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
EMAIL_USER=your_email@outlook.com

# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./config/firebase-credentials.json

# Database Configuration
DATABASE_URL=sqlite:///./email_calendar.db

# Application Settings
CHECK_INTERVAL_MINUTES=5
NOTIFICATION_ADVANCE_HOURS=24
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log
```

### 2. Microsoft 365 Setup

1. Go to [Azure Portal](https://portal.azure.com)
2. Register a new application
3. Create a client secret
4. Add API permissions:
   - `Mail.Read` (Read user mail)
   - `offline_access`
5. Copy `TENANT_ID`, `CLIENT_ID`, and `CLIENT_SECRET` to `.env`

### 3. Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project
3. Download service account key (JSON file)
4. Save to `config/firebase-credentials.json`
5. Update `FIREBASE_CREDENTIALS_PATH` in `.env`

## 📖 Usage Examples

### Basic Setup

```python
from main import EmailCalendarNotifier

# Initialize the notifier with device tokens
device_tokens = [
    "token_1_from_firebase",
    "token_2_from_firebase"
]

notifier = EmailCalendarNotifier(device_tokens=device_tokens)
```

### Process Emails and Extract Events

```python
# Process all unread emails and extract calendar events
new_events = notifier.process_emails()
print(f"Found {new_events} new events")
```

### Schedule Automated Checking

```python
# Run automatic email checking every 5 minutes
notifier.schedule_checks()
```

### Get Upcoming Events

```python
# Get events happening in the next 24 hours
upcoming_events = notifier.event_manager.get_upcoming_events(hours=24)
for event in upcoming_events:
    print(f"Event: {event['description']}")
    print(f"Date: {event['event_date']}")
    print(f"Confidence: {event['confidence']}")
```

### Send Notifications

```python
# Send notification about an upcoming event
notifier.notification_system.send_notification(
    device_token="your_device_token",
    title="Upcoming Meeting",
    body="Team standup in 1 hour",
    data={
        "event_id": "123",
        "event_date": "2026-03-28T10:00:00"
    }
)
```

### Full Workflow Example

```python
from main import EmailCalendarNotifier

# Initialize
device_tokens = ["fcm_device_token_123"]
notifier = EmailCalendarNotifier(device_tokens=device_tokens)

# Step 1: Process emails
print("Processing emails...")
new_events = notifier.process_emails()
print(f"Created {new_events} new events")

# Step 2: Get upcoming events
print("\nUpcoming events:")
upcoming = notifier.event_manager.get_upcoming_events(hours=24)
for event in upcoming:
    if not event['is_notified']:
        # Step 3: Send notification
        title = f"Reminder: {event['description'][:50]}"
        body = f"Event on {event['event_date'][:10]}"
        
        notifier.notification_system.send_notification(
            device_token=device_tokens[0],
            title=title,
            body=body,
            data={
                "event_id": str(event['id']),
                "description": event['description']
            }
        )
        
        # Step 4: Mark as notified
        notifier.event_manager.mark_as_notified(event['id'])
```

## 🗄️ Database Schema

### Events Table

```sql
CREATE TABLE events (
    id INTEGER PRIMARY KEY,
    event_date DATETIME NOT NULL,
    description VARCHAR NOT NULL,
    sender VARCHAR,
    email_subject VARCHAR,
    email_id VARCHAR UNIQUE,
    confidence FLOAT DEFAULT 0.5,
    is_notified BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## 📊 Components

### EmailReader
Handles OAuth 2.0 authentication and reads emails from Microsoft 365 Outlook.

**Methods:**
- `get_unread_emails()`: Fetch unread emails
- `mark_as_read(email_id)`: Mark email as read

### DateExtractor
Extracts dates and events from email text using NLP and pattern matching.

**Methods:**
- `extract_dates_from_text(text)`: Extract all dates from email content
- `_extract_by_patterns(text)`: Regex-based extraction
- `_extract_by_nlp(text)`: spaCy NLP-based extraction

### EventManager
Manages database operations for storing and retrieving events.

**Methods:**
- `add_event(event_data)`: Store new event
- `get_upcoming_events(hours)`: Get events within N hours
- `mark_as_notified(event_id)`: Mark event as notified
- `get_event_by_id(event_id)`: Retrieve specific event

### NotificationSystem
Sends push notifications via Firebase Cloud Messaging.

**Methods:**
- `send_notification(device_token, title, body, data)`: Send to single device
- `send_topic_notification(topic, title, body, data)`: Send to topic subscribers

## 📝 Logging

Logs are stored in `logs/app.log` and console output.

### Log Levels
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about application flow
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failures

### Sample Log Output
```
2026-03-27 10:15:30 - INFO - EmailCalendarNotifier initialized successfully
2026-03-27 10:15:31 - INFO - Connected to Outlook email
2026-03-27 10:15:32 - INFO - Extracted 3 events from email
2026-03-27 10:15:33 - INFO - Notification sent successfully: message_id_123
```

## 🐛 Troubleshooting

### spaCy Model Not Found
```bash
python -m spacy download en_core_web_sm
```

### Firebase Credentials Not Found
- Verify `FIREBASE_CREDENTIALS_PATH` in `.env`
- Ensure JSON file exists at specified path
- Check file permissions

### Microsoft 365 Authentication Failed
- Verify `TENANT_ID`, `CLIENT_ID`, `CLIENT_SECRET` are correct
- Ensure application has correct API permissions
- Check if client secret has expired

### No Events Extracted
- Verify email content contains date information
- Check date format compatibility
- Review logs for extraction errors

## 📦 Virtual Environments Best Practices

### Creating a Virtual Environment

```bash
# Create
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate (macOS/Linux)
source venv/bin/activate

# Deactivate (any OS)
deactivate
```

### Generating requirements.txt

```bash
# Generate from current environment
pip freeze > requirements.txt

# Install from requirements.txt
pip install -r requirements.txt
```

### Checking Active Environment

```bash
# On Windows
where python

# On macOS/Linux
which python
```

## 🚀 Running the Application

### One-Time Execution
```bash
python main.py
```

### Continuous Monitoring
```python
from main import EmailCalendarNotifier

notifier = EmailCalendarNotifier(device_tokens=["your_tokens"])
notifier.schedule_checks()  # Runs indefinitely
```

### With systemd (Linux/macOS)

Create `email_notifier.service`:
```ini
[Unit]
Description=Email Calendar Notifier
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/email_notifier
ExecStart=/path/to/email_notifier/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable email_notifier.service
sudo systemctl start email_notifier.service
```

## 📋 Configuration Examples

### High-Frequency Checking
```env
CHECK_INTERVAL_MINUTES=1
NOTIFICATION_ADVANCE_HOURS=1
LOG_LEVEL=DEBUG
```

### Minimal Impact
```env
CHECK_INTERVAL_MINUTES=60
NOTIFICATION_ADVANCE_HOURS=48
LOG_LEVEL=WARNING
```

## 📄 License

[Specify your license here]

## 👤 Author

Created by Kamva 

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing style
- Tests pass
- Logging is appropriate
- Documentation is updated

---

**Last Updated**: March 27, 2026
