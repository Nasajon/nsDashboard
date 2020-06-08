from sys import exit

from sqlalchemy.orm.exc import NoResultFound

from redash import models
from redash.query_runner import (
    get_configuration_schema_for_query_runner_type,
    query_runners,
)
from redash.utils import json_loads
from redash.utils.configuration import ConfigurationContainer

def validate_data_source_type(type):
    if type not in query_runners.keys():
        print(
            'Error: the type "{}" is not supported (supported types: {}).'.format(
                type, ", ".join(query_runners.keys())
            )
        )
        print("OJNK")
        exit(1)


def new(name, type, options, organization="default"):
    """Create new data source."""

    data_source = models.DataSource.get_by_name(name)

    if data_source is not None:
        print("Error: Already exists a datasource with that name.")
        return 

    validate_data_source_type(type)

    query_runner = query_runners[type]
    schema = query_runner.configuration_schema()

    options = ConfigurationContainer(options, schema)

    if not options.is_valid():
        print("Error: invalid configuration.")
        exit(1)

    print(
        "Creating {} data source ({}) with options:\n{}".format(
            type, name, options.to_json()
        )
    )

    data_source = models.DataSource.create_with_group(
        name=name,
        type=type,
        options=options,
        org=models.Organization.get_by_slug(organization),
    )
    models.db.session.commit()