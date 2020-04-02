import React from "react";
import PropTypes from "prop-types";
import Tooltip from "antd/lib/tooltip";
import { localizeTime, durationHumanize } from "@/lib/utils";
import { RefreshScheduleType, RefreshScheduleDefault } from "../proptypes";
import { withTranslation } from 'react-i18next';
import "./ScheduleDialog.css";

class SchedulePhrase extends React.Component {
  static propTypes = {
    schedule: RefreshScheduleType,
    isNew: PropTypes.bool.isRequired,
    isLink: PropTypes.bool,
    onClick: PropTypes.func,
  };

  static defaultProps = {
    schedule: RefreshScheduleDefault,
    isLink: false,
    onClick: () => { },
  };

  get content() {
    const { interval: seconds } = this.props.schedule || SchedulePhrase.defaultProps.schedule;
    if (!seconds) {
      return [this.props.t("Never")];
    }
    const humanized = durationHumanize(seconds, {
      omitSingleValueNumber: true,
    });
    const short = this.props.t("EveryTime", { time: humanized });
    let full = this.props.t("RefreshesEvery", { time: humanized });

    const { time, day_of_week: dayOfWeek } = this.props.schedule;
    if (time) {
      full += " " + this.props.t("at") + " " + localizeTime(time);
    }
    if (dayOfWeek) {
      full += " " + this.props.t("on", { context: dayOfWeek === "Sunday" || dayOfWeek === "Saturday" ? "male" : "female" }) + " " + this.props.t(dayOfWeek);
    }

    return [short, full];
  }

  render() {
    if (this.props.isNew) {
      return this.props.t("Never");
    }

    const [short, full] = this.content;
    const content = full ? <Tooltip title={full}>{short}</Tooltip> : short;

    return this.props.isLink ? (
      <a className="schedule-phrase" onClick={this.props.onClick}>
        {content}
      </a>
    ) : (
        content
      );
  }
}

export default withTranslation()(SchedulePhrase)
