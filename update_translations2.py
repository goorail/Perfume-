import os

po_path = r'locale\ar\LC_MESSAGES\django.po'
with open(po_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Make it clean - just use string replace for each block.
# We will just replace 'msgid ...\nmsgstr ""' with the translated version.

replacements = [
    (
        'msgid "You can only review products you have purchased and received."\nmsgstr ""',
        'msgid "You can only review products you have purchased and received."\nmsgstr "يمكنك فقط تقييم المنتجات التي قمت بشرائها واستلامها."'
    ),
    (
        'msgid "You can only refund orders that are Paid, Shipped, or Delivered."\nmsgstr ""',
        'msgid "You can only refund orders that are Paid, Shipped, or Delivered."\nmsgstr "يمكنك فقط استرجاع الطلبات التي تم دفعها، شحنها، أو توصيلها."'
    ),
    (
        'msgid "User matching this token does not exist."\nmsgstr ""',
        'msgid "User matching this token does not exist."\nmsgstr "المستخدم المطابق لهذا الرمز غير موجود."'
    ),
    (
        '#, fuzzy\n#| msgid "No guest cart to merge"\nmsgid "Orders merged. No guest cart to merge."\nmsgstr "لا يوجد سلة ضيف لدمجها"\n',
        'msgid "Orders merged. No guest cart to merge."\nmsgstr "تم دمج الطلبات. لا توجد سلة ضيف لدمجها."\n'
    ),
    (
        '#, fuzzy\n#| msgid "No Device ID provided for guest cart."\nmsgid "Device ID is required for guest checkout."\nmsgstr "لم يتم توفير معرف الجهاز للسلة غير المسجلة."\n',
        'msgid "Device ID is required for guest checkout."\nmsgstr "معرف الجهاز مطلوب لاتمام طلب الضيف."\n'
    ),
    (
        '#, fuzzy\n#| msgid "No Device ID provided for guest cart."\nmsgid "Device ID is required to fetch guest orders."\nmsgstr "لم يتم توفير معرف الجهاز للسلة غير المسجلة."\n',
        'msgid "Device ID is required to fetch guest orders."\nmsgstr "معرف الجهاز مطلوب لجلب طلبات الضيف."\n'
    ),
    (
        '#, fuzzy\n#| msgid "Product not found"\nmsgid "No products found"\nmsgstr "المنتج غير موجود"\n',
        'msgid "No products found"\nmsgstr "لا توجد منتجات"\n'
    )
]

new_content = content
for old, new in replacements:
    new_content = new_content.replace(old, new)


# Try to handle case where the original msgstr is empty for fuzzy ones:
replacements_fuzzy_empty = [
    (
        '#, fuzzy\n#| msgid "No guest cart to merge"\nmsgid "Orders merged. No guest cart to merge."\nmsgstr ""\n',
        'msgid "Orders merged. No guest cart to merge."\nmsgstr "تم دمج الطلبات. لا توجد سلة ضيف لدمجها."\n'
    ),
    (
        '#, fuzzy\n#| msgid "No Device ID provided for guest cart."\nmsgid "Device ID is required for guest checkout."\nmsgstr ""\n',
        'msgid "Device ID is required for guest checkout."\nmsgstr "معرف الجهاز مطلوب لاتمام طلب الضيف."\n'
    ),
    (
        '#, fuzzy\n#| msgid "No Device ID provided for guest cart."\nmsgid "Device ID is required to fetch guest orders."\nmsgstr ""\n',
        'msgid "Device ID is required to fetch guest orders."\nmsgstr "معرف الجهاز مطلوب لجلب طلبات الضيف."\n'
    ),
    (
        '#, fuzzy\n#| msgid "Product not found"\nmsgid "No products found"\nmsgstr ""\n',
        'msgid "No products found"\nmsgstr "لا توجد منتجات"\n'
    )
]
for old, new in replacements_fuzzy_empty:
    new_content = new_content.replace(old, new)

with open(po_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Translations updated via python.")
