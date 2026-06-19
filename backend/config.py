from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key:          str = "changeme"
    admin_username:   str = "admin"
    admin_password:   str = "admin"
    chrony_conf_path: str = "/etc/chrony/chrony.conf"
    chronyc_path:     str = "/usr/bin/chronyc"
    reload_command:   str = "systemctl reload chrony"
    restart_command:  str = "systemctl restart chrony"

    class Config:
        env_prefix = "CHRONYWEBUI_"
        env_file = ".env"

settings = Settings()
