import logging

from flask import abort, flash, redirect, render_template, request, url_for
from flask import current_app as app
from flask_login import current_user, login_required, login_user, logout_user
from redash import __version__, limiter, models, settings
from redash.authentication import current_org, get_login_url, get_next_path
from redash.authentication.account import (
    BadSignature,
    SignatureExpired,
    send_password_reset_email,
    send_user_disabled_email,
    send_verify_email,
    validate_token,
)
from redash.handlers import routes
from redash.handlers.base import json_response, org_scoped_rule
from redash.version_check import get_latest_version
from sqlalchemy.orm.exc import NoResultFound
import datetime
import os
from redash.query_runner.multi_tenant_util import MultiTenantUtil
from sqlalchemy.exc import IntegrityError
logger = logging.getLogger(__name__)
import json

def get_google_auth_url(next_path):
    if settings.MULTI_ORG:
        google_auth_url = url_for(
            "google_oauth.authorize_org", next=next_path, org_slug=current_org.slug
        )
    else:
        google_auth_url = url_for("google_oauth.authorize", next=next_path)
    return google_auth_url


def render_token_login_page(template, org_slug, token, invite):
    try:
        user_id = validate_token(token)
        org = current_org._get_current_object()
        user = models.User.get_by_id_and_org(user_id, org)
    except NoResultFound:
        logger.exception(
            "Bad user id in token. Token= , User id= %s, Org=%s",
            user_id,
            token,
            org_slug,
        )
        return (
            render_template(
                "error.html",
                error_message="Invalid invite link. Please ask for a new one.",
            ),
            400,
        )
    except (SignatureExpired, BadSignature):
        logger.exception("Failed to verify invite token: %s, org=%s", token, org_slug)
        return (
            render_template(
                "error.html",
                error_message="Your invite link has expired. Please ask for a new one.",
            ),
            400,
        )

    if invite and user.details.get("is_invitation_pending") is False:
        return (
            render_template(
                "error.html",
                error_message=(
                    "This invitation has already been accepted. "
                    "Please try resetting your password instead."
                ),
            ),
            400,
        )

    status_code = 200
    if request.method == "POST":
        if "password" not in request.form:
            flash("Bad Request")
            status_code = 400
        elif not request.form["password"]:
            flash("Cannot use empty password.")
            status_code = 400
        elif len(request.form["password"]) < 6:
            flash("Password length is too short (<6).")
            status_code = 400
        else:
            if invite:
                user.is_invitation_pending = False
            user.hash_password(request.form["password"])
            models.db.session.add(user)
            login_user(user)
            models.db.session.commit()
            return redirect(url_for("redash.index", org_slug=org_slug))

    google_auth_url = get_google_auth_url(url_for("redash.index", org_slug=org_slug))

    return (
        render_template(
            template,
            show_google_openid=settings.GOOGLE_OAUTH_ENABLED,
            google_auth_url=google_auth_url,
            show_saml_login=current_org.get_setting("auth_saml_enabled"),
            show_remote_user_login=settings.REMOTE_USER_LOGIN_ENABLED,
            show_ldap_login=settings.LDAP_LOGIN_ENABLED,
            org_slug=org_slug,
            user=user,
        ),
        status_code,
    )


@routes.route(org_scoped_rule("/invite/<token>"), methods=["GET", "POST"])
def invite(token, org_slug=None):
    return render_token_login_page("invite.html", org_slug, token, True)


@routes.route(org_scoped_rule("/reset/<token>"), methods=["GET", "POST"])
def reset(token, org_slug=None):
    return render_token_login_page("reset.html", org_slug, token, False)


@routes.route(org_scoped_rule("/verify/<token>"), methods=["GET"])
def verify(token, org_slug=None):
    try:
        user_id = validate_token(token)
        org = current_org._get_current_object()
        user = models.User.get_by_id_and_org(user_id, org)
    except (BadSignature, NoResultFound):
        logger.exception(
            "Failed to verify email verification token: %s, org=%s", token, org_slug
        )
        return (
            render_template(
                "error.html",
                error_message="Your verification link is invalid. Please ask for a new one.",
            ),
            400,
        )

    user.is_email_verified = True
    models.db.session.add(user)
    models.db.session.commit()

    template_context = {"org_slug": org_slug} if settings.MULTI_ORG else {}
    next_url = url_for("redash.index", **template_context)

    return render_template("verify.html", next_url=next_url)


