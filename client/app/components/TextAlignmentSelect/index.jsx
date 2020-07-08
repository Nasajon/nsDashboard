import { pickBy, startsWith } from "lodash";
import React from "react";
import PropTypes from "prop-types";
import cx from "classnames";
import Radio from "antd/lib/radio";
import Icon from "antd/lib/icon";
import Tooltip from "antd/lib/tooltip";
import { useTranslation } from 'react-i18next';
import "./index.less";

export default function TextAlignmentSelect({ className, ...props }) {
  const { t } = useTranslation();
  return (
    // Antd RadioGroup does not use any custom attributes
    <div {...pickBy(props, (v, k) => startsWith(k, "data-"))}>
      <Radio.Group className={cx("text-alignment-select", className)} {...props}>
        <Tooltip title={t("Align left")} mouseEnterDelay={0} mouseLeaveDelay={0}>
          <Radio.Button value="left" data-test="TextAlignmentSelect.Left">
            <Icon type="align-left" />
          </Radio.Button>
        </Tooltip>
        <Tooltip title={t("Align center")} mouseEnterDelay={0} mouseLeaveDelay={0}>
          <Radio.Button value="center" data-test="TextAlignmentSelect.Center">
            <Icon type="align-center" />
          </Radio.Button>
        </Tooltip>
        <Tooltip title={t("Align right")} mouseEnterDelay={0} mouseLeaveDelay={0}>
          <Radio.Button value="right" data-test="TextAlignmentSelect.Right">
            <Icon type="align-right" />
          </Radio.Button>
        </Tooltip>
      </Radio.Group>
    </div>
  );
}

TextAlignmentSelect.propTypes = {
  className: PropTypes.string,
};

TextAlignmentSelect.defaultProps = {
  className: null,
};
