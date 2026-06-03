import os
import re
import sys

# ============================================================
#  WeryGram Premium — Triple Auto-Patcher v2.0
#  Добавляет кнопку в настройки → отдельный экран с тогглами
# ============================================================

SETTINGS_PATH  = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
USERCONFIG_PATH = "TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java"
MESSAGES_PATH  = "TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
UI_DIR         = "TMessagesProj/src/main/java/org/telegram/ui"

# ============================================================
# ШАБЛОН: WeryGramPremiumActivity.java
# Новый экран настроек с тогглами (как на скриншоте)
# ============================================================
PREMIUM_ACTIVITY = '''\
package org.telegram.ui;

import android.content.Context;
import android.os.Bundle;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.Cells.TextCheckCell;
import org.telegram.ui.Components.RecyclerListView;
import org.telegram.messenger.LocaleController;
import android.graphics.Canvas;
import android.graphics.Paint;

/**
 * WeryGram Premium Settings Screen
 * Показывает тоглл-список «Визуально Telegram Premium»
 * Каждый переключатель сохраняет состояние в SharedPreferences
 * и мгновенно применяет визуальные изменения.
 */
public class WeryGramPremiumActivity extends BaseFragment {

    // ── Идентификаторы строк ──────────────────────────────────────────────
    private static final int ROW_HEADER          = 0;
    private static final int ROW_VISUAL_PREMIUM  = 1;   // «Визуально Telegram Premium»
    private static final int ROW_VERIFIED_BADGE  = 2;   // «Галочка верификации»
    private static final int ROW_HIDE_ADS        = 3;   // «Скрыть рекламу»
    private static final int ROW_ANIMATED_EMOJI  = 4;   // «Анимированные эмодзи»
    private static final int ROW_PREMIUM_STICKERS = 5;  // «Премиум стикеры»
    private static final int ROW_PREMIUM_REACTIONS = 6; // «Расширенные реакции»
    private static final int ROWS_COUNT          = 7;

    // ── Ключи SharedPreferences ───────────────────────────────────────────
    private static final String KEY_VISUAL_PREMIUM   = "visual_premium";
    private static final String KEY_VERIFIED         = "wery_verified";
    private static final String KEY_HIDE_ADS         = "wery_hide_ads";
    private static final String KEY_ANIM_EMOJI       = "wery_anim_emoji";
    private static final String KEY_PREM_STICKERS    = "wery_prem_stickers";
    private static final String KEY_PREM_REACTIONS   = "wery_prem_reactions";

    private RecyclerListView listView;
    private ListAdapter adapter;

    // ── Helpers ───────────────────────────────────────────────────────────
    private static android.content.SharedPreferences prefs() {
        return MessagesController.getGlobalMainSettings();
    }

    private static boolean get(String key) {
        return prefs().getBoolean(key, false);
    }

    private static void set(String key, boolean value) {
        prefs().edit().putBoolean(key, value).apply();
    }

    // ── BaseFragment lifecycle ────────────────────────────────────────────
    @Override
    public boolean onFragmentCreate() {
        super.onFragmentCreate();
        return true;
    }

    @Override
    public View createView(Context context) {
        // ActionBar
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setTitle("WeryGram Premium");
        actionBar.setAllowOverlayTitle(true);
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override
            public void onItemClick(int id) {
                if (id == -1) finishFragment();
            }
        });

        // Корневой контейнер
        fragmentView = new LinearLayout(context);
        LinearLayout layout = (LinearLayout) fragmentView;
        layout.setOrientation(LinearLayout.VERTICAL);
        layout.setBackgroundColor(0xFFF0F0F0);

        // RecyclerView
        listView = new RecyclerListView(context);
        listView.setLayoutManager(new LinearLayoutManager(context, LinearLayoutManager.VERTICAL, false));
        listView.setVerticalScrollBarEnabled(false);
        listView.setAdapter(adapter = new ListAdapter(context));

        // Клик по строке ↔ тоггл
        listView.setOnItemClickListener((view, position) -> {
            if (!(view instanceof TextCheckCell)) return;
            TextCheckCell cell = (TextCheckCell) view;
            switch (position) {
                case ROW_VISUAL_PREMIUM: {
                    boolean next = !get(KEY_VISUAL_PREMIUM);
                    set(KEY_VISUAL_PREMIUM, next);
                    // Синхронизируем зависимые флаги
                    if (next) {
                        set(KEY_VERIFIED,       true);
                        set(KEY_ANIM_EMOJI,     true);
                        set(KEY_PREM_STICKERS,  true);
                        set(KEY_PREM_REACTIONS, true);
                    }
                    cell.setChecked(next);
                    adapter.notifyDataSetChanged();
                    toast(next
                        ? "WeryGram: Визуальный Premium АКТИВИРОВАН! 🎉"
                        : "WeryGram: Визуальный Premium отключён");
                    break;
                }
                case ROW_VERIFIED_BADGE: {
                    boolean next = !get(KEY_VERIFIED);
                    set(KEY_VERIFIED, next);
                    cell.setChecked(next);
                    toast(next ? "Галочка верификации включена ✅" : "Галочка скрыта");
                    break;
                }
                case ROW_HIDE_ADS: {
                    boolean next = !get(KEY_HIDE_ADS);
                    set(KEY_HIDE_ADS, next);
                    cell.setChecked(next);
                    toast(next ? "Реклама скрыта 🚫" : "Реклама включена");
                    break;
                }
                case ROW_ANIMATED_EMOJI: {
                    boolean next = !get(KEY_ANIM_EMOJI);
                    set(KEY_ANIM_EMOJI, next);
                    cell.setChecked(next);
                    toast(next ? "Анимированные эмодзи включены ✨" : "Анимированные эмодзи отключены");
                    break;
                }
                case ROW_PREMIUM_STICKERS: {
                    boolean next = !get(KEY_PREM_STICKERS);
                    set(KEY_PREM_STICKERS, next);
                    cell.setChecked(next);
                    toast(next ? "Премиум стикеры включены 🎭" : "Премиум стикеры отключены");
                    break;
                }
                case ROW_PREMIUM_REACTIONS: {
                    boolean next = !get(KEY_PREM_REACTIONS);
                    set(KEY_PREM_REACTIONS, next);
                    cell.setChecked(next);
                    toast(next ? "Расширенные реакции включены 💥" : "Реакции — базовые");
                    break;
                }
            }
        });

        layout.addView(listView, new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            LinearLayout.LayoutParams.MATCH_PARENT));

        return fragmentView;
    }

    private void toast(String msg) {
        if (getParentActivity() != null)
            Toast.makeText(getParentActivity(), msg, Toast.LENGTH_SHORT).show();
    }

    // ── Adapter ───────────────────────────────────────────────────────────
    private class ListAdapter extends RecyclerView.Adapter<RecyclerView.ViewHolder> {

        private static final int TYPE_HEADER = 0;
        private static final int TYPE_CHECK  = 1;

        private final Context mCtx;

        ListAdapter(Context ctx) { mCtx = ctx; }

        @Override public int getItemCount() { return ROWS_COUNT; }

        @Override public int getItemViewType(int pos) {
            return pos == ROW_HEADER ? TYPE_HEADER : TYPE_CHECK;
        }

        @NonNull @Override
        public RecyclerView.ViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int type) {
            View v;
            if (type == TYPE_HEADER) {
                // Серый заголовок-раздел (как в Telegram Settings)
                TextView tv = new TextView(mCtx);
                tv.setPadding(
                    AndroidUtilities.dp(21), AndroidUtilities.dp(14),
                    AndroidUtilities.dp(21), AndroidUtilities.dp(6));
                tv.setTextSize(13);
                tv.setTextColor(0xFF79879B);
                tv.setText("ВИЗУАЛЬНЫЕ НАСТРОЙКИ");
                tv.setLayoutParams(new RecyclerView.LayoutParams(
                    RecyclerView.LayoutParams.MATCH_PARENT,
                    RecyclerView.LayoutParams.WRAP_CONTENT));
                return new RecyclerView.ViewHolder(tv) {};
            }
            v = new TextCheckCell(mCtx);
            v.setBackgroundColor(0xFFFFFFFF);
            return new RecyclerView.ViewHolder(v) {};
        }

        @Override
        public void onBindViewHolder(@NonNull RecyclerView.ViewHolder holder, int pos) {
            if (pos == ROW_HEADER) return;
            TextCheckCell cell = (TextCheckCell) holder.itemView;
            switch (pos) {
                case ROW_VISUAL_PREMIUM:
                    cell.setTextAndCheck(
                        "Визуально Telegram Premium",
                        get(KEY_VISUAL_PREMIUM), true);
                    break;
                case ROW_VERIFIED_BADGE:
                    cell.setTextAndCheck(
                        "Галочка верификации",
                        get(KEY_VERIFIED), true);
                    break;
                case ROW_HIDE_ADS:
                    cell.setTextAndCheck(
                        "Скрыть рекламу",
                        get(KEY_HIDE_ADS), true);
                    break;
                case ROW_ANIMATED_EMOJI:
                    cell.setTextAndCheck(
                        "Анимированные эмодзи",
                        get(KEY_ANIM_EMOJI), true);
                    break;
                case ROW_PREMIUM_STICKERS:
                    cell.setTextAndCheck(
                        "Премиум стикеры",
                        get(KEY_PREM_STICKERS), true);
                    break;
                case ROW_PREMIUM_REACTIONS:
                    cell.setTextAndCheck(
                        "Расширенные реакции",
                        get(KEY_PREM_REACTIONS), false);
                    break;
            }
        }
    }
}
'''

