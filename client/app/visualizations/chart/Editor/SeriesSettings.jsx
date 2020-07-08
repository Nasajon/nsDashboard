import { includes, map, extend, fromPairs } from "lodash";
import React, { useMemo, useCallback } from "react";
import { useDebouncedCallback } from "use-debounce";
import Table from "antd/lib/table";
import Input from "antd/lib/input";
import Radio from "antd/lib/radio";
import Empty from "antd/lib/empty";
import { sortableElement } from "react-sortable-hoc";
import { SortableContainer, DragHandle } from "@/components/sortable";
import { EditorPropTypes } from "@/visualizations/prop-types";
import ChartTypeSelect from "./ChartTypeSelect";
import getChartData from "../getChartData";
import { useTranslation } from 'react-i18next';
const SortableBodyRow = sortableElement(props => <tr {...props} />);

function getTableColumns(options, updateSeriesOption, debouncedUpdateSeriesOption, t) {
  
  const result = [
    {
      title: t("Order"),
      dataIndex: "zIndex",
      className: "text-nowrap",
      render: (unused, item) => (
        <span className="d-flex align-items-center">
          <DragHandle />
          {item.zIndex + 1}
        </span>
      ),
    },
    {
      title: t("Label"),
      dataIndex: "name",
      className: "text-nowrap",
      render: (unused, item) => (
        <Input
          data-test={`Chart.Series.${item.key}.Label`}
          placeholder={item.key}
          defaultValue={item.name}
          onChange={event => debouncedUpdateSeriesOption(item.key, "name", event.target.value)}
        />
      ),
    },
  ];

  if (!includes(["pie", "heatmap"], options.globalSeriesType)) {
    result.push({
      title: t("Y Axis"),
      dataIndex: "yAxis",
      className: "text-nowrap",
      render: (unused, item) => (
        <Radio.Group
          className="text-nowrap"
          value={item.yAxis === 1 ? 1 : 0}
          onChange={event => updateSeriesOption(item.key, "yAxis", event.target.value)}>
          <Radio value={0} data-test={`Chart.Series.${item.key}.UseLeftAxis`}>
            {t("left")}
          </Radio>
          <Radio value={1} data-test={`Chart.Series.${item.key}.UseRightAxis`}>
            {t("right")}
          </Radio>
        </Radio.Group>
      ),
    });
    result.push({
      title: t("Type"),
      dataIndex: "type",
      className: "text-nowrap",
      render: (unused, item) => (
        <ChartTypeSelect
          className="w-100"
          data-test={`Chart.Series.${item.key}.Type`}
          dropdownMatchSelectWidth={false}
          value={item.type}
          onChange={value => updateSeriesOption(item.key, "type", value)}
        />
      ),
    });
  }

  return result;
}

export default function SeriesSettings({ options, data, onOptionsChange }) {
  const series = useMemo(
    () =>
      map(
        getChartData(data.rows, options), // returns sorted series
        ({ name }, zIndex) =>
          extend({ key: name, type: options.globalSeriesType }, options.seriesOptions[name], { zIndex })
      ),
    [options, data]
  );

  const handleSortEnd = useCallback(
    ({ oldIndex, newIndex }) => {
      const seriesOptions = [...series];
      seriesOptions.splice(newIndex, 0, ...seriesOptions.splice(oldIndex, 1));
      onOptionsChange({ seriesOptions: fromPairs(map(seriesOptions, ({ key }, zIndex) => [key, { zIndex }])) });
    },
    [onOptionsChange, series]
  );

  const updateSeriesOption = useCallback(
    (key, prop, value) => {
      onOptionsChange({
        seriesOptions: {
          [key]: {
            [prop]: value,
          },
        },
      });
    },
    [onOptionsChange]
  );
  const [debouncedUpdateSeriesOption] = useDebouncedCallback(updateSeriesOption, 200);
  const { t } = useTranslation()
  const columns = useMemo(() => getTableColumns(options, updateSeriesOption, debouncedUpdateSeriesOption, t), [
    options,
    updateSeriesOption,
    debouncedUpdateSeriesOption,
    t
  ]);

  return (
    <SortableContainer
      axis="y"
      lockAxis="y"
      lockToContainerEdges
      useDragHandle
      helperClass="chart-editor-series-dragged-item"
      helperContainer={container => container.querySelector("tbody")}
      onSortEnd={handleSortEnd}
      containerProps={{
        className: "chart-editor-series",
      }}>
      <Table
        dataSource={series}
        columns={columns}
        components={{
          body: {
            row: SortableBodyRow,
          },
        }}
        onRow={item => ({ index: item.zIndex })}
        pagination={false}
        locale = {{emptyText: <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={t("No Data")} />}}
      />
    </SortableContainer>
  );
}

SeriesSettings.propTypes = EditorPropTypes;
