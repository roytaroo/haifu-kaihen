import {
    CustomForm,
    ObservableBoolean,
} from "@minecraft/server-ui";

import {
    world,
    system,
} from "@minecraft/server";

/*
 * ============================================================
 * 設定フォーム（ナビゲーター表示トグル）
 * ============================================================
 */

/**
 * @param {import("@minecraft/server").Player} player
 */
function showSettingsForm(player) {

    // tag "navi" があればON、なければOFFを初期値にする
    const navigatorEnabled = new ObservableBoolean(
        player.hasTag("navi"),
        {
            clientWritable: true,
        }
    );

    // トグルが変化したら即座にタグを付与する
    const navigatorSubscription = navigatorEnabled.subscribe((enabled) => {

        if (enabled) {
            player.addTag("navi_add");
        } else {
            player.addTag("navi_remove");
        }
    });

    const form = new CustomForm(
        player,
        "設定"
    );

    form.toggle(
        "ナビゲーター表示を有効化",
        navigatorEnabled,
        {
            description:
                "有効化することで、黄文字でナビゲーターがゲームの説明などをしてくれます。",
        }
    );

    form.closeButton();

    form.show()
        .then(() => {

            navigatorEnabled.unsubscribe(navigatorSubscription);
        })
        .catch(() => {

            navigatorEnabled.unsubscribe(navigatorSubscription);
        });
}

/*
 * ============================================================
 * 木の棒を使ったらフォーム表示（お好みでイベントを変更してください）
 * ============================================================
 */

world.afterEvents.itemUse.subscribe((event) => {

    const player = event.source;
    const item = event.itemStack;

    if (item.typeId !== "item:setting") {
        return;
    }

    system.run(() => {
        showSettingsForm(player);
    });
});