# from celery.schedules import crontab  # type:ignore
from datetime import timedelta
from config.redis import constants as RedisConfig


# broker: 消息中間件，使用redis 使用1庫
broker_url = f'redis://{RedisConfig.HOST}:{
    RedisConfig.PORT}/{RedisConfig.DB_CELERY}'

# backend: 結果存儲 使用redis 使用2庫
result_backend = f'redis://{RedisConfig.HOST}:{
    RedisConfig.PORT}/{RedisConfig.DB_CELERY}'

accept_content = ['application/json']
timezone = 'Asia/Taipei'
enable_utc = True

# 註冊任務
imports = ('celery_scraper.scraper_tasks',)

beat_schedule = {
    'first-scraper-every-minute': {
        'task': 'celery_scraper.scraper_tasks.scrape_all',
        # 'schedule': crontab(minute='5', hour='*'),
        'schedule': timedelta(seconds=10)
    },
}
