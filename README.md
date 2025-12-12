# Reverse Proxy SSL Auto-Configuration Tool

This Python script automates the setup of a reverse proxy (Nginx or Apache2) with automatic SSL certificate acquisition using Let's Encrypt Certbot. It simplifies the process of configuring HTTPS for applications running on local ports.

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Configuration Details](#configuration-details)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)
- [License](#license)

## Features

- **Automated Web Server Configuration**: Creates and enables reverse proxy configuration for Nginx or Apache2
- **Automatic Server Detection**: Detects and uses available web server (Nginx or Apache2) if not specified
- **SSL Certificate Management**: Automatically obtains Let's Encrypt SSL certificates
- **HTTPS Redirection**: Configures automatic HTTP to HTTPS redirection
- **Error Handling**: Comprehensive error handling and cleanup mechanisms
- **Flexible Configuration**: Supports both Nginx and Apache2 configurations

## Prerequisites

- Ubuntu/Debian-based Linux system
- Root or sudo access
- Either Nginx or Apache2 installed and running
- Certbot installed with appropriate plugin (Nginx or Apache2)
- Domain properly pointing to the server
- Ports 80 and 443 accessible

## Installation

### For Nginx:

1. **Install Nginx**:
```bash
sudo apt update
sudo apt install nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

2. **Install Certbot with Nginx plugin**:
```bash
sudo apt install certbot python3-certbot-nginx
```

### For Apache2:

1. **Install Apache2**:
```bash
sudo apt update
sudo apt install apache2
sudo systemctl start apache2
sudo systemctl enable apache2
```

2. **Install Certbot with Apache2 plugin**:
```bash
sudo apt install certbot python3-certbot-apache
```

3. **Clone or download the script**:
```bash
# Place the main.py script in an appropriate location
```

## Usage

```bash
sudo python3 main.py <domain> <port> [options]
```

### Parameters

- `<domain>`: Your domain name (e.g., `example.com`)
- `<port>`: Local application port (e.g., `5000`)

### Options

- `-e, --email`: Email address for Let's Encrypt registration (default: `#`)
- `-s, --server`: Specify web server to use: `nginx` or `apache2` (optional, auto-detects if not specified)

### Examples

```bash
# Basic usage (auto-detects web server)
sudo python3 main.py example.com 5000

# With custom email
sudo python3 main.py example.com 5000 -e your-email@example.com

# Force Nginx usage
sudo python3 main.py example.com 5000 -s nginx

# Force Apache2 usage
sudo python3 main.py example.com 5000 -s apache2
```

## How It Works

1. **Web Server Detection**:
   - If no server is specified with `-s`, the script detects available web server (Nginx or Apache2)
   - Uses the detected or specified server for the rest of the process

2. **Configuration Generation**:
   - Creates a basic HTTP configuration for the specified domain and port
   - Sets proper proxy headers for forwarding requests
   - Uses appropriate configuration format for detected server (Nginx or Apache2)

3. **Configuration Activation**:
   - For Nginx: Creates configuration file in `/etc/nginx/sites-available/` and symbolic link in `/etc/nginx/sites-enabled/`
   - For Apache2: Creates configuration file in `/etc/apache2/sites-available/` and enables site with `a2ensite`
   - Validates configuration syntax
   - Reloads web server service

4. **SSL Certificate Setup**:
   - Uses Certbot with appropriate plugin (Nginx or Apache2) to obtain Let's Encrypt certificate
   - Automatically configures HTTPS and redirects
   - Updates web server configuration for SSL

## Configuration Details

### Nginx Configuration

The script generates an Nginx configuration with the following features:

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:your-port;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Apache2 Configuration

The script generates an Apache2 configuration with the following features:

```apache
<VirtualHost *:80>
    ServerName your-domain.com

    <Proxy "*">
        Order deny,allow
        Allow from all
    </Proxy>

    ProxyPreserveHost On
    ProxyRequests Off

    ProxyPass / http://localhost:your-port/
    ProxyPassReverse / http://localhost:your-port/

    ErrorLog ${APACHE_LOG_DIR}/error_your-domain.com.log
    CustomLog ${APACHE_LOG_DIR}/access_your-domain.com.log combined
</VirtualHost>
```

After SSL setup, Certbot automatically updates the configuration to include HTTPS settings and redirects HTTP traffic to HTTPS for both web servers.

### Proxy Headers Explained

- `$host`: Preserves the original host header
- `$remote_addr`: Sets real IP address of client
- `$proxy_add_x_forwarded_for`: Adds client IP to forwarding chain
- `$scheme`: Preserves the original protocol (HTTP/HTTPS)

## Troubleshooting

### Common Issues

#### 1. Permission Denied
- **Cause**: Script not run with sudo
- **Solution**: Always run with `sudo python3 main.py ...`

#### 2. Port Not Accessible
- **Cause**: Ports 80/443 blocked or in use
- **Solution**: Ensure ports 80/443 are open and not used by other services

#### 3. DNS Not Pointing to Server
- **Cause**: Domain doesn't resolve to server IP
- **Solution**: Verify DNS A record points to server public IP

#### 4. Certbot Installation Missing
- **Cause**: Certbot not installed
- **Solution**: Install the appropriate plugin:
  - For Nginx: `sudo apt install certbot python3-certbot-nginx`
  - For Apache2: `sudo apt install certbot python3-certbot-apache`

#### 5. Nginx Configuration Error
- **Cause**: Invalid configuration syntax
- **Solution**: Check `/etc/nginx/sites-available/` for issues

#### 6. Apache2 Configuration Error
- **Cause**: Invalid configuration syntax or missing modules
- **Solution**: Check `/etc/apache2/sites-available/` for issues and ensure proxy modules are enabled:
  - `sudo a2enmod proxy proxy_http`

#### 7. Web Server Detection Failure
- **Cause**: Neither Nginx nor Apache2 detected or both installed but one misconfigured
- **Solution**: Explicitly specify server with `-s nginx` or `-s apache2`

### Debugging Commands

For Nginx:
```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

For Apache2:
```bash
# Test Apache2 configuration
sudo apache2ctl configtest

# Check Apache2 status
sudo systemctl status apache2

# View Apache2 error logs
sudo tail -f /var/log/apache2/error.log
```

Common commands:
```bash
# Check Certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Check listening ports
sudo netstat -tuln | grep :80
sudo netstat -tuln | grep :443
```

### Manual Cleanup

If the script fails and leaves incomplete configuration:

For Nginx:
```bash
# Remove configuration file
sudo rm /etc/nginx/sites-available/your-domain.conf

# Remove symbolic link
sudo rm /etc/nginx/sites-enabled/your-domain.conf

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx
```

For Apache2:
```bash
# Disable the site
sudo a2dissite your-domain.conf

# Remove configuration file
sudo rm /etc/apache2/sites-available/your-domain.conf

# Reload Apache2
sudo systemctl reload apache2
```

## Security Considerations

- **Always run with sudo**: The script requires elevated privileges to modify web server configurations
- **Email Privacy**: Be cautious when using the default email address in production
- **Certificate Validity**: Let's Encrypt certificates are valid for 90 days; Certbot auto-renewal should be configured
- **Firewall Configuration**: Ensure proper firewall rules allow traffic on ports 80/443
- **Web Server Modules**: For Apache2, ensure only necessary modules are enabled

### Certificate Renewal

Configure automatic renewal for Let's Encrypt certificates:

```bash
sudo crontab -e
```

Add the following line to check for renewal twice daily:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

## Advanced Configuration

### Custom Email Address
Use the `-e` or `--email` flag to specify your email address instead of the default one:

```bash
sudo python3 main.py example.com 5000 -e admin@example.com
```

### Specify Web Server Explicitly
Use the `-s` or `--server` flag to specify which web server to use:

```bash
# Force Nginx
sudo python3 main.py example.com 5000 -s nginx

# Force Apache2
sudo python3 main.py example.com 5000 -s apache2
```

### Manual Configuration
After running the script, you can manually edit the configuration file at:
- For Nginx: `/etc/nginx/sites-available/your-domain.conf`
- For Apache2: `/etc/apache2/sites-available/your-domain.conf`

## Architecture

```
Internet (Port 80/443) → Web Server (SSL Termination) → Local Application (Custom Port)
```

The script sets up this architecture automatically:
1. Web server (Nginx/Apache2) receives requests on ports 80/443
2. SSL termination occurs at web server level
3. Requests are forwarded to your application running on localhost:port
4. Response flows back through the same path

## Support

If you encounter issues:

1. Verify all prerequisites are met
2. Check system logs for specific error messages
3. Ensure your domain properly resolves to the server
4. Confirm ports 80/443 are accessible from the internet
5. Run the script with verbose output to see detailed logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Submit a pull request

## License

This project is free to use and modify. See the LICENSE file for details.

## Acknowledgments

- [Nginx](https://nginx.org/) for the web server software
- [Certbot](https://certbot.eff.org/) for the Let's Encrypt client
- [Let's Encrypt](https://letsencrypt.org/) for free SSL certificates