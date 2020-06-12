from flask import Flask
from werkzeug.contrib.fixers import ProxyFix

from redash import settings
import datetime
import os


class Redash(Flask):
    """A custom Flask app for Redash"""

    def __init__(self, *args, **kwargs):
        kwargs.update(
            {
                "template_folder": settings.STATIC_ASSETS_PATH,
                "static_folder": settings.STATIC_ASSETS_PATH,
                "static_url_path": "/static",
            }
        )
        super(Redash, self).__init__(__name__, *args, **kwargs)
        # Make sure we get the right referral address even behind proxies like nginx.
        self.wsgi_app = ProxyFix(self.wsgi_app, settings.PROXIES_COUNT)
        # Configure Redash using our settings
        self.config.from_object("redash.settings")


def create_app():
    from redash import (
        authentication,
        extensions,
        handlers,
        limiter,
        mail,
        migrate,
        security,
        tasks,
    )
    from redash.handlers.webpack import configure_webpack
    from redash.metrics import request as request_metrics
    from redash.models import db, users
    from redash.utils import sentry
    from redash.version_check import reset_new_version_status

    sentry.init()
    app = Redash()

    # Check and update the cached version for use by the client
    app.before_first_request(reset_new_version_status)
    expire_time = os.getenv("expire_time", 86400)
    app.permanent_session_lifetime = datetime.timedelta(seconds=expire_time)
    security.init_app(app)
    request_metrics.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    authentication.init_app(app)
    limiter.init_app(app)
    handlers.init_app(app)
    configure_webpack(app)
    extensions.init_app(app)
    users.init_app(app)
    tasks.init_app(app)

    return app
