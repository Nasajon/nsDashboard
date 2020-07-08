import i18n from 'i18next'
import LanguageDetector from 'i18next-browser-languagedetector'
import { initReactI18next } from 'react-i18next'
import pt from '@/locales/pt-BR.json'
i18n.use(LanguageDetector).use(initReactI18next)
    .init({
        fallbackLng: "pt-BR",
        resources: pt,
        keySeparator: false,
        nsSeparator: false
    });

export default i18n;