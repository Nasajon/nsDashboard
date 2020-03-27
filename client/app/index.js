import React from "react";
import ReactDOM from "react-dom";
import ApplicationArea from "@/components/ApplicationArea";
import { I18nextProvider } from 'react-i18next';
import i18n from './i18n.js';

import "@/config";

import offlineListener from "@/services/offline-listener";

ReactDOM.render(<I18nextProvider i18n={i18n}><ApplicationArea /></I18nextProvider>, document.getElementById("application-root"), () => {
  offlineListener.init();
});
