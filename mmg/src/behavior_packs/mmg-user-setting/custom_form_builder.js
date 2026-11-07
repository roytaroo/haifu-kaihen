import {
    CustomForm,
    ObservableString,
    ObservableNumber,
    ObservableBoolean,
    ObservableUIRawMessage,
} from "@minecraft/server-ui";

import { Player } from "@minecraft/server";

export class CustomFormBuilder {
    /** @type {Player} */
    player;

    /** @type {Array<(form: CustomForm) => void>} */
    elements = [];

    /** @type {Map<string, ObservableString | ObservableNumber | ObservableBoolean | ObservableUIRawMessage>} */
    observables = new Map();

    /** @type {ObservableString} */
    title;

    /** @type {CustomForm | undefined} */
    form;

    /**
     * @param {Player} player
     * @param {string} [title="Custom Form"]
     */
    constructor(player, title = "Custom Form") {
        this.player = player;
        this.title = new ObservableString(String(title));
    }

    /**
     * @param {string} name
     * @param {ObservableString | ObservableNumber | ObservableBoolean | ObservableUIRawMessage} observable
     * @returns {CustomFormBuilder}
     */
    register(name, observable) {
        if (this.observables.has(name)) {
            throw new Error(`Observable "${name}" is already registered.`);
        }

        this.observables.set(name, observable);
        return this;
    }

    /**
     * @template {ObservableString | ObservableNumber | ObservableBoolean | ObservableUIRawMessage} T
     * @param {string} name
     * @returns {T}
     */
    get(name) {
        const observable = this.observables.get(name);

        if (!observable) {
            throw new Error(`Observable "${name}" was not found.`);
        }

        return /** @type {T} */ (observable);
    }

    /**
     * @param {string} name
     * @returns {boolean}
     */
    has(name) {
        return this.observables.has(name);
    }

    /**
     * @param {string} text
     * @returns {CustomFormBuilder}
     */
    setTitle(text) {
        this.title.setData(String(text));
        return this;
    }

    /**
     * @param {string | import("@minecraft/server-ui").UIRawMessage | ObservableString | ObservableUIRawMessage} text
     * @param {import("@minecraft/server-ui").HeaderOptions} [options]
     * @returns {CustomFormBuilder}
     */
    header(text, options) {
        this.elements.push(form => {
            form.header(text, options);
        });

        return this;
    }

    /**
     * @param {string | import("@minecraft/server-ui").UIRawMessage | ObservableString | ObservableUIRawMessage} text
     * @param {import("@minecraft/server-ui").TextOptions} [options]
     * @returns {CustomFormBuilder}
     */
    label(text, options) {
        this.elements.push(form => {
            form.label(text, options);
        });

        return this;
    }

    /**
     * @param {import("@minecraft/server-ui").SpacingOptions} [options]
     * @returns {CustomFormBuilder}
     */
    spacer(options) {
        this.elements.push(form => {
            form.spacer(options);
        });

        return this;
    }

    /**
     * @param {import("@minecraft/server-ui").DividerOptions} [options]
     * @returns {CustomFormBuilder}
     */
    divider(options) {
        this.elements.push(form => {
            form.divider(options);
        });

        return this;
    }

    /**
     * @param {string} name
     * @param {string | import("@minecraft/server-ui").UIRawMessage | ObservableString | ObservableUIRawMessage} label
     * @param {string} [defaultValue=""]
     * @param {(value: string, player: Player) => void} [onChange]
     * @param {import("@minecraft/server-ui").TextFieldOptions} [options]
     * @returns {CustomFormBuilder}
     */
    textField(name, label, defaultValue = "", onChange, options) {
        const observable = new ObservableString(String(defaultValue), {
            clientWritable: true,
        });

        if (onChange) {
            observable.subscribe(value => {
                onChange(value, this.player);
            });
        }

        this.register(name, observable);

        this.elements.push(form => {
            form.textField(label, observable, options);
        });

        return this;
    }

    /**
     * @param {string} name
     * @param {string | import("@minecraft/server-ui").UIRawMessage | ObservableString | ObservableUIRawMessage} label
     * @param {boolean} [defaultValue=false]
     * @param {(value: boolean, player: Player) => void} [onChange]
     * @param {import("@minecraft/server-ui").ToggleOptions} [options]
     * @returns {CustomFormBuilder}
     */
    toggle(name, label, defaultValue = false, onChange, options) {
        const observable = new ObservableBoolean(Boolean(defaultValue), {
            clientWritable: true,
        });

        if (onChange) {
            observable.subscribe(value => {
                onChange(value, this.player);
            });
        }

        this.register(name, observable);

        this.elements.push(form => {
            form.toggle(label, observable, options);
        });

        return this;
    }

