import logging
import time
import copy
import unicodedata
from flask import make_response, request
from flask_login import current_user
from flask_restful import abort
from werkzeug.urls import url_quote
from redash import models, settings
from redash.handlers.base import BaseResource, get_object_or_404, record_event
from redash.permissions import (
    has_access,
    not_view_only,
    require_access,
    require_permission,
    require_any_of_permission,
    view_only,
)
from redash.tasks import Job
from redash.tasks.queries import enqueue_query
from redash.utils import (
    collect_parameters_from_request,
    gen_query_hash,
    json_dumps,
    utcnow,
    to_filename,
)
from redash.models.parameterized_query import (
    ParameterizedQuery,
    InvalidParameterError,
    QueryDetachedFromDataSourceError,
    dropdown_values,
)
from redash.serializers import (
    serialize_query_result,
    serialize_query_result_to_dsv,
    serialize_query_result_to_xlsx,
    serialize_job,
)


def get_download_filename(query_result, query, filetype):
    retrieved_at = query_result.retrieved_at.strftime("%Y_%m_%d")
    if query:
        filename = to_filename(query.name) if query.name != "" else str(query.id)
    else:
        filename = str(query_result.id)
    return "{}_{}.{}".format(filename, retrieved_at, filetype)


def content_disposition_filenames(attachment_filename):
    if not isinstance(attachment_filename, str):
        attachment_filename = attachment_filename.decode("utf-8")

    try:
        attachment_filename = attachment_filename.encode("ascii")
    except UnicodeEncodeError:
        filenames = {
            "filename": unicodedata.normalize("NFKD", attachment_filename).encode(
                "ascii", "ignore"
            ),
            "filename*": "UTF-8''%s" % url_quote(attachment_filename, safe=b""),
        }
    else:
        filenames = {"filename": attachment_filename}

    return filenames


ONE_YEAR = 60 * 60 * 24 * 365.25


class QueryResultTenantResource(BaseResource):
    @staticmethod
    def add_cors_headers(headers):
        if "Origin" in request.headers:
            origin = request.headers["Origin"]

            if set(["*", origin]) & settings.ACCESS_CONTROL_ALLOW_ORIGIN:
                headers["Access-Control-Allow-Origin"] = origin
                headers["Access-Control-Allow-Credentials"] = str(
                    settings.ACCESS_CONTROL_ALLOW_CREDENTIALS
                ).lower()

    @require_any_of_permission(("view_query", "execute_query"))
    def options(self, query_id=None, tenant=None, query_result_id=None, filetype="json"):
        headers = {}
        self.add_cors_headers(headers)

        if settings.ACCESS_CONTROL_REQUEST_METHOD:
            headers[
                "Access-Control-Request-Method"
            ] = settings.ACCESS_CONTROL_REQUEST_METHOD

        if settings.ACCESS_CONTROL_ALLOW_HEADERS:
            headers[
                "Access-Control-Allow-Headers"
            ] = settings.ACCESS_CONTROL_ALLOW_HEADERS

        return make_response("", 200, headers)

    @require_any_of_permission(("view_query", "execute_query"))
    def get(self, query_id=None, tenant=None, query_result_id=None, filetype="json"):
        """
        Retrieve query results.

        :param number query_id: The ID of the query whose results should be fetched
        :param number query_result_id: the ID of the query result to fetch
        :param string filetype: Format to return. One of 'json', 'xlsx', or 'csv'. Defaults to 'json'.

        :<json number id: Query result ID
        :<json string query: Query that produced this result
        :<json string query_hash: Hash code for query text
        :<json object data: Query output
        :<json number data_source_id: ID of data source that produced this result
        :<json number runtime: Length of execution time in seconds
        :<json string retrieved_at: Query retrieval date/time, in ISO format
        """
        # TODO:
        # This method handles two cases: retrieving result by id & retrieving result by query id.
        # They need to be split, as they have different logic (for example, retrieving by query id
        # should check for query parameters and shouldn't cache the result).
        should_cache = query_result_id is not None

        parameter_values = collect_parameters_from_request(request.args)

        query = get_object_or_404(
            models.Query.get_by_id_and_org, query_id, self.current_org
        )

        query_result = models.QueryResult.get_by_query_hash_and_tenant(query.query_hash, tenant)
        if query_result is None or (query.schedule is not None and models.should_schedule_next(
            query_result.retrieved_at,
            utcnow(),
            query.schedule["interval"],
            query.schedule["time"],
            query.schedule["day_of_week"],
            query.schedule_failures,
        )):
            started_at = time.time()
            user_copy = copy.deepcopy(self.current_user)
            user_copy.tenant = tenant
            data, _ = query_result.data_source.query_runner.run_query(query_result.query_text, user_copy)
            run_time = time.time() - started_at
            query_result = models.QueryResult.store_result(self.current_org.id, query_result.data_source, query_result.query_hash, query_result.query_text, data, run_time, utcnow(), tenant)
            models.db.session.commit()

        require_access(query_result.data_source, self.current_user, view_only)

        if isinstance(self.current_user, models.ApiUser):
            event = {
                "user_id": None,
                "org_id": self.current_org.id,
                "action": "api_get",
                "api_key": self.current_user.name,
                "file_type": filetype,
                "user_agent": request.user_agent.string,
                "ip": request.remote_addr,
            }

            if query_id:
                event["object_type"] = "query"
                event["object_id"] = query_id
            else:
                event["object_type"] = "query_result"
                event["object_id"] = query_result_id

            self.record_event(event)

        response_builders = {
            'json': self.make_json_response,
            'xlsx': self.make_excel_response,
            'csv': self.make_csv_response,
            'tsv': self.make_tsv_response
        }
        response = response_builders[filetype](query_result)

        if len(settings.ACCESS_CONTROL_ALLOW_ORIGIN) > 0:
            self.add_cors_headers(response.headers)

        if should_cache:
            response.headers.add_header(
                "Cache-Control", "private,max-age=%d" % ONE_YEAR
            )

        filename = get_download_filename(query_result, query, filetype)

        filenames = content_disposition_filenames(filename)
        response.headers.add("Content-Disposition", "attachment", **filenames)

        return response

    @staticmethod
    def make_json_response(query_result):
        data = json_dumps({"query_result": query_result.to_dict()})
        headers = {"Content-Type": "application/json"}
        return make_response(data, 200, headers)

    @staticmethod
    def make_csv_response(query_result):
        headers = {"Content-Type": "text/csv; charset=UTF-8"}
        return make_response(serialize_query_result_to_dsv(query_result, ","), 200, headers)

    @staticmethod
    def make_tsv_response(query_result):
        headers = {"Content-Type": "text/tab-separated-values; charset=UTF-8"}
        return make_response(serialize_query_result_to_dsv(query_result, "\t"), 200, headers)

    @staticmethod
    def make_excel_response(query_result):
        headers = {
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        }
        return make_response(serialize_query_result_to_xlsx(query_result), 200, headers)
