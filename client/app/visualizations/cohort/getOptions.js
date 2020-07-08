import i18n from "@/i18n"
const DEFAULT_OPTIONS = {
  timeInterval: "daily",
  mode: "diagonal",
  dateColumn: i18n.t("date"),
  stageColumn: i18n.t("day_number"),
  totalColumn: i18n.t("total"),
  valueColumn: i18n.t("value"),
};

export default function getOptions(options) {
  return { ...DEFAULT_OPTIONS, ...options };
}