    /**
     * @param {string} name
     * @param {string | import("@minecraft/server-ui").UIRawMessage | ObservableString | ObservableUIRawMessage} label
     * @param {number} defaultValue
     * @param {number | ObservableNumber} min
     * @param {number | ObservableNumber} max
     * @param {(value: number, player: Player) => void} [onChange]
     * @param {import("@minecraft/server-ui").SliderOptions} [options]
     * @returns {CustomFormBuilder}
     */
    slider(name, label, defaultValue, min, max, onChange, options) {
        const observable = new ObservableNumber(Number(defaultValue), {
            clientWritable: true,
        });

        if (onChange) {
            observable.subscribe(value => {
                onChange(value, this.player);
            });
        }

        this.register(name, observable);

        this.elements.push(form => {
            form.slider(label, observable, min, max, options);
        });

        return this;
    }

    /**
     * @param {string} name
     * @param {string | import("@minecraft/server-ui").UIRawMessage | ObservableString | ObservableUIRawMessage} label
     * @param {import("@minecraft/server-ui").DropdownItem[]} items
     * @param {number} [defaultIndex=0]
     * @param {(value: number, player: Player) => void} [onChange]
     * @param {import("@minecraft/server-ui").DropdownOptions} [options]
     * @returns {CustomFormBuilder}
     */
    dropdown(name, label, items, defaultIndex = 0, onChange, options) {
        const defaultItem = items[defaultIndex];

        const initialValue =
            defaultItem && typeof defaultItem === "object"
                ? defaultItem.value
                : defaultIndex;

        const observable = new ObservableNumber(Number(initialValue), {
            clientWritable: true,
        });

        if (onChange) {
            observable.subscribe(value => {
                onChange(value, this.player);
            });
        }

        this.register(name, observable);

        this.elements.push(form => {
            form.dropdown(label, observable, items, options);
        });

        return this;
    }

    /**
     * @param {string} name
     * @param {string} [defaultValue=""]
     * @returns {CustomFormBuilder}
     */
    string(name, defaultValue = "") {
        return this.register(
            name,
            new ObservableString(String(defaultValue))
        );
    }

    /**
     * @param {string} name
     * @param {number} [defaultValue=0]
     * @returns {CustomFormBuilder}
     */
    number(name, defaultValue = 0) {
        return this.register(
            name,
            new ObservableNumber(Number(defaultValue))
        );
    }

    /**
     * @param {string} name
     * @param {boolean} [defaultValue=false]
     * @returns {CustomFormBuilder}
     */
    boolean(name, defaultValue = false) {
        return this.register(
            name,
            new ObservableBoolean(Boolean(defaultValue))
        );
    }

    /**
     * @param {string | import("@minecraft/server-ui").UIRawMessage | ObservableString | ObservableUIRawMessage} label
     * @param {(player: Player) => void} onClick
     * @param {import("@minecraft/server-ui").ButtonOptions} [options]
     * @returns {CustomFormBuilder}
     */
    button(label, onClick, options) {
        this.elements.push(form => {
            form.button(
                label,
                () => {
                    onClick(this.player);
                },
                options
            );
        });

        return this;
    }

    /**
     * @param {string | ObservableString} src
     * @param {string | ObservableString} pack
     * @param {import("@minecraft/server-ui").ImageOptions} [options]
     * @returns {CustomFormBuilder}
     */
    image(src, pack, options) {
        this.elements.push(form => {
            form.image(src, pack, options);
        });

        return this;
    }

    /**
     * @param {Array<{
     *   label: string | import("@minecraft/server-ui").UIRawMessage | ObservableString | ObservableUIRawMessage,
     *   onClick: (player: Player) => void,
     *   options?: import("@minecraft/server-ui").ButtonOptions
     * }>} buttons
     * @param {import("@minecraft/server-ui").MultiButtonRowOptions} [options]
     * @returns {CustomFormBuilder}
     */
    multiButtonRow(buttons, options) {
        this.elements.push(form => {
            form.multiButtonRow(
                buttons.map(button => ({
                    label: button.label,
                    onClick: () => {
                        button.onClick(this.player);
                    },
                    options: button.options,
                })),
                options
            );
        });

        return this;
    }

    /**
     * @returns {CustomFormBuilder}
     */
    closeButton() {
        this.elements.push(form => {
            form.closeButton();
        });

        return this;
    }

    /**
     * @returns {boolean}
     */
    isShowing() {
        return this.form?.isShowing() ?? false;
    }

    /**
     * @returns {CustomFormBuilder}
     */
    close() {
        this.form?.close();
        return this;
    }

    /**
     * @returns {Promise<import("@minecraft/server-ui").DataDrivenScreenClosedReason>}
     */
    async show() {
        const form = new CustomForm(this.player, this.title);
        this.form = form;

        for (const element of this.elements) {
            element(form);
        }

        return await form.show();
    }
}
