from celery import Celery  # type: ignore

app = Celery('scraper')
app.config_from_object('config.celery.config')

# 自動找到並註冊所有任務
app.autodiscover_tasks(['celery_scraper'])
