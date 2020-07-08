import React from "react";
import Menu from "antd/lib/menu";
import PageHeader from "@/components/PageHeader";
import location from "@/services/location";
import settingsMenu from "@/services/settingsMenu";
import { useTranslation } from 'react-i18next';

function wrapSettingsTab(options, WrappedComponent) {
  if (options) {
    settingsMenu.add(options);
  }

  return function SettingsTab(props) {
    const activeItem = settingsMenu.getActiveItem(location.path);
    const { t } = useTranslation();
    return (
      <div className="settings-screen">
        <div className="container">
          <PageHeader title="Settings" />
          <div className="bg-white tiled">
            <Menu selectedKeys={[activeItem && activeItem.title]} selectable={false} mode="horizontal">
              {settingsMenu.items
                .filter(item => item.isAvailable())
                .map(item => (
                  <Menu.Item key={item.title}>
                    <a href={item.path} data-test="SettingsScreenItem">
                      {t(item.title)}
                    </a>
                  </Menu.Item>
                ))}
            </Menu>
            <div className="p-15">
              <div>
                <WrappedComponent {...props} />
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };
}

export default wrapSettingsTab;
