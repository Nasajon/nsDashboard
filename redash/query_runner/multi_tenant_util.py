from redash import redis_connection
import os
import requests
import json
from redash.worker import job, get_job_logger

logger = get_job_logger(__name__)


class MultiTenantUtil:
    REDIS_TENANT_KEY = "USER_TENANT_"
    TENANT_PLACEHOLDER = "C_TENANT"

    @staticmethod
    def get_current_tenant(user):
        # Recuperando o tenant do Redis
        tenant = redis_connection.get(MultiTenantUtil.REDIS_TENANT_KEY + str(user.id))
        if (tenant is None):
            tenant = 'null'

        return tenant

    @staticmethod
    def set_current_tenant(user, tenant):
        redis_connection.set(MultiTenantUtil.REDIS_TENANT_KEY + str(user.id), tenant)

    @staticmethod
    def request_access_token(email, password):
        realm = os.getenv("realm", "QA")
        client = os.getenv("client", "meucondominio_api")
        keycloak_url = 'https://auth.nasajon.com.br/auth/realms/' + realm + '/protocol/openid-connect/token'
        params = 'client_id=' + client + '&username=' + email + '&password=' + password + '&grant_type=password' + '&scope=offline_access'
        response = requests.post(
            keycloak_url, data=params, headers={'Content-Type': 'application/x-www-form-urlencoded'})

        response.raise_for_status()

        return json.loads(response.text)["access_token"]

    @staticmethod
    def request_tenant(access_token):
        user_url = os.getenv("user_url", "http://192.168.1.102:81/profile")
        response = requests.get(
            user_url, headers={'Authorization': access_token})

        response.raise_for_status()

        return json.loads(response.text)["organizacoes"][0]["id"]

    @staticmethod
    def prepare_query(query, user):
        if user != None:
            # tenant = MultiTenantUtil.get_current_tenant(user)

            # Substituindo o tenant na query
            query = query.replace(MultiTenantUtil.TENANT_PLACEHOLDER, str(user.tenant))

        # with open('/app/a.txt', 'a') as f:
        #     f.write(query + '\n')

        return query


# SÓ PARA TESTA ABAIXO:
# Adicionando um tenant para o usuário de ID 1 no redis (para teste):
# class U:
#     id = 1


# MultiTenantUtil.set_current_tenant(U(), '47')
