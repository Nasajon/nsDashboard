import React from "react";
import { Section, Switch } from "@/components/visualizations/editor";
import { EditorPropTypes } from "@/visualizations/prop-types";
import { useTranslation } from 'react-i18next';
import AxisSettings from "./AxisSettings";

export default function XAxisSettings({ options, onOptionsChange }) {
  const { t } = useTranslation();
  return (
    <React.Fragment>
      <AxisSettings
        id="XAxis"
        features={{ autoDetectType: true }}
        options={options.xAxis}
        onChange={xAxis => onOptionsChange({ xAxis })}
      />

      <Section>
        <Switch
          data-test="Chart.XAxis.Sort"
          defaultChecked={options.sortX}
          onChange={sortX => onOptionsChange({ sortX })}>
          {t("Sort Values")}
        </Switch>
      </Section>

      <Section>
        <Switch
          data-test="Chart.XAxis.Reverse"
          defaultChecked={options.reverseX}
          onChange={reverseX => onOptionsChange({ reverseX })}>
          {t("Reverse Order")}
        </Switch>
      </Section>

      <Section>
        <Switch
          data-test="Chart.XAxis.ShowLabels"
          defaultChecked={options.xAxis.labels.enabled}
          onChange={enabled => onOptionsChange({ xAxis: { labels: { enabled } } })}>
          {t("Show Labels")}
        </Switch>
      </Section>
    </React.Fragment>
  );
}

XAxisSettings.propTypes = EditorPropTypes;
