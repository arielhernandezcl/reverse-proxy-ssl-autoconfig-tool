# Technical Documentation: Reverse Proxy SSL Auto-Configuration Tool

## Overview

This Python script automates the setup of an Nginx reverse proxy with SSL certificate acquisition from Let's Encrypt. It streamlines the process of making local applications accessible via HTTPS by generating Nginx configurations and managing SSL certificates automatically.

## Code Structure

### File Organization

- `main.py`: Main executable script containing all functionality
- `README.md`: Project documentation (generated)

### Module Dependencies

- `argparse`: For command-line argument parsing
- `subprocess`: For executing system commands (nginx, certbot, systemctl)
- `os`: For file system operations and permission checking

## Core Components

### 1. Configuration Constants

```python
CERTBOT_EMAIL = "email@email"  # Default email for Let's Encrypt registration
NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"  # Nginx configuration directory
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"     # Nginx enabled sites directory
```

### 2. Nginx Configuration Functions

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

#### `create_and_enable_proxy(domain, config_content)`

- **Purpose**: Creates configuration file and enables it in Nginx
- **Parameters**:
  - `domain` (str): Domain name for the proxy
  - `config_content` (str): Nginx configuration content
- **Process**:
  1. Writes configuration to `/etc/nginx/sites-available/{domain}.conf`
  2. Creates symbolic link in `/etc/nginx/sites-enabled/`
  3. Validates Nginx configuration syntax
  4. Reloads Nginx service
- **Error Handling**: Removes symbolic link on failure and provides detailed error messages

### 3. SSL Management Function

#### `run_certbot(domain, email)`

- **Purpose**: Acquires and installs Let's Encrypt SSL certificate
- **Parameters**:
  - `domain` (str): Domain name for certificate
  - `email` (str): Email for Let's Encrypt registration
- **Process**:
  1. Executes Certbot with Nginx plugin
  2. Configures automatic HTTP to HTTPS redirect
  3. Updates Nginx configuration for SSL
- **Error Handling**: Provides specific troubleshooting information based on error types

### 4. Main Execution Flow

#### `main()`

- **Purpose**: Orchestrates the complete proxy and SSL setup process
- **Process**:
  1. Parses command-line arguments
  2. Generates initial HTTP configuration
  3. Sets up reverse proxy with Nginx
  4. Acquires SSL certificate via Certbot
  5. Configures HTTPS redirection

## Execution Flow

```
1. Command-line arguments validation
2. ┌─ HTTP Configuration Creation
3. │  ├── Generate Nginx config
4. │  ├── Save to sites-available
5. │  ├── Create symbolic link
6. │  ├── Validate syntax
7. │  └── Reload Nginx
8. │
9. └─ SSL Certificate Setup
10.    ├── Run Certbot
11.    ├── Configure HTTPS
12.    └── Update Nginx for SSL
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

### Nginx-Specific Error Handling

- Validates configuration before reload
- Restores previous state on configuration errors
- Provides Nginx-specific troubleshooting information

## Security Considerations

### Privilege Management

- Requires root privileges (validated at startup)
- Uses symbolic links for configuration management
- Follows Nginx file permission best practices

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
- Nginx web server
- Certbot client with Nginx plugin
- systemd (for systemctl commands)

### File System Access

- Write access to `/etc/nginx/sites-available/`
- Write access to `/etc/nginx/sites-enabled/`
- Nginx service management permissions

### Network Requirements

- Open ports 80 and 443
- Domain DNS resolution to server IP
- Internet access for certificate validation

## Configuration Template Details

The generated Nginx configuration includes:

- IPv4 and IPv6 listeners on port 80
- Proper proxy headers for application integration
- Complete request forwarding to localhost:port
- Standard security headers via Certbot

## Maintenance and Operations

### Certificate Renewal

- Let's Encrypt certificates require renewal every 90 days
- Certbot automatically configures renewal via cron job
- Manual renewal: `sudo certbot renew`

### Configuration Management

- Configurations stored in standard Nginx locations
- Easy manual editing if needed
- Symbolic links follow Nginx best practices

### Monitoring and Logging

- Nginx logs available at `/var/log/nginx/`
- Certbot logs at `/var/log/letsencrypt/`
- Certbot provides automatic monitoring of certificate expiration

## Extensibility

### Possible Enhancements

- Support for multiple domains/SAN certificates
- Custom Nginx configuration templates
- Integration with different web servers
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

- Nginx configuration syntax validation
- Certbot certificate acquisition process
- System service management
- File system operations

### Validation Steps

- Nginx configuration test before reload
- Certificate validity checks
- Service status verification
- Cleanup verification on failure

## Performance Considerations

### Execution Time

- Nginx configuration creation: < 1 second
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
- Nginx 1.10+
- Certbot 1.0+
- systemd (standard on supported platforms)
