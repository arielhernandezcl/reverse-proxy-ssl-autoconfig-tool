import argparse
import subprocess
import os
import sys

# --- Variables de Configuración ---
CERTBOT_EMAIL = "#"

# Rutas para Nginx
NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"

# Rutas y comandos para Apache2
APACHE_SITES_AVAILABLE = "/etc/apache2/sites-available"
APACHE_A2ENSITE = ["a2ensite"]

# --- Detección del Servidor Web ---

def detect_web_server():
    try:
        subprocess.run(["nginx", "-v"], check=True, capture_output=True)
        if os.path.isdir(NGINX_SITES_AVAILABLE):
            return "nginx"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    try:
        subprocess.run(["apache2ctl", "-v"], check=True, capture_output=True)
        if os.path.isdir(APACHE_SITES_AVAILABLE):
            return "apache2"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return None

# =================================================================
# --- Funciones para NGINX ---
# =================================================================

def generate_nginx_config(domain, port):
    config_content = f"""
server {{
    listen 80;
    listen [::]:80;
    server_name {domain};

    location / {{
        proxy_pass http://localhost:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    return config_content

def create_and_enable_nginx_proxy(domain, config_content):
    config_file_path = os.path.join(NGINX_SITES_AVAILABLE, f"{domain}.conf")
    link_path = os.path.join(NGINX_SITES_ENABLED, f"{domain}.conf")
    
    print(f". Creando archivo de configuración en: {config_file_path}")
    try:
        with open(config_file_path, "w") as f:
            f.write(config_content)

        if not os.path.exists(link_path):
            subprocess.run(["ln", "-s", config_file_path, link_path], check=True, capture_output=True)
            print(f". Enlace simbólico creado en: {link_path}")
        else:
            print(f"! El enlace simbólico ya existe, omitiendo la creación.")

        subprocess.run(["nginx", "-t"], check=True, capture_output=True)
        print(". Sintaxis de Nginx verificada correctamente.")

        subprocess.run(["systemctl", "reload", "nginx"], check=True, capture_output=True)
        print(". Nginx recargado. El proxy inverso HTTP está activo.")
        
        return True

    except subprocess.CalledProcessError as e:
        print(f"X Error durante la configuración de Nginx. Código: {e.returncode}")
        if os.path.exists(link_path):
             os.remove(link_path)
             print(f"Limpiando enlace simbólico: {link_path}")
             
        if e.stderr is not None:
            print(f"Detalles de Nginx: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"X Ocurrió un error inesperado en Nginx: {e}")
        return False

def run_certbot_nginx(domain, email):
    try:
        certbot_command = [
            "certbot", "run", 
            "--nginx", 
            "-d", domain, 
            "--non-interactive", 
            "--agree-tos", 
            "--email", email, 
            "--redirect", 
            "-v"
        ]
        
        subprocess.run(certbot_command, check=True, capture_output=True)
        print(f". Certificado SSL de Let's Encrypt obtenido e instalado para {domain}.")
        print(". Nginx ha sido actualizado a HTTPS/SSL.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"X Error al ejecutar Certbot (Nginx). Código de salida: {e.returncode}")
        if e.stderr is not None:
             error_details = e.stderr.decode()
             print(f"Detalles del error: {error_details}")
        else:
             print("No hay detalles de error explícitos. Consulta el log de Certbot para más información.")
        return False
    except FileNotFoundError:
        print("X Certbot no se encontró. Asegúrate de que esté instalado.")
        return False

# =================================================================
# --- Funciones para APACHE2 ---
# =================================================================

def generate_apache_config(domain, port):
    config_content = f"""
<VirtualHost *:80>
    ServerName {domain}
    
    <Proxy "*">
        Order deny,allow
        Allow from all
    </Proxy>
    
    ProxyPreserveHost On
    ProxyRequests Off
    
    ProxyPass / http://localhost:{port}/
    ProxyPassReverse / http://localhost:{port}/

    ErrorLog ${{APACHE_LOG_DIR}}/error_{domain}.log
    CustomLog ${{APACHE_LOG_DIR}}/access_{domain}.log combined
