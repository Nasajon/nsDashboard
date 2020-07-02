import { extend, trim } from "lodash";
import React from "react";
import PropTypes from "prop-types";
import { useDebouncedCallback } from "use-debounce";
import { Section, Input, ControlLabel, ContextHelp } from "@/components/visualizations/editor";
import { formatSimpleTemplate } from "@/lib/value-format";
import { useTranslation } from 'react-i18next';

function Editor({ column, onChange }) {
  const [onChangeDebounced] = useDebouncedCallback(onChange, 200);
  const { t } = useTranslation();
  return (
    <React.Fragment>
      <Section>
        <Input
          label={t("URL template")}
          data-test="Table.ColumnEditor.Image.UrlTemplate"
          defaultValue={column.imageUrlTemplate}
          onChange={event => onChangeDebounced({ imageUrlTemplate: event.target.value })}
        />
      </Section>

      <Section>
        <ControlLabel
          label={
            <React.Fragment>
              {t("Size")}
              <ContextHelp placement="topLeft" arrowPointAtCenter>
                <div className="m-b-5">{t("Any positive integer value that specifies size in pixels.")}</div>
                <div>{t("Leave empty to use default value.")}</div>
              </ContextHelp>
            </React.Fragment>
          }>
          <div className="d-flex align-items-center">
            <Input
              data-test="Table.ColumnEditor.Image.Width"
              placeholder={t("Width")}
              defaultValue={column.imageWidth}
              onChange={event => onChangeDebounced({ imageWidth: event.target.value })}
            />
            <span className="p-l-5 p-r-5">&times;</span>
            <Input
              data-test="Table.ColumnEditor.Image.Height"
              placeholder={t("Height")}
              defaultValue={column.imageHeight}
              onChange={event => onChangeDebounced({ imageHeight: event.target.value })}
            />
          </div>
        </ControlLabel>
      </Section>

      <Section>
        <Input
          label={t("Title template")}
          data-test="Table.ColumnEditor.Image.TitleTemplate"
          defaultValue={column.imageTitleTemplate}
          onChange={event => onChangeDebounced({ imageTitleTemplate: event.target.value })}
        />
      </Section>

      <Section>
        <ContextHelp
          placement="topLeft"
          arrowPointAtCenter
          icon={<span style={{ cursor: "default" }}>{t("Format specs")} {ContextHelp.defaultIcon}</span>}>
          <div>
            {t("All columns can be referenced using")} <code>{"{{ column_name }}"}</code> {t("syntax")}.
          </div>
          <div>
            {t("Use")} <code>{"{{ @ }}"}</code> {t("to reference current (this) column")}.
          </div>
          <div>{t("This syntax is applicable to URL, Title and Size options")}.</div>
        </ContextHelp>
      </Section>
    </React.Fragment>
  );
}

Editor.propTypes = {
  column: PropTypes.shape({
    name: PropTypes.string.isRequired,
    imageUrlTemplate: PropTypes.string,
    imageWidth: PropTypes.string,
    imageHeight: PropTypes.string,
    imageTitleTemplate: PropTypes.string,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
};

export default function initImageColumn(column) {
  function prepareData(row) {
    row = extend({ "@": row[column.name] }, row);

    const src = trim(formatSimpleTemplate(column.imageUrlTemplate, row));
    if (src === "") {
      return {};
    }

    const width = parseInt(formatSimpleTemplate(column.imageWidth, row), 10);
    const height = parseInt(formatSimpleTemplate(column.imageHeight, row), 10);
    const title = trim(formatSimpleTemplate(column.imageTitleTemplate, row));

    const result = { src };

    if (Number.isFinite(width) && width > 0) {
      result.width = width;
    }
    if (Number.isFinite(height) && height > 0) {
      result.height = height;
    }
    if (title !== "") {
      result.text = title; // `text` is used for search
      result.title = title;
      result.alt = title;
    }

    return result;
  }

  function ImageColumn({ row }) {
    // eslint-disable-line react/prop-types
    const { text, ...props } = prepareData(row);
    return <img alt="" {...props} />;
  }

  ImageColumn.prepareData = prepareData;

  return ImageColumn;
}

initImageColumn.friendlyName = "Image";
initImageColumn.Editor = Editor;
