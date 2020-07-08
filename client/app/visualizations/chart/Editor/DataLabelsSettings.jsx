import { includes } from "lodash";
import React from "react";
import { useDebouncedCallback } from "use-debounce";
import { Section, Input, Checkbox, ContextHelp } from "@/components/visualizations/editor";
import { EditorPropTypes } from "@/visualizations/prop-types";
import { useTranslation } from 'react-i18next';
export default function DataLabelsSettings({ options, onOptionsChange }) {
  const isShowDataLabelsAvailable = includes(
    ["line", "area", "column", "scatter", "pie", "heatmap"],
    options.globalSeriesType
  );

  const [debouncedOnOptionsChange] = useDebouncedCallback(onOptionsChange, 200);
  const { t } = useTranslation();
  return (
    <React.Fragment>
      {isShowDataLabelsAvailable && (
        <Section>
          <Checkbox
            data-test="Chart.DataLabels.ShowDataLabels"
            defaultChecked={options.showDataLabels}
            onChange={event => onOptionsChange({ showDataLabels: event.target.checked })}>
            {t("Show Data Labels")}
          </Checkbox>
        </Section>
      )}

      <Section>
        <Input
          label={
            <React.Fragment>
              {t("Number Values Format")}
              <ContextHelp.NumberFormatSpecs />
            </React.Fragment>
          }
          data-test="Chart.DataLabels.NumberFormat"
          defaultValue={options.numberFormat}
          onChange={e => debouncedOnOptionsChange({ numberFormat: e.target.value })}
        />
      </Section>

      <Section>
        <Input
          label={
            <React.Fragment>
              {t("Percent Values Format")}
              <ContextHelp.NumberFormatSpecs />
            </React.Fragment>
          }
          data-test="Chart.DataLabels.PercentFormat"
          defaultValue={options.percentFormat}
          onChange={e => debouncedOnOptionsChange({ percentFormat: e.target.value })}
        />
      </Section>

      <Section>
        <Input
          label={
            <React.Fragment>
              {t("Date/Time Values Format")}
              <ContextHelp.DateTimeFormatSpecs />
            </React.Fragment>
          }
          data-test="Chart.DataLabels.DateTimeFormat"
          defaultValue={options.dateTimeFormat}
          onChange={e => debouncedOnOptionsChange({ dateTimeFormat: e.target.value })}
        />
      </Section>

      <Section>
        <Input
          label={
            <React.Fragment>
              {t("Data Labels")}
              <ContextHelp placement="topRight" arrowPointAtCenter>
                <div className="p-b-5">{t("Use special names to access additional properties:")}</div>
                <div>
                  <code>{"{{ @@name }}"}</code> {t("series name")};
                </div>
                <div>
                  <code>{"{{ @@x }}"}</code> {t("x-value")};
                </div>
                <div>
                  <code>{"{{ @@y }}"}</code> {t("y-value")};
                </div>
                <div>
                  <code>{"{{ @@yPercent }}"}</code> {t("relative y-value")};
                </div>
                <div>
                  <code>{"{{ @@yError }}"}</code> {t("y deviation")};
                </div>
                <div>
                  <code>{"{{ @@size }}"}</code> {t("bubble size")};
                </div>
                <div className="p-t-5">
                  {t("Also, all query result columns can be referenced")}
                  <br />
                  {t("using")}
                  <code className="text-nowrap">{"{{ column_name }}"}</code> {t("syntax")}.
                </div>
              </ContextHelp>
            </React.Fragment>
          }
          data-test="Chart.DataLabels.TextFormat"
          placeholder="(auto)"
          defaultValue={options.textFormat}
          onChange={e => debouncedOnOptionsChange({ textFormat: e.target.value })}
        />
      </Section>
    </React.Fragment>
  );
}

DataLabelsSettings.propTypes = EditorPropTypes;
