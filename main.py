import argparse
import subprocess
import os


CERTBOT_EMAIL = "" 

NGINX_SITES_AVAILABLE = "/etc/nginx/sites-available"
NGINX_SITES_ENABLED = "/etc/nginx/sites-enabled"

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

def create_and_enable_proxy(domain, config_content):
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
        print(f"X Ocurrió un error inesperado: {e}")
        return False

def run_certbot(domain, email):
    
    subcommand = "run"
    action = "obtención e instalación"

    print(f"\n- Iniciando Certbot para {action} del certificado SSL...")
    
    try:
        certbot_command = [
            "certbot", subcommand, 
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
        print(". El archivo de configuración de Nginx ha sido actualizado a HTTPS/SSL.")
            
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"X Error al ejecutar Certbot. Código de salida: {e.returncode}")
        print("Asegúrate de que los puertos 80/443 están abiertos y el DNS apunta a este servidor.")
        
        if e.stderr is not None:
            error_details = e.stderr.decode()
            print(f"Detalles del error: {error_details}")
        else:
            print("No hay detalles de error explícitos. Consulta el log de Certbot para más información.")
            
        return False
    except FileNotFoundError:
        print("X Certbot no se encontró. Asegúrate de que Certbot esté instalado (`sudo apt install certbot python3-certbot-nginx`).")
        return False

def main():
    parser = argparse.ArgumentParser(description="Automatiza la configuración de Nginx Reverse Proxy y SSL con Certbot.")
    parser.add_argument("domain", help="El nombre de dominio (ej: midominio.com).")
    parser.add_argument("port", type=int, help="El puerto local de la aplicación (ej: 5000).")
    parser.add_argument("-e", "--email", default=CERTBOT_EMAIL, help="Dirección de correo electrónico para Certbot.")
    args = parser.parse_args()

    if args.email == "info@sonix.cl" and CERTBOT_EMAIL == "info@sonix.cl":
         print("! Usando el email por defecto. Asegúrate de que info@sonix.cl es correcto o usa la opción -e.")
    
    domain = args.domain
    port = args.port

    print(f"- Configurando Proxy Reverso para: https://{domain} -> http://localhost:{port}...")

    config_content = generate_nginx_config(domain, port)
    
    if not create_and_enable_proxy(domain, config_content):
        print("X Proceso detenido debido a fallos en la configuración inicial de Nginx.")
        return

    if not run_certbot(domain, args.email): 
         print("X Fallo: La configuración de Nginx está activa, pero solo por HTTP.")
        
    print("\n- Proceso completado.")

if __name__ == "__main__":
    if os.geteuid() != 0:
        print("X Este script debe ejecutarse con 'sudo'.")
        print("Sintaxis: sudo python3 main.py [dominio] [puerto]")
    else:
        main()