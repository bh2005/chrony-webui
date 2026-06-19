from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str = "changeme"
    chrony_conf_path: str = "/etc/chrony/chrony.conf"
    chronyc_path: str = "/usr/bin/chronyc"
    reload_command: str = "systemctl reload chrony"

    class Config:
        env_prefix = "CHRONYWEBUI_"
        env_file = ".env"

settings = Settings()
