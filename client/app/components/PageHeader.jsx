import React from "react";
import PropTypes from "prop-types";
import { useTranslation } from 'react-i18next';
export default function PageHeader({ title }) {
  const { t } = useTranslation();
  return (
    <div className="page-header-wrapper row p-l-15 p-r-15 m-b-10 m-l-0 m-r-0">
      <div className="col-sm-9 p-l-0 p-r-0">
        <h3>{t(title)}</h3>
      </div>
    </div>
  );
}

PageHeader.propTypes = {
  title: PropTypes.string.isRequired,
};
