    private static void openTelegramGiftsDialog(int account, TLRPC.User target) {
        AndroidUtilities.runOnUIThread(() -> {
            try {
                BaseFragment lastFragment = LaunchActivity.getSafeLastFragment();
                if (lastFragment == null) {
                    toast("Ошибка: фрагмент не найден");
                    return;
                }
                Class<?> giftSheetClass = Class.forName("org.telegram.ui.Components.Premium.GiftPremiumBottomSheet");
                java.lang.reflect.Constructor<?> constructor = giftSheetClass.getDeclaredConstructor(
                    BaseFragment.class,
                    TLRPC.User.class
                );
                constructor.setAccessible(true);
                Object sheet = constructor.newInstance(lastFragment, target);
                java.lang.reflect.Method showMethod = sheet.getClass().getDeclaredMethod("show");
                showMethod.setAccessible(true);
                showMethod.invoke(sheet);
            } catch (Exception e) {
                FileLog.e("WeryGram: " + e);
                toast("Ошибка открытия меню подарков");
            }
        });
    }
