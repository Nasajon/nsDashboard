from redash import redis_connection


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
    def prepare_query(query, user):
        if user != None:
            tenant = MultiTenantUtil.get_current_tenant(user)

            # Substituindo o tenant na query
            query = query.replace(MultiTenantUtil.TENANT_PLACEHOLDER, tenant)

        # with open('/app/a.txt', 'a') as f:
        #     f.write(query + '\n')

        return query


# SÓ PARA TESTA ABAIXO:
# Adicionando um tenant para o usuário de ID 1 no redis (para teste):
class U:
    id = 1


MultiTenantUtil.set_current_tenant(U(), '47')
