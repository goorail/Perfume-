import polib

po_path = r'locale\ar\LC_MESSAGES\django.po'
po = polib.pofile(po_path)

translations = {
    'You can only review products you have purchased and received.': 'يمكنك فقط تقييم المنتجات التي قمت بشرائها واستلامها.',
    'You can only refund orders that are Paid, Shipped, or Delivered.': 'يمكنك فقط استرجاع الطلبات التي تم دفعها، شحنها، أو توصيلها.',
    'User matching this token does not exist.': 'المستخدم المطابق لهذا الرمز غير موجود.',
    'Orders merged. No guest cart to merge.': 'تم دمج الطلبات. لا توجد سلة ضيف لدمجها.',
    'Device ID is required for guest checkout.': 'معرف الجهاز مطلوب لاتمام طلب الضيف.',
    'Device ID is required to fetch guest orders.': 'معرف الجهاز مطلوب لجلب طلبات الضيف.',
    'No products found': 'لا توجد منتجات',
}

for entry in po:
    if entry.msgid in translations:
        entry.msgstr = translations[entry.msgid]
        if 'fuzzy' in entry.flags:
            entry.flags.remove('fuzzy')

po.save()

print("Translations updated successfully.")
