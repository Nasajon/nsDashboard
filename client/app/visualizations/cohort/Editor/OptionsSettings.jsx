import { map } from "lodash";
import React from "react";
import { Section, Select } from "@/components/visualizations/editor";
import { EditorPropTypes } from "@/visualizations/prop-types";
import { useTranslation } from 'react-i18next';
const CohortTimeIntervals = {
  daily: "Daily",
  weekly: "Weekly",
  monthly: "Monthly",
};

const CohortModes = {
  diagonal: "Fill gaps with zeros",
  simple: "Show data as is",
};

export default function OptionsSettings({ options, onOptionsChange }) {
  const { t } = useTranslation()
  return (
    <React.Fragment>
      <Section>
        <Select
          label={t("Time Interval")}
          data-test="Cohort.TimeInterval"
          className="w-100"
          value={options.timeInterval}
          onChange={timeInterval => onOptionsChange({ timeInterval })}>
          {map(CohortTimeIntervals, (name, value) => (
            <Select.Option key={value} data-test={"Cohort.TimeInterval." + value}>
              {t(name)}
            </Select.Option>
          ))}
        </Select>
      </Section>

      <Section>
        <Select
          label={t("Mode")}
          data-test="Cohort.Mode"
          className="w-100"
          value={options.mode}
          onChange={mode => onOptionsChange({ mode })}>
          {map(CohortModes, (name, value) => (
            <Select.Option key={value} data-test={"Cohort.Mode." + value}>
              {t(name)}
            </Select.Option>
          ))}
        </Select>
      </Section>
    </React.Fragment>
  );
}

OptionsSettings.propTypes = EditorPropTypes;
