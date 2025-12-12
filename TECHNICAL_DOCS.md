# Technical Documentation: Reverse Proxy SSL Auto-Configuration Tool

## Overview

This Python script automates the setup of a reverse proxy (Nginx or Apache2) with SSL certificate acquisition from Let's Encrypt. It streamlines the process of making local applications accessible via HTTPS by generating web server configurations and managing SSL certificates automatically.

## Code Structure

### File Organization

- `main.py`: Main executable script containing all functionality
- `README.md`: Project documentation (generated)

### Module Dependencies

- `argparse`: For command-line argument parsing
- `subprocess`: For executing system commands (nginx, apache2ctl, certbot, systemctl, a2ensite, a2enmod)
- `os`: For file system operations and permission checking

## Core Components

### 1. Configuration Constants

```python
CERTBOT_EMAIL = "#"  # Default email for Let's Encrypt registration
NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"  # Nginx configuration directory
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"     # Nginx enabled sites directory
APACHE_SITES_AVAILABLE = "/etc/apache2/sites-available"  # Apache2 configuration directory
APACHE_A2ENSITE = ["a2ensite"]  # Apache2 command for enabling sites
```

### 2. Web Server Detection

#### `detect_web_server()`

- **Purpose**: Detects if Nginx or Apache2 are installed and active
- **Process**:
  1. Tries to run `nginx -v` and checks for `/etc/nginx/sites-available` directory
  2. If Nginx is not found, tries `apache2ctl -v` and checks for `/etc/apache2/sites-available` directory
  3. Returns "nginx", "apache2", or None based on detection
- **Use**: Used when no server is specified via the `--server` argument

### 3. Nginx Configuration Functions

#### `generate_nginx_config(domain, port)`

- **Purpose**: Creates the initial HTTP configuration for the reverse proxy
- **Parameters**:
  - `domain` (str): Domain name for the proxy
  - `port` (int): Local port of the target application
- **Returns**: String containing Nginx server block configuration
- **Headers Set**:
  - `Host`: Maintains original host header
  - `X-Real-IP`: Sets real IP of client
  - `X-Forwarded-For`: Adds IP to forwarding chain
  - `X-Forwarded-Proto`: Preserves original protocol

#### `create_and_enable_nginx_proxy(domain, config_content)`

- **Purpose**: Creates configuration file and enables it in Nginx
- **Parameters**:
  - `domain` (str): Domain name for the proxy
  - `config_content` (str): Nginx configuration content
- **Process**:
  1. Writes configuration to `/etc/nginx/sites-available/{domain}.conf`
  2. Creates symbolic link in `/etc/nginx/sites-enabled/`
  3. Validates Nginx configuration syntax with `nginx -t`
  4. Reloads Nginx service with `systemctl reload nginx`
- **Error Handling**: Removes symbolic link on failure and provides detailed error messages

#### `run_certbot_nginx(domain, email)`

- **Purpose**: Acquires and installs Let's Encrypt SSL certificate using Nginx plugin
- **Parameters**:
  - `domain` (str): Domain name for certificate
  - `email` (str): Email for Let's Encrypt registration
- **Process**:
  1. Executes Certbot with Nginx plugin
  2. Configures automatic HTTP to HTTPS redirect
  3. Updates Nginx configuration for SSL
- **Error Handling**: Provides specific troubleshooting information based on error types

### 4. Apache2 Configuration Functions

#### `generate_apache_config(domain, port)`

- **Purpose**: Creates the initial HTTP configuration for the reverse proxy
- **Parameters**:
  - `domain` (str): Domain name for the proxy
  - `port` (int): Local port of the target application
- **Returns**: String containing Apache2 VirtualHost configuration
- **Headers Set**:
  - `ProxyPreserveHost On`: Maintains original host header
  - Proper proxy settings for forwarding requests

#### `enable_apache_proxy_modules()`

- **Purpose**: Enables required proxy modules for Apache2
- **Process**:
  1. Enables `proxy` module using `a2enmod`
  2. Enables `proxy_http` module using `a2enmod`
- **Error Handling**: Checks if modules are already enabled

#### `create_and_enable_apache_proxy(domain, config_content)`

- **Purpose**: Creates configuration file and enables it in Apache2
- **Parameters**:
  - `domain` (str): Domain name for the proxy
  - `config_content` (str): Apache2 configuration content
- **Process**:
  1. Calls `enable_apache_proxy_modules()` to ensure required modules are loaded
  2. Writes configuration to `/etc/apache2/sites-available/{domain}.conf`
  3. Enables site with `a2ensite {domain}.conf`
  4. Validates Apache2 configuration syntax with `apache2ctl configtest`
  5. Reloads Apache2 service with `systemctl reload apache2`
- **Error Handling**: Disables the site on failure and provides detailed error messages

#### `run_certbot_apache(domain, email)`

- **Purpose**: Acquires and installs Let's Encrypt SSL certificate using Apache2 plugin
- **Parameters**:
  - `domain` (str): Domain name for certificate
  - `email` (str): Email for Let's Encrypt registration
- **Process**:
  1. Executes Certbot with Apache2 plugin
  2. Configures automatic HTTP to HTTPS redirect
  3. Updates Apache2 configuration for SSL
- **Error Handling**: Provides specific troubleshooting information based on error types

### 5. Main Execution Flow

#### `main()`

