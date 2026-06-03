import os
import re
import sys

def patch_clean_telegram():
    settings_path = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
    
    if not os.path.exists(settings_path):
        print(f"🚨 КРИТИЧЕСКАЯ ОШИБКА: Файл не найден: {settings_path}")
        sys.exit(1)

    print("⏳ Авто-патчер WeryGram начал работу...")

    with open(settings_path, "r", encoding="utf-8") as f:
        code = f.read()

    # 0. ОЧИСТКА: Вычищаем старые следы мода, чтобы не было накладок
    code = re.sub(r'case 9999:.*?break;', '', code, flags=re.DOTALL)
    werygram_btn = 'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.msg_settings, "WeryGram"));'
    code = code.replace(werygram_btn, "")
    code = code.replace('items.add(UItem.asAction(9999, R.drawable.msg_settings, "WeryGram"));', "")

    is_button_ok = False
    is_click_ok = False

    # 1. УМНЫЙ ПОИСК ЯКОРЯ ДЛЯ КНОПКИ (Ищет сквозь переносы строк)
    match_chat = re.search(r'(items\.add\([\s\S]*?[cC]hat[sS]ettings[\s\S]*?\);)', code)
    match_privacy = re.search(r'(items\.add\([\s\S]*?[pP]rivacy[\s\S]*?\);)', code)
    match_notifications = re.search(r'(items\.add\([\s\S]*?[nN]otif[\s\S]*?\);)', code)

    if match_chat:
        anchor = match_chat.group(1)
        code = code.replace(anchor, f'{anchor}\n        {werygram_btn}')
        is_button_ok = True
        print("✅ Кнопка WeryGram успешно добавлена под 'Настройки чатов'!")
    elif match_privacy:
        anchor = match_privacy.group(1)
        code = code.replace(anchor, f'{anchor}\n        {werygram_btn}')
        is_button_ok = True
        print("✅ Кнопка WeryGram успешно добавлена под 'Конфиденциальность'!")
    elif match_notifications:
        anchor = match_notifications.group(1)
        code = code.replace(anchor, f'{anchor}\n        {werygram_btn}')
        is_button_ok = True
        print("✅ Кнопка WeryGram успешно добавлена под 'Уведомления'!")
    else:
        print("🚨 ОШИБКА: Не удалось найти ни один стандартный раздел (ChatSettings, Privacy, Notifications) для вставки кнопки!")

    # 2. ВНЕДРЕНИЕ ДИАЛОГОВОГО ОКНА (ОБРАБОТЧИК КЛИКА)
    switch_anchor = "switch (item.id) {"
    if switch_anchor in code:
        dialog_code = """case 9999:
            if (SettingsActivity.this.getParentActivity() != null) {
                android.app.AlertDialog.Builder builder = new android.app.AlertDialog.Builder(SettingsActivity.this.getParentActivity());
                
                boolean isEnabled = SettingsActivity.this.getParentActivity().getSharedPreferences("werygram_settings", android.content.Context.MODE_PRIVATE).getBoolean("visual_premium", false);
                builder.setTitle("WeryGram Premium (" + (isEnabled ? "Включен" : "Выключен") + ")");
                
                builder.setMessage("Premium данная функция включает телеграм премиум визуально");
                
                builder.setPositiveButton("Включить", new android.content.DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(android.content.DialogInterface dialog, int which) {
                        SettingsActivity.this.getParentActivity().getSharedPreferences("werygram_settings", android.content.Context.MODE_PRIVATE).edit().putBoolean("visual_premium", true).apply();
                        android.widget.Toast.makeText(SettingsActivity.this.getParentActivity(), "Визуальный Premium успешно ВКЛЮЧЕН! Перезапустите приложение.", android.widget.Toast.LENGTH_SHORT).show();
                    }
                });
                
                builder.setNegativeButton("Выключить", new android.content.DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(android.content.DialogInterface dialog, int which) {
                        SettingsActivity.this.getParentActivity().getSharedPreferences("werygram_settings", android.content.Context.MODE_PRIVATE).edit().putBoolean("visual_premium", false).apply();
                        android.widget.Toast.makeText(SettingsActivity.this.getParentActivity(), "Визуальный Premium ВЫКЛЮЧЕН!", android.widget.Toast.LENGTH_SHORT).show();
                    }
                });
                
                builder.show();
            }
            break;"""
        
        code = code.replace(switch_anchor, f"{switch_anchor}\n            {dialog_code}")
        is_click_ok = True
        print("✅ Интерактивное диалоговое окно успешно вшито в обработчик кликов!")

    # Финальная проверка работоспособности патча
    if not is_button_ok or not is_click_ok:
        print("🚨 Критическая ошибка: Патч применен не полностью. Сборка остановлена.")
        sys.exit(1)

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(code)

    print("\n🎉 ВСЁ ГОТОВО! Логика успешно обновлена.")

if __name__ == "__main__":
    patch_clean_telegram()
