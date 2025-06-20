# Backend Setup Guide

This guide provides step-by-step instructions for setting up and running the Flask backend for the Event Registration Application.

## 1. Project Structure

```
register-form-app/
├── frontend/
│   ├── static/
│   │   ├── css/
│   └── templates/
│       ├── index.html
│       ├── success.html
│       └── error.html
├── backend/
│   ├── app.py
│   └── config.py
├── requirements.txt
└── .env
```

## 2. Prerequisites

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install python3-pip python3-venv
```

## 3. Setup Python Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 4. Create requirements.txt

```bash
# Create requirements.txt with these dependencies
Flask==2.0.1
python-dotenv==0.19.0
mysql-connector-python==8.0.26
boto3==1.18.44
gunicorn==20.1.0
```

## 5. Environment Variables

Create a `.env` file in the root directory:
```
# Flask configuration
FLASK_DEBUG=False  # Set to True for development, False for production
SECRET_KEY=your-secret-key-here  # Generate a secure random key for production

# Database configuration
DB_HOST=your_mysql_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
# AWS configuration
AWS_REGION=your_aws_region
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
LAMBDA_FUNCTION_NAME=your_lambda_function
```

To generate a secure secret key, you can use Python:
```bash
python3 -c 'import secrets; print(secrets.token_hex(32))'
```

Important notes about Flask configuration:
- FLASK_DEBUG:
  - True: Shows detailed errors, enables auto-reload (development only)
  - False: Hides errors, better security (use in production)
- SECRET_KEY:
  - Used for session security and CSRF protection
  - Must be kept secret
  - Should be a long random string
  - Never commit to version control

## 6. Running in Development

```bash
# Activate virtual environment
source venv/bin/activate

# Run Flask development server
python backend/app.py
```

## 7. Production Deployment with Gunicorn

1. Create Gunicorn service file:
```bash
sudo nano /etc/systemd/system/register-app.service
```

Add this content:
```ini
[Unit]
Description=Gunicorn instance to serve register application
After=network.target

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/home/ubuntu/register-form-app
Environment="PATH=/home/ubuntu/register-form-app/venv/bin"
ExecStart=/home/ubuntu/register-form-app/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5000 backend.app:app

[Install]
WantedBy=multi-user.target
```

2. Start and enable the service:
```bash
sudo systemctl start register-app
sudo systemctl enable register-app
```

## 8. Running in Background

1. Using systemd (recommended):
```bash
# Check status
sudo systemctl status register-app

# View logs
sudo journalctl -u register-app
```

2. Using screen (alternative):
```bash
# Install screen
sudo apt install screen

# Create new screen session
screen -S register-app

# Run the application
source venv/bin/activate
python backend/app.py

# Detach from screen: Press Ctrl+A, then D
# Reattach to screen: screen -r register-app
```


## 9. Monitoring

1. Check application logs:
```bash
# Gunicorn logs
sudo journalctl -u register-app

# Application logs
tail -f /home/ubuntu/register-form-app/app.log
```

2. Monitor system resources:
```bash
# Check CPU and memory usage
htop

# Check disk space
df -h
```

## 10. Troubleshooting

1. If the application doesn't start:
```bash
# Check service status
sudo systemctl status register-app

# Check logs
sudo journalctl -u register-app -n 50

# Check permissions
ls -l /home/ubuntu/register-form-app
```

2. If you can't access the application:
```bash
# Check if the port is open
sudo netstat -tulpn | grep 5000
```

## 11. Maintenance

1. Update the application:
```bash
# Pull new code
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart the service
sudo systemctl restart register-app
```

2. Backup:
```bash
# Backup database
mysqldump -u register_user -p event_registration > backup.sql

# Backup application files
tar -czf register-app-backup.tar.gz /home/ubuntu/register-form-app
```

## 13. Cleanup

To remove the application:
```bash
# Stop and disable services
sudo systemctl stop register-app
sudo systemctl disable register-app

# Remove systemd service
sudo rm /etc/systemd/system/register-app.service
sudo systemctl daemon-reload
```

Remember to:
- Keep your dependencies updated
- Monitor your logs regularly
- Backup your database
- Update your security groups as needed
- Access the application using http://your-ec2-ip:5000 