# -*- coding: utf-8 -*-


from celery import Celery


def make_celery(app):
    """create a new celery instance,
    use broker of app's config (broker can be: rabbitmq Redis MongoDB...),
    update other celery config,
    then create a task class in app context
    """
    celery = Celery(app.import_name,
                    backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery
