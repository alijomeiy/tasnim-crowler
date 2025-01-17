import requests
from bs4 import BeautifulSoup

def keepable_tag(tag):
    """
    تشخیص اینکه آیا تگ باید نگه داشته شود یا خیر.
    """
    # نگه‌داشتن تگ head
    if tag.name == "head":
        return True
    
    # نگه‌داشتن تگ‌های script با نوع text/css
    if tag.name == "script" and tag.get("type") == "text/css":
        return True

    # اگر کلاس تگ شامل col و col-12 باشد
    classes = tag.get("class") or []
    if "col" in classes and "col-12" in classes:
        return True

    return False


def is_subtree_keepable(tag):
    """
    بررسی می‌کند که آیا تگ جاری یا فرزندانش باید نگه داشته شوند یا خیر.
    اگر تگ جاری یا هر فرزندش keepable باشد، نتیجه True خواهد بود.
    """
    if keepable_tag(tag):
        return True

    for child in tag.children:
        if child.name and is_subtree_keepable(child):
            return True
    return False


def remove_unkeepable(tag):
    """
    به صورت بازگشتی تگ‌هایی را که نباید نگه داشته شوند، حذف می‌کند
    مگر آنکه در زیرشاخه‌هایشان تگی باشد که باید نگه داشته شود.
    """
    # اگر تگ جاری قابل نگه‌داری است، نیازی به حذف کردنش نداریم
    if keepable_tag(tag):
        return

    # برای هر فرزند، همین فرایند را تکرار می‌کنیم
    for child in list(tag.children):
        if child.name:
            remove_unkeepable(child)

    # اگر زیرشاخه‌ای هم قابل نگه‌داری نبود، تگ جاری را حذف کن
    if not is_subtree_keepable(tag):
        tag.decompose()


def extract_content(url):
    """
    محتوای صفحه را از آدرس داده‌شده دریافت کرده،
    تگ‌ها و بخش‌های غیرضروری را حذف و در نهایت استایل فونت Vazir-Medium.ttf را تزریق می‌کند.
    """
    response = requests.get(url)
    if response.status_code != 200:
        print(f"خطا در دریافت صفحه: {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # حذف تگ‌های ناخواسته
    remove_unkeepable(soup)
    
    # حذف تگ‌هایی که کلاس 'footer-container' و 'container' را با هم دارند
    footers = soup.find_all(
        lambda t: t.get('class')
                  and 'footer-container' in t.get('class')
                  and 'container' in t.get('class')
    )
    for f in footers:
        f.decompose()
    
    # تنظیم جهت متن بر روی راست به چپ (در صورت وجود body)
    if soup.body:
        soup.body['dir'] = 'rtl'

    # ـــــــــــــــــــــــــــــــــــــــــــــــــــــــ
    # تزریق @font-face برای استفاده از فایل فونت Vazir-Medium.ttf
    # ـــــــــــــــــــــــــــــــــــــــــــــــــــــــ

    # 1) اطمینان از وجود تگ <head>
    head_tag = soup.find("head")
    if not head_tag:
        head_tag = soup.new_tag("head")
        # اگر <html> داریم، head را در ابتدای آن می‌گذاریم
        if soup.html:
            soup.html.insert(0, head_tag)
        else:
            # در صورت نبود <html>، آن را می‌سازیم
            html_tag = soup.new_tag("html")
            html_tag.append(head_tag)
            # محتوای اصلی را به تگ html منتقل می‌کنیم
            for child in list(soup.contents):
                html_tag.append(child)
            # و در نهایت html_tag را به soup اضافه می‌کنیم
            soup.append(html_tag)

    # 2) ساخت تگ <style> و تنظیمات فونت
    # نکته مهم: برای override کردن !important در CSS خارجی، اینجا هم !important می‌گذاریم
    style_tag = soup.new_tag("style")
    style_tag.string = """
@font-face {
    font-family: 'Vazir';
    src: url('Vazir-Medium.ttf') format('truetype');
}

/* برای اعمال روی کلیه تگ‌ها و نیز override کردن مقدار قبلی: */
body, p, h1, h2, h3, h4, h5, h6, span, a, strong, em, i, b, u, div, section, article, * {
    font-family: 'Vazir' !important;
}
"""

    head_tag.append(style_tag)

    # در نهایت خروجی HTML را برمی‌گردانیم
    return soup.prettify()


def convert_to_html(content, output_path):
    """
    محتوای HTML را در فایل مشخص‌شده ذخیره می‌کند.
    """
    if content:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"فایل HTML ذخیره شد: {output_path}")
    else:
        print(f"خطا: محتوایی برای تبدیل به HTML یافت نشد: {output_path}")


# ----------------------------- نمونه‌ی استفاده -----------------------------
if __name__ == "__main__":
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