- **Purpose**: Orchestrates the complete proxy and SSL setup process
- **Process**:
  1. Parses command-line arguments including optional server specification
  2. Determines web server to use (auto-detect or specified via `--server`)
  3. Generates appropriate HTTP configuration based on web server
  4. Sets up reverse proxy with selected web server (Nginx or Apache2)
  5. Acquires SSL certificate via Certbot using appropriate plugin
  6. Configures HTTPS redirection

## Execution Flow

```
1. Command-line arguments validation
2. ┌─ Web Server Selection
3. │  ├── Use --server argument if provided
4. │  └── Auto-detect if argument is not provided
5. │
6. │  ┌─ HTTP Configuration Creation for selected web server
7. │  │  ├── Generate appropriate config (Nginx or Apache2)
8. │  │  ├── Save to sites-available
9. │  │  ├── Enable (symlink for Nginx, a2ensite for Apache2)
10. │  │  ├── Validate syntax
11. │  │  └── Reload service
12. │  │
13. │  └─ SSL Certificate Setup
14. │      ├── Run Certbot with appropriate plugin
15. │      ├── Configure HTTPS
16. │      └── Update web server config for SSL
```

## Error Handling Strategy

### Subprocess Error Handling

- Uses `subprocess.CalledProcessError` for system command failures
- Captures and displays stderr output for debugging
- Implements cleanup procedures in case of failures

### File System Error Handling

- Validates file operations
- Removes created files/links on failure
- Provides clear error messages to user

### Web Server-Specific Error Handling

Nginx:
- Validates configuration before reload
- Restores previous state on configuration errors
- Provides Nginx-specific troubleshooting information

Apache2:
- Enables required proxy modules before configuration
- Disables site on failure
- Provides Apache2-specific troubleshooting information

## Security Considerations

### Privilege Management

- Requires root privileges (validated at startup)
- Uses symbolic links for Nginx configuration management
- Uses a2ensite/a2dissite for Apache2 configuration management
- Follows file permission best practices for both web servers

### Input Validation

- Validates domain format (implicit via argument parsing)
- Validates port number (integer type check)
- Uses secure subprocess execution

### Certificate Security

- Uses Let's Encrypt certificates (trusted CA)
- Configures automatic HTTP to HTTPS redirects
- Implements standard SSL security headers via Certbot

## System Requirements

### Mandatory Dependencies

- Python 3.x
- Either Nginx or Apache2 web server
- Certbot client with appropriate plugin (Nginx or Apache2)
- systemd (for systemctl commands)

### File System Access

For Nginx:
- Write access to `/etc/nginx/sites-available/`
- Write access to `/etc/nginx/sites-enabled/`
- Nginx service management permissions

For Apache2:
- Write access to `/etc/apache2/sites-available/`
- Execute permissions for `a2ensite` and `a2enmod`
- Apache2 service management permissions

### Network Requirements

- Open ports 80 and 443
- Domain DNS resolution to server IP
- Internet access for certificate validation

## Configuration Template Details

### Nginx Configuration Template
The generated Nginx configuration includes:
- IPv4 and IPv6 listeners on port 80
- Proper proxy headers for application integration
- Complete request forwarding to localhost:port
- Standard security headers via Certbot

### Apache2 Configuration Template
The generated Apache2 configuration includes:
- Port 80 VirtualHost configuration
- Proper proxy settings with ProxyPreserveHost
- Error and access logs per domain
- ProxyPass and ProxyPassReverse directives

## Maintenance and Operations

### Certificate Renewal

- Let's Encrypt certificates require renewal every 90 days
- Certbot automatically configures renewal via cron job
- Manual renewal: `sudo certbot renew`

### Configuration Management

For Nginx:
- Configurations stored in standard Nginx locations
- Easy manual editing if needed
- Symbolic links follow Nginx best practices

For Apache2:
- Configurations stored in standard Apache2 locations
- Easy manual editing if needed
- Uses a2ensite/a2dissite for enabling/disabling

### Monitoring and Logging

- Nginx logs available at `/var/log/nginx/`
- Apache2 logs available at `/var/log/apache2/`
- Certbot logs at `/var/log/letsencrypt/`
- Certbot provides automatic monitoring of certificate expiration

## Extensibility

### Possible Enhancements

- Support for multiple domains/SAN certificates
- Custom configuration templates for both web servers
- Integration with more web servers
- Advanced SSL security configurations
- Docker container support
- API endpoints for configuration management

### Current Limitations

- Ubuntu/Debian specific paths
- Requires systemd (not suitable for all systems)
- Single domain certificates only
- Hardcoded default email address

## Testing Strategy

### Integration Points

- Nginx/Apache2 configuration syntax validation
- Certbot certificate acquisition process
- System service management
- File system operations

### Validation Steps

- Web server configuration test before reload
- Certificate validity checks
- Service status verification
- Cleanup verification on failure

## Performance Considerations

### Execution Time

- Web server configuration creation: < 1 second
- Certbot certificate acquisition: 5-30 seconds (network dependent)
- Total execution time: 10-45 seconds typically

### Resource Usage

- Minimal memory footprint
- Low CPU usage during execution
- Standard system call overhead for subprocess operations

## Compatibility

### Supported Platforms

- Ubuntu 18.04+
- Debian 10+
- Other Debian-based distributions with appropriate package names

### Software Versions

- Python 3.6+
- Nginx 1.10+ or Apache2 2.4+
- Certbot 1.0+
- systemd (standard on supported platforms)
