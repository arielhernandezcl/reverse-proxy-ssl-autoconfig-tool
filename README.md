# Reverse Proxy SSL Auto-Configuration Tool

This Python script automates the setup of an Nginx reverse proxy with automatic SSL certificate acquisition using Let's Encrypt Certbot. It simplifies the process of configuring HTTPS for applications running on local ports.

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

- **Automated Nginx Configuration**: Creates and enables Nginx reverse proxy configuration
- **SSL Certificate Management**: Automatically obtains Let's Encrypt SSL certificates
- **HTTPS Redirection**: Configures automatic HTTP to HTTPS redirection
- **Error Handling**: Comprehensive error handling and cleanup mechanisms
- **Validation**: Nginx configuration syntax validation before reload

## Prerequisites

- Ubuntu/Debian-based Linux system
- Root or sudo access
- Nginx installed and running
- Certbot installed with Nginx plugin
- Domain properly pointing to the server
- Ports 80 and 443 accessible

## Installation

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

- `-e, --email`: Email address for Let's Encrypt registration (default: `email@email`)

### Examples

```bash
# Basic usage
sudo python3 main.py example.com 5000

# With custom email
sudo python3 main.py example.com 5000 -e your-email@example.com
```

## How It Works

1. **Nginx Configuration Generation**:
   - Creates a basic HTTP configuration for the specified domain and port
   - Sets proper proxy headers for forwarding requests

2. **Configuration Activation**:
   - Creates configuration file in `/etc/nginx/sites-available/`
   - Creates symbolic link in `/etc/nginx/sites-enabled/`
   - Validates configuration syntax
   - Reloads Nginx service

3. **SSL Certificate Setup**:
   - Uses Certbot to obtain Let's Encrypt certificate
   - Automatically configures HTTPS and redirects
   - Updates Nginx configuration for SSL

## Configuration Details

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

After SSL setup, Certbot automatically updates the configuration to include HTTPS settings and redirects HTTP traffic to HTTPS.

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
- **Solution**: Install with `sudo apt install certbot python3-certbot-nginx`

#### 5. Nginx Configuration Error
- **Cause**: Invalid configuration syntax
- **Solution**: Check `/etc/nginx/sites-available/` for issues

### Debugging Commands

```bash
# Test Nginx configuration
sudo nginx -t

# Check Nginx status
sudo systemctl status nginx

# View Nginx error logs
sudo tail -f /var/log/nginx/error.log

# Check Certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log
```

### Manual Cleanup

If the script fails and leaves incomplete configuration:

```bash
# Remove configuration file
sudo rm /etc/nginx/sites-available/your-domain.conf

# Remove symbolic link
sudo rm /etc/nginx/sites-enabled/your-domain.conf

# Reload Nginx
sudo nginx -t && sudo systemctl reload nginx
```

## Security Considerations

- **Always run with sudo**: The script requires elevated privileges to modify Nginx configurations
- **Email Privacy**: Be cautious when using the default email address in production
- **Certificate Validity**: Let's Encrypt certificates are valid for 90 days; Certbot auto-renewal should be configured
- **Firewall Configuration**: Ensure proper firewall rules allow traffic on ports 80/443

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

### Manual Nginx Configuration
After running the script, you can manually edit the Nginx configuration file at:
`/etc/nginx/sites-available/your-domain.conf`

## Architecture

```
Internet (Port 80/443) → Nginx (SSL Termination) → Local Application (Custom Port)
```

The script sets up this architecture automatically:
1. Nginx receives requests on ports 80/443
2. SSL termination occurs at Nginx level
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