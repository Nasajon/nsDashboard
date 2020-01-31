from redash.query_runner.pg import PostgreSQL
from redash.query_runner import register
from redash.query_runner.multi_tenant_util import MultiTenantUtil

import logging

logger = logging.getLogger(__name__)


class PostgreSQLMultiTenant(PostgreSQL):

    @classmethod
    def type(cls):
        return "pg_multi_tenant"

    @classmethod
    def name(cls):
        return "PostgreSQLMultiTenant"

    @classmethod
    def enabled(cls):
        return True

    def run_query(self, query, user):

        # Tratando a query quanto a substituição do tenant
        query = MultiTenantUtil.prepare_query(query, user)

        # Executando a query através da superclasse
        return super(PostgreSQLMultiTenant, self).run_query(query, user)


register(PostgreSQLMultiTenant)
