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

## 👤 Author

Created by Kamva for University of Cape Town

**Last Updated**: May 07, 2026