</VirtualHost>
"""
    return config_content

def enable_apache_proxy_modules():
    print("- Verificando y habilitando módulos de proxy de Apache2...")
    
    for mod in ["proxy", "proxy_http"]:
        try:
            subprocess.run(["a2enmod", mod], check=True, capture_output=True)
            print(f". Módulo {mod} habilitado.")
        except subprocess.CalledProcessError as e:
            if f"Module {mod} already enabled" not in e.stderr.decode():
                raise 
        except FileNotFoundError:
            print("X El comando 'a2enmod' no se encontró.")
            return False
            
    return True
    
def create_and_enable_apache_proxy(domain, config_content):
    
    if not enable_apache_proxy_modules():
        return False
        
    config_file_name = f"{domain}.conf"
    config_file_path = os.path.join(APACHE_SITES_AVAILABLE, config_file_name)
    
    print(f". Creando archivo de configuración en: {config_file_path}")
    try:
        with open(config_file_path, "w") as f:
            f.write(config_content)

        print(f". Habilitando sitio con a2ensite {config_file_name}...")
        subprocess.run(["a2ensite", config_file_name], check=True, capture_output=True)
        print(f". Sitio habilitado.")

        subprocess.run(["apache2ctl", "configtest"], check=True, capture_output=True)
        print(". Sintaxis de Apache2 verificada correctamente.")

        subprocess.run(["systemctl", "reload", "apache2"], check=True, capture_output=True)
        print(". Apache2 recargado. El proxy inverso HTTP está activo.")
        
        return True

    except subprocess.CalledProcessError as e:
        print(f"X Error durante la configuración de Apache2. Código: {e.returncode}")
        
        try:
             subprocess.run(["a2dissite", config_file_name], capture_output=True)
             print(f"Limpiando sitio deshabilitado: {config_file_name}")
        except:
             pass
             
        if e.stderr is not None:
            print(f"Detalles de Apache2: {e.stderr.decode()}")
        return False
    except Exception as e:
        print(f"X Ocurrió un error inesperado en Apache2: {e}")
        return False

def run_certbot_apache(domain, email):
    try:
        certbot_command = [
            "certbot", "run", 
            "--apache", 
            "-d", domain, 
            "--non-interactive", 
            "--agree-tos", 
            "--email", email, 
            "--redirect", 
            "-v"
        ]
        
        subprocess.run(certbot_command, check=True, capture_output=True)
        print(f". Certificado SSL de Let's Encrypt obtenido e instalado para {domain}.")
        print(". Apache2 ha sido actualizado a HTTPS/SSL.")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"X Error al ejecutar Certbot (Apache). Código de salida: {e.returncode}")
        if e.stderr is not None:
             error_details = e.stderr.decode()
             print(f"Detalles del error: {error_details}")
        else:
             print("No hay detalles de error explícitos. Consulta el log de Certbot para más información.")
        return False
    except FileNotFoundError:
        print("X Certbot no se encontró. Asegúrate de que esté instalado.")
        return False

# =================================================================
# --- Función Principal ---
# =================================================================

def main():
    parser = argparse.ArgumentParser(description="Automatiza la configuración de Reverse Proxy (Nginx/Apache2) y SSL con Certbot.")
    parser.add_argument("domain", help="El nombre de dominio (ej: midominio.com).")
    parser.add_argument("port", type=int, help="El puerto local de la aplicación (ej: 5000).")
    parser.add_argument("-e", "--email", default=CERTBOT_EMAIL, help="Dirección de correo electrónico para Certbot.")
    args = parser.parse_args()

    if args.email == CERTBOT_EMAIL and CERTBOT_EMAIL == "info@sonix.cl":
         print("! Usando el email por defecto 'info@sonix.cl'. Asegúrate de que es correcto o usa la opción -e.")
    
    domain = args.domain
    port = args.port
    
    web_server = detect_web_server()

    if web_server is None:
        print("X No se pudo detectar una instalación activa de Nginx ni Apache2.")
        print("Asegúrate de que uno de ellos esté instalado y de que las rutas de configuración existan.")
        sys.exit(1)
    
    print(f"🎉 Servidor web detectado: **{web_server.upper()}**")
    print(f"- Configurando Proxy Reverso para: https://{domain} -> http://localhost:{port}...")
    
    if web_server == "nginx":
        config_content = generate_nginx_config(domain, port)
        proxy_success = create_and_enable_nginx_proxy(domain, config_content)
        run_certbot_func = run_certbot_nginx
    else: # apache2
        config_content = generate_apache_config(domain, port)
        proxy_success = create_and_enable_apache_proxy(domain, config_content)
        run_certbot_func = run_certbot_apache

    if not proxy_success:
        print("X Proceso detenido debido a fallos en la configuración inicial del servidor web.")
        return

    print(f"\n- Iniciando Certbot para obtención e instalación del certificado SSL...")
    if not run_certbot_func(domain, args.email): 
        print(f"X Fallo: La configuración de {web_server.upper()} está activa, pero solo por HTTP (puerto 80).")
        
    print("\n✅ Proceso completado.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("X Este script debe ejecutarse con 'sudo'.")
        print("Sintaxis: sudo python3 main.py [dominio] [puerto] [-e email]")
    else:
        main()