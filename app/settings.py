import os
class Settings:
    def __init__(self):
        self.host = os.getenv("DB_HOST")
        self.user = os.getenv("DB_USER")
        self.port = int(os.getenv("DB_PORT"))
        self.password = os.getenv("DB_PASS")
        self.name = os.getenv("DB_NAME")
        self.skey = os.getenv("SECRET_KEY")
        self.alg = os.getenv("ALGORITHM")
        self.etime = int(os.getenv("EXPIRATION_TIME"))
        self.github_token = os.getenv("GITHUB_TOKEN")