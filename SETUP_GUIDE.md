# Setup Guide: Reverse Proxy SSL Auto-Configuration Tool

## System Requirements

### Operating System
- Ubuntu 18.04 LTS or later
- Ubuntu 20.04 LTS or later (recommended)
- Ubuntu 22.04 LTS (latest supported)
- Debian 10 or later
- Other Debian-based distributions (with modifications)

### System Resources
- At least 1GB of available RAM
- 500MB of free disk space (for packages and certificates)
- Root or sudo access required

### Network Requirements
- Static public IP address
- Ports 80 and 443 accessible from the internet
- Domain name pointing to the server's IP address

## Prerequisites Installation

### Step 1: Update System Packages
```bash
sudo apt update && sudo apt upgrade -y
```

### Option A: Install Nginx Web Server
```bash
# Install Nginx
sudo apt install nginx

# Start and enable Nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify Nginx is running
sudo systemctl status nginx
```

### Option B: Install Apache2 Web Server
```bash
# Install Apache2
sudo apt install apache2

# Start and enable Apache2
sudo systemctl start apache2
sudo systemctl enable apache2

# Verify Apache2 is running
sudo systemctl status apache2
```

### Step 3: Install Certbot with Appropriate Plugin
Choose the appropriate plugin based on your web server:

For Nginx:
```bash
# Install Certbot and Nginx plugin
sudo apt install certbot python3-certbot-nginx

# Verify installation
certbot --version
```

For Apache2:
```bash
# Install Certbot and Apache2 plugin
sudo apt install certbot python3-certbot-apache

# Verify installation
certbot --version
```

### Step 4: Configure Firewall (if using UFW)
```bash
# Allow SSH (if needed)
sudo ufw allow ssh
sudo ufw allow OpenSSH

# Allow HTTP and HTTPS
# For Nginx:
sudo ufw allow 'Nginx Full'

# For Apache2:
sudo ufw allow 'Apache Full'
# Or separately for both:
sudo ufw allow 80
sudo ufw allow 443

# Enable firewall (if not already enabled)
sudo ufw enable

# Check status
sudo ufw status
```

### Step 5: Verify Domain DNS Configuration
```bash
# Verify your domain points to your server's IP
nslookup your-domain.com
# Should return your server's public IP address

# Alternative check
dig your-domain.com +short
```

## Installation of the Proxy Tool

### Step 1: Download the Script
```bash
# Create a directory for the script
mkdir ~/nginx-proxy-setup
cd ~/nginx-proxy-setup

# Copy the main.py script to this location
# (Use your preferred method: git, wget, scp, etc.)
```

### Step 2: Set Proper Permissions
```bash
# Make sure the script is executable
chmod +x main.py

# Verify the script
ls -la main.py
```

### Step 3: Test Basic Script Execution
```bash
# Check if Python is available
python3 --version

# Test script execution (without parameters to see help)
python3 main.py --help
```

## Verification of Prerequisites

### Verify Web Server Installation

For Nginx:
```bash
# Check if Nginx is installed and running
nginx -v
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# Verify Nginx serves on port 80
curl -I http://localhost
```

For Apache2:
```bash
# Check if Apache2 is installed and running
apache2 -v
sudo systemctl status apache2

# Test Apache2 configuration
sudo apache2ctl configtest

# Verify Apache2 serves on port 80
curl -I http://localhost
```

### Verify Certbot Installation
```bash
# Check certbot version and installation
certbot --version

# Test certbot with appropriate plugin
certbot plugins
# Should list "nginx" or "apache" in the installed plugins depending on your setup
```

### Verify System Permissions
```bash
# Check if user has sudo access
sudo -l

# Verify script execution with sudo
sudo python3 main.py --help
```

## Preparing Your Application

### Step 1: Deploy Your Application
Your application should be running on the server before setting up the proxy. Examples:

**For Node.js applications:**
```bash
# Example: Node.js app on port 3000
node app.js &
# Or using PM2:
pm2 start app.js --name myapp --port 3000
```

**For Python Flask applications:**
```bash
# Example: Flask app on port 5000
export FLASK_APP=app.py
flask run --host=0.0.0.0 --port=5000 &
```

**For Python Django applications:**
```bash
# Example: Django app on port 8000
python manage.py runserver 0.0.0.0:8000 &
```

### Step 2: Verify Application is Running
```bash
# Test if your application is responding
curl http://localhost:YOUR_APP_PORT

# Verify the application is accessible locally
netstat -tuln | grep YOUR_APP_PORT
netstat -tuln | grep :3000  # Example for port 3000
```

### Step 3: Configure Application for Proxy
Ensure your application is configured to:
- Accept connections from all hosts (0.0.0.0) or localhost
- Trust proxy headers if needed
- Handle HTTPS redirects properly

## Pre-Configuration Checks

### Network Connectivity
```bash
# Check if ports 80 and 443 are accessible from outside
sudo netstat -tuln | grep :80
sudo netstat -tuln | grep :443

# Test external accessibility (from another machine)
curl -I http://your-domain.com
```

### DNS Propagation
```bash
# Wait for DNS propagation before running the script
nslookup your-domain.com
# Should return your server's IP

# Alternative check
ping your-domain.com
```

