import requests
from bs4 import BeautifulSoup

def keepable_tag(tag):
    """
    بررسی می‌کند آیا تگ به‌تنهایی شرایط نگه‌داری دارد یا خیر:
      1) تگ script با type="text/css"
      2) تگی که کلاس آن شامل 'col' و 'col-12' باشد
    """
    # اگر تگ script است و نوع آن text/css باشد
    if tag.name == "script" and tag.get("type") == "text/css":
        return True

    # اگر کلاس تگ شامل col و col-12 باشد
    classes = tag.get("class") or []
    if "col" in classes and "col-12" in classes:
        return True

    return False

def is_subtree_keepable(tag):
    """
    بررسی می‌کند آیا این تگ یا هر یک از فرزندانش (به صورت بازگشتی)
    نگه‌داشتنی هستند یا خیر.
    اگر تگ یا یکی از فرزندانش نگه‌داشتنی باشد، نتیجه True است.
    """
    if keepable_tag(tag):
        return True

    for child in tag.children:
        if child.name and is_subtree_keepable(child):
            return True
    return False

def remove_unkeepable(tag):
    """
    به شکل بازگشتی (Post-order) روی درخت HTML حرکت می‌کند و تگ‌هایی را حذف می‌کند که:
      - خودش نگه‌داشتنی نیست
      - و هیچ فرزند نگه‌داشتنی هم ندارد.

    اما اگر:
      - تگ، خود تگ <head> باشد، کاری با آن (و فرزندانش) نداریم.
      - تگ نگه‌داشتنی باشد، کل زیرشاخه‌اش را حفظ می‌کنیم.
    """
    # اگر تگ head باشد، هیچ حذفی انجام نمی‌دهیم تا همهٔ فرزندان head حفظ شوند
    if tag.name == "head":
        return

    # اگر خود تگ نگه‌داشتنی باشد، کل زیرشاخه را نگه می‌داریم
    if keepable_tag(tag):
        return

    # در غیر این صورت، باید فرزندان را بررسی و حذف کنیم
    for child in list(tag.children):
        if child.name:
            remove_unkeepable(child)

    # اگر پس از حذف فرزندان غیرضروری، این تگ و باقیمانده‌اش نگه‌داشتنی نباشند، حذف می‌کنیم
    if not is_subtree_keepable(tag):
        tag.decompose()

def extract_content(url):
    """
    محتوای صفحه را می‌گیرد، تگ‌ها را بر اساس منطق بالا فیلتر می‌کند
    (با حفظ <head> و ساختار والدین در صورت وجود فرزندان نگه‌داشتنی)
    سپس تگ‌هایی که کلاس 'footer-container container' دارند را حذف می‌کند،
    در نهایت کل صفحه را راست‌چین (rtl) کرده و خروجی را برمی‌گرداند.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"خطا در دریافت صفحه: {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # مرحله 1) حذف تگ‌های ناخواسته (به جز <head>)
    remove_unkeepable(soup)
    
    # مرحله 2) حذف تگ‌هایی که کلاس 'footer-container' و 'container' را با هم دارند
    footers = soup.find_all(
        lambda t: t.get('class') 
                  and 'footer-container' in t.get('class') 
                  and 'container' in t.get('class')
    )
    for f in footers:
        f.decompose()
    
    # مرحله 3) راست‌چین کردن کل صفحه
    if soup.html:
        soup.html['dir'] = 'rtl'
    else:
        if soup.body:
            soup.body['dir'] = 'rtl'

    # مرحله 4) خروجی نهایی را از تگ بدنه به صورت prettify برمی‌گردانیم
    body = soup.find('body')
    return body.prettify() if body else soup.prettify()

def convert_to_html(content, output_path):
    """
    محتوای استخراج‌شده را در یک فایل HTML ذخیره می‌کند.
    """
    if content:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"فایل HTML ذخیره شد: {output_path}")
    else:
        print(f"خطا: محتوایی برای تبدیل به HTML یافت نشد: {output_path}")


# ----------------------------- نمونه‌ی استفاده -----------------------------

print("==========START!===========")

# لینک صفحه وب که حاوی لیست جلسات تفسیر است
page_url = 'https://javadi.esra.ir/%D8%A2%D8%B1%D8%B4%DB%8C%D9%88-%D8%AF%D8%B1%D9%88%D8%B3-%D8%AA%D9%81%D8%B3%DB%8C%D8%B1/-/categories/2087759?p_r_p_resetCur=true&p_r_p_categoryId=2087759'
response = requests.get(page_url)
if response.status_code != 200:
    print(f"خطا در دریافت صفحه: {page_url}")
    exit()

soup = BeautifulSoup(response.content, 'html.parser')
li_elements = soup.find_all('li')

def extract_links():
    links = []
    for li in li_elements:
        span = li.find('span')
        anchor = li.find('a')
        # بررسی اینکه آیا span متن "تفسیر سوره بقره جلسه" را دارد
        if span and 'تفسیر سوره بقره جلسه' in span.text:
            if anchor and anchor.has_attr('href'):
                links.append(anchor['href'])
    return links

all_links = extract_links()
for i, url in enumerate(all_links):
    content = extract_content(url)
    output_file = f"tafseer_baqara_session_{i + 1}.html"
    convert_to_html(content, output_file)

print("==========DONE!===========")
