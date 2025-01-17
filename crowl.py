import requests
from bs4 import BeautifulSoup

def keepable_tag(tag):
    if tag.name == "head":
        return True
    
    if tag.name == "script" and tag.get("type") == "text/css":
        return True

    # اگر کلاس تگ شامل col و col-12 باشد
    classes = tag.get("class") or []
    if "col" in classes and "col-12" in classes:
        return True

    return False

def is_subtree_keepable(tag):
    if keepable_tag(tag):
        return True

    for child in tag.children:
        if child.name and is_subtree_keepable(child):
            return True
    return False

def remove_unkeepable(tag):
    if keepable_tag(tag):
        return

    for child in list(tag.children):
        if child.name:
            remove_unkeepable(child)

    if not is_subtree_keepable(tag):
        tag.decompose()

def extract_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"خطا در دریافت صفحه: {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    
    remove_unkeepable(soup)
    
    # مرحله 2) حذف تگ‌هایی که کلاس 'footer-container' و 'container' را با هم دارند
    footers = soup.find_all(
        lambda t: t.get('class') 
                  and 'footer-container' in t.get('class') 
                  and 'container' in t.get('class')
    )
    for f in footers:
        f.decompose()
    
    
    soup.body['dir'] = 'rtl'

    body = soup.find('body')
    return body.prettify() #if body else soup.prettify()

def convert_to_html(content, output_path):
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