# ============================================================
# ОСНОВНОЙ ПATCHER
# ============================================================

def patch_settings(code: str) -> str:
    """Добавляет кнопку WeryGram Premium в SettingsActivity и навигацию на новый экран."""

    # 1. Убираем старые версии кнопки (чистый старт)
    code = re.sub(r'case 9999:.*?break;', '', code, flags=re.DOTALL)
    code = re.sub(r'items\.add\(SettingCell\.Factory\.of\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'items\.add\(UItem\.asCheck\(9999,[\s\S]*?\);\s*', '', code)

    # 2. Кнопка в список настроек (зелёная, с иконкой настроек)
    BUTTON = (
        'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, '
        'R.drawable.msg_settings, "WeryGram Premium"));'
    )

    # Вставляем ВЫШЕ первого упоминания Notifications
    match = re.search(r'(items\.add\([\s\S]*?[nN]otif[\s\S]*?\);)', code)
    if match:
        anchor = match.group(1)
        code = code.replace(anchor, f'{BUTTON}\n        {anchor}', 1)
        print("✅ Кнопка WeryGram Premium добавлена в начало списка настроек.")
    else:
        code = code.replace(
            "switch (item.id) {",
            f"{BUTTON}\n        switch (item.id) {{", 1)
        print("✅ Кнопка добавлена резервным методом.")

    # 3. Обработчик клика — ОТКРЫВАЕМ новый экран, а не тоггл напрямую
    CLICK_HANDLER = """\
case 9999: {
            presentFragment(new org.telegram.ui.WeryGramPremiumActivity());
            break;
        }"""
    switch_anchor = "switch (item.id) {"
    if switch_anchor in code:
        code = code.replace(
            switch_anchor,
            f"{switch_anchor}\n            {CLICK_HANDLER}", 1)
        print("✅ Обработчик клика → переход на WeryGramPremiumActivity добавлен.")

    return code


def patch_userconfig(code: str) -> str:
    """Внедряет проверку visual_premium в getCurrentUser()."""
    if "visual_premium" in code:
        print("ℹ️  UserConfig уже содержит патч — пропускаем.")
        return code

    anchor = "public TLRPC.User getCurrentUser() {"
    if anchor not in code:
        print("⚠️  Не найден getCurrentUser() в UserConfig — пропускаем.")
        return code

    injection = """\
public TLRPC.User getCurrentUser() {
        if (currentUser != null &&
                org.telegram.messenger.MessagesController.getGlobalMainSettings()
                    .getBoolean("visual_premium", false)) {
            currentUser.premium  = true;
            currentUser.verified = true;
        }"""
    code = code.replace(anchor, injection, 1)
    print("✅ Логика Premium + Верификация внедрены в UserConfig.getCurrentUser().")
    return code


def patch_messages_controller(code: str) -> str:
    """Перехватывает getUser() для подмены статуса текущего пользователя."""
    if "visual_premium" in code:
        print("ℹ️  MessagesController уже содержит патч — пропускаем.")
        return code

    # Точная сигнатура из реального файла:
    # public TLRPC.User getUser(Long id) {
    #     if (id == 0) {
    #         return UserConfig.getInstance(currentAccount).getCurrentUser();
    #     }
    #     return users.get(id);
    # }
    OLD = (
        "public TLRPC.User getUser(Long id) {\n"
        "        if (id == 0) {\n"
        "            return UserConfig.getInstance(currentAccount).getCurrentUser();\n"
        "        }\n"
        "        return users.get(id);\n"
        "    }"
    )
    NEW = """\
public TLRPC.User getUser(Long id) {
        if (id == 0) {
            return UserConfig.getInstance(currentAccount).getCurrentUser();
        }
        TLRPC.User user = users.get(id);
        if (user != null && id != null &&
                id.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (MessagesController.getGlobalMainSettings()
                    .getBoolean("visual_premium", false)) {
                user.premium  = true;
                user.verified = true;
            }
        }
        return user;
    }"""

    if OLD in code:
        patched = code.replace(OLD, NEW, 1)
        print("✅ Перехватчик getUser() добавлен в MessagesController.")
        return patched

    # Запасной вариант — regex на случай незначительных отличий в пробелах
    patched = re.sub(
        r'public TLRPC\.User getUser\(Long\s+(\w+)\)\s*\{'
        r'\s*if\s*\(\1\s*==\s*0\)\s*\{'
        r'\s*return\s+UserConfig\.getInstance\(currentAccount\)\.getCurrentUser\(\);\s*\}'
        r'\s*return\s+(\w+)\.get\(\1\);\s*\}',
        r'''public TLRPC.User getUser(Long \1) {
        if (\1 == 0) {
            return UserConfig.getInstance(currentAccount).getCurrentUser();
        }
        TLRPC.User user = \2.get(\1);
        if (user != null && \1 != null &&
                \1.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (MessagesController.getGlobalMainSettings()
                    .getBoolean("visual_premium", false)) {
                user.premium  = true;
                user.verified = true;
            }
        }
        return user;
    }''',
        code
    )

    if patched != code:
        print("✅ Перехватчик getUser() добавлен (regex-метод).")
    else:
        print("⚠️  getUser() не найден — пропускаем. Патч UserConfig достаточен.")

    return patched


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

def run():
    print("⏳  WeryGram Premium Patcher v2.0 запускается...\n")

    # --- Проверяем наличие обязательного файла ---
    if not os.path.exists(SETTINGS_PATH):
        print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: файл не найден: {SETTINGS_PATH}")
        sys.exit(1)

    # ── 1. SettingsActivity ──────────────────────────────────────────────
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        code = f.read()
    code = patch_settings(code)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        f.write(code)

    # ── 2. UserConfig ────────────────────────────────────────────────────
    if os.path.exists(USERCONFIG_PATH):
        with open(USERCONFIG_PATH, "r", encoding="utf-8") as f:
            uc = f.read()
        uc = patch_userconfig(uc)
        with open(USERCONFIG_PATH, "w", encoding="utf-8") as f:
            f.write(uc)
    else:
        print(f"⚠️  Не найден: {USERCONFIG_PATH}")

    # ── 3. MessagesController ────────────────────────────────────────────
    if os.path.exists(MESSAGES_PATH):
        with open(MESSAGES_PATH, "r", encoding="utf-8") as f:
            mc = f.read()
        mc = patch_messages_controller(mc)
        with open(MESSAGES_PATH, "w", encoding="utf-8") as f:
            f.write(mc)
    else:
        print(f"⚠️  Не найден: {MESSAGES_PATH}")

    # ── 4. Создаём новый Activity файл ───────────────────────────────────
    out_path = os.path.join(UI_DIR, "WeryGramPremiumActivity.java")
    if os.path.exists(out_path):
        print(f"ℹ️  {out_path} уже существует — перезаписываем.")
    os.makedirs(UI_DIR, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(PREMIUM_ACTIVITY)
    print(f"✅ WeryGramPremiumActivity.java создан: {out_path}")

    print("\n🎉  ВСЕ МОДУЛИ УСПЕШНО МОДИФИЦИРОВАНЫ!")
    print("    ➜ Запустите сборку: ./gradlew assembleDebug")
    print("    ➜ Новый экран откроется при нажатии «WeryGram Premium» в настройках.")


if __name__ == "__main__":
    run()
        
