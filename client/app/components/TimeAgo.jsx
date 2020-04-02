import moment from "moment";
import { isNil } from "lodash";
import React, { useEffect, useMemo, useState } from "react";
import PropTypes from "prop-types";
import { Moment } from "@/components/proptypes";
import { clientConfig } from "@/services/auth";
import Tooltip from "antd/lib/tooltip";
import { useTranslation } from 'react-i18next';
function toMoment(value) {
  value = !isNil(value) ? moment(value) : null;
  return value && value.isValid() ? value : null;
}

export default function TimeAgo({ date, placeholder, autoUpdate }) {
  const startDate = toMoment(date);
  const [value, setValue] = useState(null);
  const title = useMemo(() => (startDate ? startDate.format(clientConfig.dateTimeFormat) : null), [startDate]);
  const { t } = useTranslation();
  useEffect(() => {
    function update() {
      var temp = startDate ? startDate.fromNow() : placeholder;
      var time = temp.match(/(\d+)/);
      if (time !== null) {
        temp = temp.replace(/[0-9]/g, '').trim();
        temp = t(temp, { "time": time[0] });
      } else {
        temp = t(temp)
      }
      setValue(temp);
    }
    update();

    if (autoUpdate) {
      const timer = setInterval(update, 30 * 1000);
      return () => clearInterval(timer);
    }
  }, [autoUpdate, startDate, placeholder, t]);

  return (
    <Tooltip title={title}>
      <span data-test="TimeAgo">{value}</span>
    </Tooltip>
  );
}

TimeAgo.propTypes = {
  date: PropTypes.oneOfType([PropTypes.string, PropTypes.number, PropTypes.instanceOf(Date), Moment]),
  placeholder: PropTypes.string,
  autoUpdate: PropTypes.bool,
};

TimeAgo.defaultProps = {
  date: null,
  placeholder: "",
  autoUpdate: true,
};
