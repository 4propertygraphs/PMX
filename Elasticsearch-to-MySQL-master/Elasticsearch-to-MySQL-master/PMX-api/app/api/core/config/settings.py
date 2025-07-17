class TestingConfig:
    TESTING = True
    PMX_DATABASE_URI = "mysql+pymysql://root@localhost:3306/pmx_report"
    API_KEY_DATABASE_URI = "mysql+pymysql://root@localhost:3306/pmx_api_auth"
    URL = "http://127.0.0.1:8000/"
