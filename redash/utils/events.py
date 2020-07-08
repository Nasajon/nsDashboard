from sys import exit

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from redash import models

def record(
    action,
    object_type,
    data
):
    """
    Inserir eventos no Redash
    """

    try:
        event = models.Event(
            org_id=1,
            user_id=1,
            action=action,
            object_type=object_type,
            additional_properties=data,
        )

        models.db.session.add(event)
        models.db.session.commit()
    except Exception as e:
        print("Failed inserting event: %s" % e)
        exit(1)
