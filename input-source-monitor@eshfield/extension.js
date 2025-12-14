import Gio from "gi://Gio";
import GLib from "gi://GLib";
import St from "gi://St";

import { Extension } from "resource:///org/gnome/shell/extensions/extension.js";
import * as Main from "resource:///org/gnome/shell/ui/main.js";
import * as PanelMenu from "resource:///org/gnome/shell/ui/panelMenu.js";
import * as Keyboard from "resource:///org/gnome/shell/ui/status/keyboard.js";

const ICON_NAME = "view-wrapped-symbolic";
const ICON_STYLE = "system-status-icon";

const DBUS_INTERFACE = `
    <node>
        <interface name="org.gnome.InputSourceMonitor">
            <signal name="SourceChanged">
                <arg type="s" name="source"/>
            </signal>
        </interface>
    </node>
`;
const DBUS_NAME = "org.gnome.InputSourceMonitor";
const DBUS_PATH = "/org/gnome/InputSourceMonitor";
const DBUS_SIGNAL_NAME = "SourceChanged";
const MANAGER_SIGNAL_NAME = "current-source-changed";

export default class InputSourceMonitorExtension extends Extension {
    constructor(metadata) {
        super(metadata);

        this._dbus = null;
        this._indicator = null;
        this._manager = Keyboard.getInputSourceManager();
        this._ownerId = null;
        this._signalId = null;
    }

    enable() {
        // setup panel indicator
        this._indicator = new PanelMenu.Button(0.0, this.metadata.name, false);

        const icon = new St.Icon({
            icon_name: ICON_NAME,
            style_class: ICON_STYLE,
        });

        this._indicator.add_child(icon);
        Main.panel.addToStatusArea(this.uuid, this._indicator);

        // setup D-Bus interface
        this._dbus = Gio.DBusExportedObject.wrapJSObject(
            DBUS_INTERFACE,
            this,
        );
        this._dbus.export(Gio.DBus.session, DBUS_PATH);

        // reserve D-Bus name
        this._ownerId = Gio.DBus.session.own_name(
            DBUS_NAME,
            Gio.BusNameOwnerFlags.NONE,
            null,
            null
        );

        // subscribe to input source changes
        this._signalId = this._manager.connect(
            MANAGER_SIGNAL_NAME,
            () => {
                const source = this._manager.currentSource;
                this._dbus.emit_signal(
                    DBUS_SIGNAL_NAME,
                    GLib.Variant.new("(s)", [source.id])
                );
            },
        );
    }

    disable() {
        if (this._signalId) {
            this._manager.disconnect(this._signalId);
            this._signalId = null;
        }

        if (this._dbus) {
            this._dbus.flush();
            this._dbus.unexport();
            this._dbus = null;
        }

        if (this._ownerId) {
            Gio.DBus.session.unown_name(this._ownerId);
            this._ownerId = null;
        }

        if (this._indicator) {
            this._indicator.destroy();
            this._indicator = null;
        }
    }
}
