from rq import Connection
from sqlalchemy.orm import configure_mappers

from redash import rq_redis_connection
from redash.tasks import (
    Worker,
    rq_scheduler,
    schedule_periodic_jobs,
    periodic_job_definitions,
)

def scheduler():
    jobs = periodic_job_definitions()
    schedule_periodic_jobs(jobs)
    rq_scheduler.run()


def worker(queues=None):
    # Configure any SQLAlchemy mappers loaded until now so that the mapping configuration
    # will already be available to the forked work horses and they won't need
    # to spend valuable time re-doing that on every fork.
    configure_mappers()

    if not queues:
        queues = ["scheduled_queries", "queries", "periodic", "emails", "default", "schemas"]

    with Connection(rq_redis_connection):
        w = Worker(queues, log_job_description=False, job_monitoring_interval=5)
        w.work()

