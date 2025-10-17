# Usage Examples: Reverse Proxy SSL Auto-Configuration Tool

## Basic Usage Examples

### Example 1: Basic Setup

```bash
sudo python3 main.py example.com 3000
```

- Sets up Nginx reverse proxy for `example.com` pointing to `localhost:3000`
- Uses default email `email@email` for Let's Encrypt registration
- Configures HTTP to HTTPS redirect automatically

### Example 2: Custom Email

```bash
sudo python3 main.py myapp.com 8080 -e admin@myapp.com
```

- Sets up proxy for `myapp.com` pointing to `localhost:8080`
- Uses custom email `admin@myapp.com` for Let's Encrypt registration

## Common Scenarios

### Scenario 1: Deploying a Node.js Application

```bash
# Your Node.js app is running on port 3000
sudo python3 main.py api.myapp.com 3000 -e admin@myapp.com
```

### Scenario 2: Setting up a Python Flask Application

```bash
# Your Flask app is running on port 5000
sudo python3 main.py flask-app.com 5000
```

### Scenario 3: Frontend Application Behind Proxy

```bash
# Your React/Vue app is running on port 3001
sudo python3 main.py frontend.mycompany.com 3001 -e it@mycompany.com
```

## Step-by-Step Walkthrough

### Preparing Your Application

1. **Ensure your application is running**:

   ```bash
   # Example: Flask app running in background
   python3 app.py &
   # Verify it's running on your chosen port
   curl http://localhost:5000
   ```

2. **Verify domain points to server**:

   ```bash
   nslookup yourdomain.com
   # Should return your server's IP address
   ```

3. **Ensure required ports are open**:
   ```bash
   # Check if ports 80 and 443 are accessible
   sudo ufw status  # If using ufw firewall
   # Ports 80 and 443 should be allowed
   ```

### Running the Script

4. **Execute the configuration script**:

   ```bash
   sudo python3 main.py yourdomain.com 5000 -e your-email@example.com
   ```

5. **Monitor the output**:

   ```
   - Configurando Proxy Reverso para: https://yourdomain.com -> http://localhost:5000...
   . Creando archivo de configuración en: /etc/nginx/sites-available/yourdomain.com.conf
   . Enlace simbólico creado en: /etc/nginx/sites-enabled/yourdomain.com.conf
   . Sintaxis de Nginx verificada correctamente.
   . Nginx recargado. El proxy inverso HTTP está activo.

   - Iniciando Certbot para obtención e instalación del certificado SSL...
   . Certificado SSL de Let's Encrypt obtenido e instalado para yourdomain.com.
   . El archivo de configuración de Nginx ha sido actualizado a HTTPS/SSL.

   - Proceso completado.
   ```

### Verification Steps

6. **Test HTTP to HTTPS redirect**:

   ```bash
   curl -I http://yourdomain.com
   # Should return a 301 redirect to https
   ```

7. **Test HTTPS connection**:

   ```bash
   curl -I https://yourdomain.com
   # Should return 200 OK
   ```

8. **Check certificate validity**:
   ```bash
   openssl s_client -connect yourdomain.com:443 -servername yourdomain.com
   ```

## Multiple Applications Setup

### Setting up multiple domains/subdomains

For multiple applications on the same server:

1. **Application 1**:

   ```bash
   sudo python3 main.py api.myapp.com 5000 -e admin@myapp.com
   ```

2. **Application 2**:

   ```bash
   sudo python3 main.py dashboard.myapp.com 3000 -e admin@myapp.com
   ```

3. **Application 3**:
   ```bash
   sudo python3 main.py docs.myapp.com 4000 -e admin@myapp.com
   ```

## Troubleshooting Common Issues

### Issue 1: Ports 80/443 Not Accessible

```bash
# Check firewall settings
sudo ufw status
sudo ufw allow 80
sudo ufw allow 443
sudo ufw reload
```

### Issue 2: Domain Not Resolving

```bash
# Verify DNS
nslookup yourdomain.com
dig yourdomain.com

# Check if domain points to correct IP
ping yourdomain.com
```

### Issue 3: Nginx Configuration Error

```bash
# Test configuration
sudo nginx -t

# Check specific configuration file
sudo cat /etc/nginx/sites-available/yourdomain.com.conf

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Issue 4: Certificate Acquisition Failure

```bash
# Check Certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Test Certbot manually
sudo certbot --nginx -d yourdomain.com --dry-run
```

## Advanced Configuration Examples

### Example: Working with Docker Applications

If your application runs in a Docker container on port 3000:

```bash
sudo python3 main.py docker-app.com 3000 -e admin@docker-app.com
```

### Example: Subdomain Setup

For a specific service on a subdomain:

```bash
sudo python3 main.py mail.service.com 8000 -e admin@service.com
```

### Example: Port-Specific Applications

For applications that require specific ports:

```bash
# API on port 4000
sudo python3 main.py api.company.com 4000 -e admin@company.com

# Admin panel on port 8080
sudo python3 main.py admin.company.com 8080 -e admin@company.com
```

## Post-Setup Verification Checklist

- [ ] Domain resolves to server IP
- [ ] HTTP requests redirect to HTTPS
- [ ] SSL certificate is valid and trusted
- [ ] Application responds correctly through proxy
- [ ] Nginx logs show no errors
- [ ] Certbot auto-renewal is configured

## Maintenance Examples

### Checking Certificate Status

```bash
sudo certbot certificates
```

### Testing Renewal

```bash
sudo certbot renew --dry-run
```

### Adding Auto-Renewal Cron Job

```bash
sudo crontab -e
# Add this line:
0 12 * * * /usr/bin/certbot renew --quiet
```

## Common Application-Specific Examples

### Express.js Application

```bash
# App running on port 3000
sudo python3 main.py express-api.com 3000 -e admin@express-api.com
```

### Django Application

```bash
# Django running on port 8000
sudo python3 main.py django-site.com 8000 -e admin@django-site.com
```

### React Development Server

```bash
# React dev server on port 3000
sudo python3 main.py react-dev.com 3000 -e dev@react-dev.com
```

### Python Flask Application

```bash
# Flask app on port 5000
sudo python3 main.py flask-api.com 5000 -e admin@flask-api.com
```

## Integration with Application Deployment

### Example deployment script

```bash
#!/bin/bash
# deploy.sh

# Start your application
echo "Starting application..."
pm2 start app.js --name myapp

# Wait for application to be ready
sleep 5

# Configure proxy and SSL
echo "Configuring Nginx proxy and SSL..."
sudo python3 main.py "$1" "$2" -e "$3"

echo "Deployment complete!"
echo "Visit: https://$1"
```

Usage:

```bash
chmod +x deploy.sh
./deploy.sh myapp.com 3000 admin@myapp.com
```

This document provides comprehensive examples for using the reverse proxy SSL auto-configuration tool in various scenarios, helping users understand how to effectively deploy and configure their applications with HTTPS.
