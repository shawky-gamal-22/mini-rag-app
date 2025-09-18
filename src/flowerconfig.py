from dotenv import dotenv_values
config = dotenv_values(".env")


port = 5555
max_tasks= 10000
auto_refresh = True
#db = 'flower.db' # SQLlist database for persistent storage

basic_auth = [f'admin:{config["CELERY_FLOWER_PASSWORD"]}']
