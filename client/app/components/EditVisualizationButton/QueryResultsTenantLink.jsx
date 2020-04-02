import React from "react";
import PropTypes from "prop-types";

export default function QueryResultsTenantLink(props) {
  let href = "";

  const { query, queryResult, fileType } = props;
  const resultId = queryResult.getId && queryResult.getId();
  const resultData = queryResult.getData && queryResult.getData();
  const tenant = queryResult.getTenant && queryResult.getTenant();

  if (resultId && resultData && query.name) {
    if (query.id) {
      href = `api/queries/${query.id}/tenant/${tenant}/results/${resultId}.${fileType}${props.embed ? `?api_key=${props.apiKey}` : ""}`;
    } else {
      href = ``;
    }
  }

  return (
    <a target="_blank" rel="noopener noreferrer" disabled={props.disabled} href={href} download>
      {props.children}
    </a>
  );
}

QueryResultsTenantLink.propTypes = {
  query: PropTypes.object.isRequired, // eslint-disable-line react/forbid-prop-types
  queryResult: PropTypes.object, // eslint-disable-line react/forbid-prop-types
  fileType: PropTypes.string,
  disabled: PropTypes.bool.isRequired,
  embed: PropTypes.bool,
  apiKey: PropTypes.string,
  children: PropTypes.oneOfType([PropTypes.arrayOf(PropTypes.node), PropTypes.node]).isRequired,
};

QueryResultsTenantLink.defaultProps = {
  queryResult: {},
  fileType: "csv",
  embed: false,
  apiKey: "",
};