### Domain Validation Requirements
Before running the script, ensure:
- [ ] Domain registrar's DNS settings point to your server IP
- [ ] DNS propagation is complete (can take 24-48 hours for new domains)
- [ ] No other services are using ports 80 and 443
- [ ] Your application is running on the specified local port
- [ ] You have a valid email address for Let's Encrypt registration

## Running a Test Configuration

### Before Production Use
You can test the configuration process with a dry run approach:

1. **Test HTTP-only configuration first** (without SSL):

For Nginx:
   ```bash
   # Manually create a simple Nginx config to test proxy
   sudo nano /etc/nginx/sites-available/test-proxy
   ```

   Add this test configuration:
   ```nginx
   server {
       listen 80;
       listen [::]:80;
       server_name your-domain.com;

       location / {
           proxy_pass http://localhost:YOUR_PORT;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

For Apache2:
   ```bash
   # Manually create a simple Apache2 config to test proxy
   sudo nano /etc/apache2/sites-available/test-proxy.conf
   ```

   Add this test configuration:
   ```apache
   <VirtualHost *:80>
       ServerName your-domain.com

       <Proxy "*">
           Order deny,allow
           Allow from all
       </Proxy>

       ProxyPreserveHost On
       ProxyRequests Off

       ProxyPass / http://localhost:YOUR_PORT/
       ProxyPassReverse / http://localhost:YOUR_PORT/

       ErrorLog ${APACHE_LOG_DIR}/error_test-proxy.log
       CustomLog ${APACHE_LOG_DIR}/access_test-proxy.log combined
   </VirtualHost>
   ```

2. **Enable the test configuration**:

For Nginx:
   ```bash
   sudo ln -s /etc/nginx/sites-available/test-proxy /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

For Apache2:
   ```bash
   sudo a2ensite test-proxy.conf
   sudo apache2ctl configtest
   sudo systemctl reload apache2
   ```

3. **Test HTTP access**:
   ```bash
   curl http://your-domain.com
   ```

## Security Preparations

### SSL Certificate Information
- Have a valid email address ready for Let's Encrypt registration
- Understand that Let's Encrypt certificates are free and valid for 90 days
- Plan for automatic renewal setup after successful initial configuration

### Firewall Configuration
```bash
# Recommended firewall settings
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh    # Or your SSH port if different
sudo ufw allow 80     # HTTP
sudo ufw allow 443    # HTTPS
sudo ufw enable
```

## System Monitoring Setup

### Log Configuration
After successful setup, monitor these logs:

For Nginx:
```bash
# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs for Nginx
sudo journalctl -u nginx -f
```

For Apache2:
```bash
# Apache2 access logs
sudo tail -f /var/log/apache2/access.log

# Apache2 error logs
sudo tail -f /var/log/apache2/error.log

# System logs for Apache2
sudo journalctl -u apache2 -f
```

### Certificate Renewal Setup
```bash
# Add automatic renewal to crontab
sudo crontab -e

# Add this line for automatic renewal twice daily:
0 12 * * * /usr/bin/certbot renew --quiet
0 0 * * * /usr/bin/certbot renew --quiet
```

## Troubleshooting Preparation

### Essential Commands for Debugging

For Nginx:
```bash
# Nginx configuration test
sudo nginx -t

# Nginx status
sudo systemctl status nginx

# Check Nginx configuration files
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/sites-enabled/
```

For Apache2:
```bash
# Apache2 configuration test
sudo apache2ctl configtest

# Apache2 status
sudo systemctl status apache2

# Check Apache2 configuration files
ls -la /etc/apache2/sites-available/
ls -la /etc/apache2/sites-enabled/
```

Common commands:
```bash
# Check active connections
sudo netstat -tulnp | grep :80
sudo netstat -tulnp | grep :443

# Certbot certificate status
sudo certbot certificates
```

## Final Pre-Run Checklist

Before executing the main script, verify:
- [ ] System is updated with latest packages
- [ ] Nginx is installed and running
- [ ] Certbot is installed with Nginx plugin
- [ ] Domain DNS points to server IP
- [ ] Ports 80 and 443 are accessible
- [ ] Your application is running on the target port
- [ ] You have a valid email for Let's Encrypt
- [ ] You have sudo access to run the script
- [ ] Firewall allows HTTP/HTTPS traffic
- [ ] No other services are using ports 80/443

## Running the Configuration Script

Once all prerequisites are verified:

### For Auto-Detection
```bash
sudo python3 main.py your-domain.com your-app-port -e your-email@example.com
```

### For Nginx Specifically
```bash
sudo python3 main.py your-domain.com your-app-port -e your-email@example.com -s nginx
```

### For Apache2 Specifically
```bash
sudo python3 main.py your-domain.com your-app-port -e your-email@example.com -s apache2
```

Examples:
```bash
# Auto-detect web server
sudo python3 main.py example.com 3000 -e admin@example.com

# Force Nginx usage
sudo python3 main.py example.com 3000 -e admin@example.com -s nginx

# Force Apache2 usage
sudo python3 main.py example.com 3000 -e admin@example.com -s apache2
```

This setup guide provides all the necessary steps to prepare your system for using the reverse proxy SSL auto-configuration tool, ensuring a smooth installation and configuration process.