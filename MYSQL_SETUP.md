# MySQL Setup Guide for EC2

This guide provides step-by-step instructions for setting up MySQL on an EC2 instance for the Event Registration Application.

## 1. Install MySQL Server

```bash
# Update package list
sudo apt update

# Install MySQL Server
sudo apt install mysql-server

# Start MySQL service
sudo systemctl start mysql

# Enable MySQL to start on boot
sudo systemctl enable mysql

# Check MySQL status
sudo systemctl status mysql
```

## 2. Secure MySQL Installation

```bash
# Run MySQL secure installation script
sudo mysql_secure_installation

# Follow the prompts:
# - Set root password
# - Remove anonymous users
# - Disallow root login remotely
# - Remove test database
# - Reload privilege tables
```

## 3. Configure MySQL to Accept Remote Connections

```bash
# Edit MySQL configuration
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Find the line with bind-address and change it to:
bind-address = 0.0.0.0

# Restart MySQL
sudo systemctl restart mysql
```

## 4. Create Database and User

```bash
# Login to MySQL as root
sudo mysql -u root -p

# Create database
CREATE DATABASE your_db_name;

# Create user and grant privileges
CREATE USER 'your_db_user'@'%' IDENTIFIED BY 'your_db_password';
GRANT ALL PRIVILEGES ON your_db_name.* TO 'your_db_user'@'%';
FLUSH PRIVILEGES;
```

## 5. Create Required Tables

```sql
USE your_db_name;

CREATE TABLE your_table_name (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL,
    designation VARCHAR(50) NOT NULL,
    it_experience VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    llm_decision VARCHAR(10),
    email_sent BOOLEAN DEFAULT FALSE
);
```

## 6. Configure Security Group

1. Go to AWS EC2 Console
2. Select your instance's security group
3. Add inbound rule:
   - Type: MySQL/Aurora (3306)
   - Source: Anywhere-IPv4 (0.0.0.0/0)
   - Description: Allow MySQL access

## 7. Verify Setup

```bash
# Test local connection
mysql -u your_db_user -p your_db_name

# Test remote connection (from another machine)
mysql -h <EC2_PUBLIC_IP> -u your_db_user -p your_db_name
```

## 8. Environment Variables for Application

Set these environment variables in your application:
```
DB_HOST=<EC2_PUBLIC_IP>
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

## 9. Useful MySQL Commands

```sql
-- View all users and their hosts
SELECT user, host FROM mysql.user;

-- View user privileges
SHOW GRANTS FOR 'your_db_user'@'%';

-- View table structure
DESCRIBE your_table_name;

-- View all records
SELECT * FROM your_table_name;

-- Clear table data and reset auto-increment
TRUNCATE TABLE your_table_name;
```

## 10. Troubleshooting

1. If connection fails:
   ```bash
   # Check MySQL status
   sudo systemctl status mysql
   
   # Check MySQL logs
   sudo tail -f /var/log/mysql/error.log
   
   # Verify MySQL is listening
   sudo netstat -tlnp | grep mysql
   ```

2. If user can't connect:
   ```sql
   -- Check user permissions
   SHOW GRANTS FOR 'your_db_user'@'%';
   
   -- Recreate user if needed
   DROP USER IF EXISTS 'your_db_user'@'%';
   CREATE USER 'your_db_user'@'%' IDENTIFIED BY 'your_db_password';
   GRANT ALL PRIVILEGES ON your_db_name.* TO 'your_db_user'@'%';
   FLUSH PRIVILEGES;
   ```

## 11. Backup and Restore

```bash
# Backup database
mysqldump -u your_db_user -p your_db_name > backup.sql

# Restore database
mysql -u your_db_user -p your_db_name < backup.sql
```


Remember to replace `<EC2_PUBLIC_IP>` with your actual EC2 instance's public IP address. 