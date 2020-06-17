from sys import exit

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from redash import models


def build_groups(org, groups, is_admin):
    if isinstance(groups, str):
        groups = groups.split(",")
        groups.remove("")  # in case it was empty string
        groups = [int(g) for g in groups]

    if groups is None:
        groups = [org.default_group.id]

    if is_admin:
        groups += [org.admin_group.id]

    return groups


def create(
    email,
    name,
    tenant,
    password,
    is_admin=False,
    groups=None,
):
    """
    Create user EMAIL with display name NAME.
    """
    print("Creating user (%s, %s)..." % (email, name))
    print("Admin: %r" % is_admin)

    org = models.Organization.get_by_slug("default")
    groups = build_groups(org, groups, is_admin)

    user = models.User(org=org, email=email, name=name, group_ids=groups, tenant=tenant)

    try:
        models.db.session.add(user)
        models.db.session.commit()
    except Exception as e:
        print("Failed creating user: %s" % e)
        exit(1)
