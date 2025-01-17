import requests
from bs4 import BeautifulSoup
import re

print("==========START!===========")
# لینک صفحه وب که حاوی لیست جلسات تفسیر است
page_url = 'https://javadi.esra.ir/%D8%A2%D8%B1%D8%B4%DB%8C%D9%88-%D8%AF%D8%B1%D9%88%D8%B3-%D8%AA%D9%81%D8%B3%DB%8C%D8%B1/-/categories/2087759?p_r_p_resetCur=true&p_r_p_categoryId=2087759'  # لینک صفحه مورد نظر

# درخواست به صفحه وب و دریافت محتوای HTML
response = requests.get(page_url)
if response.status_code != 200:
    print(f"خطا در دریافت صفحه: {page_url}")
    exit()
soup = BeautifulSoup(response.content, 'html.parser')

# پیدا کردن لینک‌هایی که با عنوان "تفسیر سوره بقره جلسه ..." هستند

# جستجوی تمامی li های درون ul با id="list"
li_elements = soup.find_all('li')
# فهرست لینک‌هایی که متن مورد نظر را دارند

def extract_links():
    links = []
    for li in li_elements:
        span = li.find('span')
        anchor = li.find('a')
        
        # بررسی اینکه آیا span متن "تفسیر سوره بقره جلسه" را دارد
        if span and 'تفسیر سوره بقره جلسه' in span.text:
            # link = (anchor.text, anchor['href'])
            link = anchor['href']
            links.append(link)
    return links

# تابعی برای استخراج محتوای صفحه و حذف هدر، فوتر و دکمه‌ها
def extract_content(url):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"خطا در دریافت صفحه: {url}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    for tag in soup.find_all():
        # اگر تگ اسکریپت با type="text/css" باشد، آن را حذف نکن
        if tag.name == "script" and tag.get("type") == "text/css":
            continue
        
        # اگر تگ کلاس col col-12 دارد، آن را حذف نکن
        if "class" in tag.attrs:
            classes = tag.get("class", [])
            if "col" in classes and "col-12" in classes:
                continue
        
        # اگر هیچ‌کدام از شرایط بالا برقرار نباشد، تگ را حذف کن
        tag.decompose()

    # محتوای اصلی را استخراج کنید
    content = soup.find('body')  # می‌توانید انتخابگر خود را بر اساس ساختار صفحه تنظیم کنید
    return content.prettify() if content else None

# تبدیل محتوای استخراج شده به HTML و ذخیره در فایل
def convert_to_html(content, output_path):
    if content:
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f"فایل HTML ذخیره شد: {output_path}")
    else:
        print(f"خطا: محتوایی برای تبدیل به HTML یافت نشد: {output_path}")

# پردازش هر لینک و تبدیل به HTML
links = extract_links()
for i, url in enumerate(links):
    content = extract_content(url)
    output_file = f"tafseer_baqara_session_{i + 1}.html"
    convert_to_html(content, output_file)
