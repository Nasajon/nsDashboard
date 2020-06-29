import { isString, isObject, isFinite, isNumber, merge } from "lodash";
import React from "react";
import PropTypes from "prop-types";
import { useDebouncedCallback } from "use-debounce";
import * as Grid from "antd/lib/grid";
import { Section, Select, Input, InputNumber } from "@/components/visualizations/editor";
import { useTranslation } from 'react-i18next';
function toNumber(value) {
  value = isNumber(value) ? value : parseFloat(value);
  return isFinite(value) ? value : null;
}

export default function AxisSettings({ id, options, features, onChange }) {
  function optionsChanged(newOptions) {
    onChange(merge({}, options, newOptions));
  }
  const { t } = useTranslation();
  const [handleNameChange] = useDebouncedCallback(text => {
    const title = isString(text) && text !== "" ? { text } : null;
    optionsChanged({ title });
  }, 200);

  const [handleMinMaxChange] = useDebouncedCallback(opts => optionsChanged(opts), 200);

  return (
    <React.Fragment>
      <Section>
        <Select
          label={t("Scale")}
          className="w-100"
          data-test={`Chart.${id}.Type`}
          defaultValue={options.type}
          onChange={type => optionsChanged({ type })}>
          {features.autoDetectType && (
            <Select.Option value="-" data-test={`Chart.${id}.Type.Auto`}>
              {t("Auto Detect")}
            </Select.Option>
          )}
          <Select.Option value="datetime" data-test={`Chart.${id}.Type.DateTime`}>
            {t("Datetime")}
          </Select.Option>
          <Select.Option value="linear" data-test={`Chart.${id}.Type.Linear`}>
            {t("Linear")}
          </Select.Option>
          <Select.Option value="logarithmic" data-test={`Chart.${id}.Type.Logarithmic`}>
            {t("Logarithmic")}
          </Select.Option>
          <Select.Option value="category" data-test={`Chart.${id}.Type.Category`}>
            {t("Category")}
          </Select.Option>
        </Select>
      </Section>

      <Section>
        <Input
          label={t("Name")}
          data-test={`Chart.${id}.Name`}
          defaultValue={isObject(options.title) ? options.title.text : null}
          onChange={event => handleNameChange(event.target.value)}
        />
      </Section>

      {features.range && (
        <Section>
          <Grid.Row gutter={15} type="flex" align="middle">
            <Grid.Col span={12}>
              <InputNumber
                label={t("Min Value")}
                className="w-100"
                placeholder="Auto"
                data-test={`Chart.${id}.RangeMin`}
                defaultValue={toNumber(options.rangeMin)}
                onChange={value => handleMinMaxChange({ rangeMin: toNumber(value) })}
              />
            </Grid.Col>
            <Grid.Col span={12}>
              <InputNumber
                label={t("Max Value")}
                className="w-100"
                placeholder="Auto"
                data-test={`Chart.${id}.RangeMax`}
                defaultValue={toNumber(options.rangeMax)}
                onChange={value => handleMinMaxChange({ rangeMax: toNumber(value) })}
              />
            </Grid.Col>
          </Grid.Row>
        </Section>
      )}
    </React.Fragment>
  );
}

AxisSettings.propTypes = {
  id: PropTypes.string.isRequired,
  options: PropTypes.shape({
    type: PropTypes.string.isRequired,
    title: PropTypes.shape({
      text: PropTypes.string,
    }),
    rangeMin: PropTypes.number,
    rangeMax: PropTypes.number,
  }).isRequired,
  features: PropTypes.shape({
    autoDetectType: PropTypes.bool,
    range: PropTypes.bool,
  }),
  onChange: PropTypes.func,
};

AxisSettings.defaultProps = {
  features: {},
  onChange: () => {},
};