@routes.route(org_scoped_rule("/forgot"), methods=["GET", "POST"])
def forgot_password(org_slug=None):
    if not current_org.get_setting("auth_password_login_enabled"):
        abort(404)

    submitted = False
    if request.method == "POST" and request.form["email"]:
        submitted = True
        email = request.form["email"]
        try:
            org = current_org._get_current_object()
            user = models.User.get_by_email_and_org(email, org)
            if user.is_disabled:
                send_user_disabled_email(user)
            else:
                send_password_reset_email(user)
        except NoResultFound:
            logging.error("No user found for forgot password: %s", email)

    return render_template("forgot.html", submitted=submitted)


@routes.route(org_scoped_rule("/verification_email/"), methods=["POST"])
def verification_email(org_slug=None):
    if not current_user.is_email_verified:
        send_verify_email(current_user, current_org)

    return json_response(
        {
            "message": "Please check your email inbox in order to verify your email address."
        }
    )


@routes.route(org_scoped_rule("/login"), methods=["GET", "POST"])
@limiter.limit(settings.THROTTLE_LOGIN_PATTERN)
def login(org_slug=None):
    # We intentionally use == as otherwise it won't actually use the proxy. So weird :O
    # noinspection PyComparisonWithNone
    if current_org == None and not settings.MULTI_ORG:
        return redirect("/setup")
    elif current_org == None:
        return redirect("/")

    index_url = url_for("redash.index", org_slug=org_slug)
    unsafe_next_path = request.args.get("next", index_url)
    next_path = get_next_path(unsafe_next_path)
    if current_user.is_authenticated:
        return redirect(next_path)

    if request.method == "POST":
        try:
            org = current_org._get_current_object()
            user = models.User.get_by_email_and_org(request.form["email"], org)
            if (
                user
                and not user.is_disabled
                and user.verify_password(request.form["password"])
            ):
                # Código para acessar dados do cliente cadastrados no diretório e passar para o redash
                # access_token = MultiTenantUtil.request_access_token(request.form["email"], str(request.form["password"]))

                # tenant = MultiTenantUtil.request_tenant(access_token)
                # if user.tenant != int(tenant):
                #     user.tenant = tenant
                #     models.db.session.commit()

                # tenant_groups = models.TenantGroup.find_by_tenant(tenant)
                # group_ids = [tenant_group.group_id for tenant_group in tenant_groups]

                # # O grupo 1 é o grupo dos admins e o grupo 2 é o grupo default criado pelo redash
                # if 1 in user.group_ids:
                #     group_ids += [1]
                # if 2 in user.group_ids:
                #     group_ids += [2]

                # if user.group_ids != group_ids:
                #     user.group_ids = group_ids
                #     models.db.session.commit()
                licenciamento = models.Configuracao.find_by_campo_aplicacao(43, 0)
                modulos = json.loads(licenciamento.valor)["Modulos"]
                licenciamento_aprovado = False
                for modulo in modulos:
                    if modulo["Codigo"] == "nsDash":
                        licenciamento_aprovado = True
                        break
                
                if licenciamento_aprovado:
                    login_user(user)
                    return redirect(next_path)
                else:
                    flash("Sem permissão para acessar o Relatórios. Entre em contato com o suporte da Nasajon.")
            else:
                flash("Wrong email or password.")
        except NoResultFound:
            # Código para criar um usuário do diretório no redash e logar com ele
            # user = create_user(request)
            # if user != None:
            #     login_user(user)
            #     return redirect(next_path)
            flash("Wrong email or password.")
        except Exception as e:
            if "Unauthorized" in str(e):
                flash("Wrong email or password.")
            else:
                flash(str(e))

    google_auth_url = get_google_auth_url(next_path)

    return render_template(
        "login.html",
        org_slug=org_slug,
        next=next_path,
        email=request.form.get("email", ""),
        show_google_openid=settings.GOOGLE_OAUTH_ENABLED,
        google_auth_url=google_auth_url,
        show_password_login=current_org.get_setting("auth_password_login_enabled"),
        show_saml_login=current_org.get_setting("auth_saml_enabled"),
        show_remote_user_login=settings.REMOTE_USER_LOGIN_ENABLED,
        show_ldap_login=settings.LDAP_LOGIN_ENABLED,
    )


