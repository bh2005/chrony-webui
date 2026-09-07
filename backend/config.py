from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key:          str = "changeme"
    admin_username:   str = "admin"
    admin_password:   str = "admin"
    chrony_conf_path: str = "/etc/chrony/chrony.conf"
    chronyc_path:     str = "/usr/bin/chronyc"
    reload_command:   str = "systemctl reload chrony"
    restart_command:  str = "systemctl restart chrony"

    # ACME (interne step-CA)
    acme_sh_path:               str = "/etc/acme/acme.sh"
    acme_ca_url:                str = "https://dekdli047.corp.k-plus-s.net/acme/acme/directory"
    acme_cert_home:             str = "/etc/acme/certs"
    acme_webroot:               str = "/var/www/chrony-webui"
    acme_email:                 str = "monitoring@k-plus-s.com"
    cert_install_dir:           str = "/etc/ssl/chrony-webui"
    cert_deploy_reload_command: str = "systemctl reload nginx"

    class Config:
        env_prefix = "CHRONYWEBUI_"
        env_file = ".env"

settings = Settings()
