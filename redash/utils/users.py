from sys import exit

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

from redash import models
from redash.utils.criptografia_senha import CriptografiaSenha

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

def create_user_erp():
    
    usuarios = models.Usuario.usuarios_acesso_nsdash()
    org = models.Organization.get_by_slug("default")

    for usuario in usuarios:    
        try:
            user = models.User.get_by_email_or_name_and_org(usuario.login, org)
            user.hash_password(CriptografiaSenha.descodificar(usuario.senha))
            if usuario.email is not None and usuario.email != '':
                user.email = usuario.email
            models.db.session.commit()
        except NoResultFound:
            user = models.User(
                org=org,
                name=usuario.login,
                email=usuario.email if usuario.email is not None and usuario.email != '' else (usuario.login + "@nsdash.com"),
                group_ids=[org.default_group.id]
            )
            user.hash_password(CriptografiaSenha.descodificar(usuario.senha))
            try:
                models.db.session.add(user)
                models.db.session.commit()
            except Exception as e:
                print(str(e))

    usuarios = models.Usuario.usuarios_sem_acesso_nsdash()

    for usuario in usuarios:    
        try:
            user = models.User.get_by_email_or_name_and_org(usuario.login, org)
            user.disable()
            models.db.session.commit()
        except NoResultFound:
            pass