def create_user(request):
    try:
        access_token = MultiTenantUtil.request_access_token(request.form["email"], str(request.form["password"]))
        tenant = MultiTenantUtil.request_tenant(access_token)
        tenant_groups = models.TenantGroup.find_by_tenant(tenant)
        group_ids = [tenant_group.group_id for tenant_group in tenant_groups]
        user = models.User(
            org=current_org,
            name=request.form["email"],
            email=request.form["email"],
            is_invitation_pending=False,
            group_ids=group_ids,
        )

        user.hash_password(request.form["password"])
        user.tenant = tenant
        try:
            models.db.session.add(user)
            models.db.session.commit()
        except IntegrityError as e:
            if "email" in str(e):
                flash("Email already taken.")
            else:
                flash(str(e))

        return user
    except Exception as e:
        if "Unauthorized" in str(e):
            flash("Wrong email or password.")
        else:
            flash(str(e))


@routes.route(org_scoped_rule("/logout"))
def logout(org_slug=None):
    logout_user()
    return redirect(get_login_url(next=None))


def base_href():
    if settings.MULTI_ORG:
        base_href = url_for("redash.index", _external=True, org_slug=current_org.slug)
    else:
        base_href = url_for("redash.index", _external=True)

    return base_href


def date_time_format_config():
    date_format = current_org.get_setting("date_format")
    date_format_list = set(["DD/MM/YY", "MM/DD/YY", "YYYY-MM-DD", settings.DATE_FORMAT])
    time_format = current_org.get_setting("time_format")
    time_format_list = set(["HH:mm", "HH:mm:ss", "HH:mm:ss.SSS", settings.TIME_FORMAT])
    return {
        "dateFormat": date_format,
        "dateFormatList": list(date_format_list),
        "timeFormatList": list(time_format_list),
        "dateTimeFormat": "{0} {1}".format(date_format, time_format),
    }


def number_format_config():
    return {
        "integerFormat": current_org.get_setting("integer_format"),
        "floatFormat": current_org.get_setting("float_format"),
    }


def client_config():
    if not current_user.is_api_user() and current_user.is_authenticated:
        client_config = {
            "newVersionAvailable": bool(get_latest_version()),
            "version": __version__,
        }
    else:
        client_config = {}

    if (
        current_user.has_permission("admin")
        and current_org.get_setting("beacon_consent") is None
    ):
        client_config["showBeaconConsentMessage"] = True

    defaults = {
        "allowScriptsInUserInput": settings.ALLOW_SCRIPTS_IN_USER_INPUT,
        "showPermissionsControl": current_org.get_setting(
            "feature_show_permissions_control"
        ),
        "allowCustomJSVisualizations": settings.FEATURE_ALLOW_CUSTOM_JS_VISUALIZATIONS,
        "autoPublishNamedQueries": settings.FEATURE_AUTO_PUBLISH_NAMED_QUERIES,
        "extendedAlertOptions": settings.FEATURE_EXTENDED_ALERT_OPTIONS,
        "mailSettingsMissing": not settings.email_server_is_configured(),
        "dashboardRefreshIntervals": settings.DASHBOARD_REFRESH_INTERVALS,
        "queryRefreshIntervals": settings.QUERY_REFRESH_INTERVALS,
        "googleLoginEnabled": settings.GOOGLE_OAUTH_ENABLED,
        "pageSize": settings.PAGE_SIZE,
        "pageSizeOptions": settings.PAGE_SIZE_OPTIONS,
        "tableCellMaxJSONSize": settings.TABLE_CELL_MAX_JSON_SIZE,
    }

    client_config.update(defaults)
    client_config.update({"basePath": base_href()})
    client_config.update(date_time_format_config())
    client_config.update(number_format_config())

    return client_config


def messages():
    messages = []

    if not current_user.is_email_verified:
        messages.append("email-not-verified")

    if settings.ALLOW_PARAMETERS_IN_EMBEDS:
        messages.append("using-deprecated-embed-feature")

    return messages


@routes.route("/api/config", methods=["GET"])
def config(org_slug=None):
    return json_response(
        {"org_slug": current_org.slug, "client_config": client_config()}
    )


@routes.route(org_scoped_rule("/api/session"), methods=["GET"])
@login_required
def session(org_slug=None):
    if current_user.is_api_user():
        user = {"permissions": [], "apiKey": current_user.id}
    else:
        user = {
            "profile_image_url": current_user.profile_image_url,
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "groups": current_user.group_ids,
            "permissions": current_user.permissions,
        }

    return json_response(
        {
            "user": user,
            "messages": messages(),
            "org_slug": current_org.slug,
            "client_config": client_config(),
        }
    )
