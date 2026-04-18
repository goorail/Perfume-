import re

po_path = r'locale\ar\LC_MESSAGES\django.po'
with open(po_path, 'r', encoding='utf-8') as f:
    content = f.read()

translations = {
    'msgid "You can only review products you have purchased and received."\nmsgstr ""': 
    'msgid "You can only review products you have purchased and received."\nmsgstr "يمكنك فقط تقييم المنتجات التي قمت بشرائها واستلامها."',

    'msgid "You can only refund orders that are Paid, Shipped, or Delivered."\nmsgstr ""':
    'msgid "You can only refund orders that are Paid, Shipped, or Delivered."\nmsgstr "يمكنك فقط استرجاع الطلبات التي تم دفعها، شحنها، أو توصيلها."',
    
    'msgid "User matching this token does not exist."\nmsgstr ""':
    'msgid "User matching this token does not exist."\nmsgstr "المستخدم المطابق لهذا الرمز غير موجود."',
    
    'msgid "Orders merged. No guest cart to merge."\nmsgstr ""':
    'msgid "Orders merged. No guest cart to merge."\nmsgstr "تم دمج الطلبات. لا توجد سلة ضيف لدمجها."',
    
    'msgid "Device ID is required for guest checkout."\nmsgstr ""':
    'msgid "Device ID is required for guest checkout."\nmsgstr "معرف الجهاز مطلوب لاتمام طلب الضيف."',
    
    'msgid "Device ID is required to fetch guest orders."\nmsgstr ""':
    'msgid "Device ID is required to fetch guest orders."\nmsgstr "معرف الجهاز مطلوب لجلب طلبات الضيف."',
    
    'msgid "No products found"\nmsgstr ""':
    'msgid "No products found"\nmsgstr "لا توجد منتجات"',
}

# Also handle fuzzy entries by removing "#, fuzzy\n" and fixing msgstr if it has bad placeholder.
# I will use a simple pass.

new_content = content
for k, v in translations.items():
    new_content = new_content.replace(k, v)

# Specifically for the ones that might have fuzzy matched old translations:
# For "No products found"
new_content = re.sub(
    r'#, fuzzy\n#\| msgid "Product not found"\nmsgid "No products found"\nmsgstr ".*?"', 
    r'msgid "No products found"\nmsgstr "لا توجد منتجات"', 
    new_content, flags=re.DOTALL
)

# For "Orders merged. No guest cart to merge."
new_content = re.sub(
    r'#, fuzzy\n#\| msgid "No guest cart to merge"\nmsgid "Orders merged\. No guest cart to merge\."\nmsgstr ".*?"', 
    r'msgid "Orders merged. No guest cart to merge."\nmsgstr "تم دمج الطلبات. لا توجد سلة ضيف لدمجها."', 
    new_content, flags=re.DOTALL
)

# For "Device ID is required for guest checkout."
new_content = re.sub(
    r'#, fuzzy\n#\| msgid "No Device ID provided for guest cart\."\nmsgid "Device ID is required for guest checkout\."\nmsgstr ".*?"', 
    r'msgid "Device ID is required for guest checkout."\nmsgstr "معرف الجهاز مطلوب لاتمام طلب الضيف."', 
    new_content, flags=re.DOTALL
)

# For "Device ID is required to fetch guest orders."
new_content = re.sub(
    r'#, fuzzy\n#\| msgid "No Device ID provided for guest cart\."\nmsgid "Device ID is required to fetch guest orders\."\nmsgstr ".*?"', 
    r'msgid "Device ID is required to fetch guest orders."\nmsgstr "معرف الجهاز مطلوب لجلب طلبات الضيف."', 
    new_content, flags=re.DOTALL
)

with open(po_path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print("Updated PO file successfully")
