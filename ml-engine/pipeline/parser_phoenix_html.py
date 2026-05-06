# ไฟล์: 2_parse_html_split.py
import os
import json
import re
import shutil
from datetime import datetime
from bs4 import BeautifulSoup
from tqdm import tqdm

PREMIUM_KEYWORDS = [
    "Premium Set", "Special Set", "Complete Set", 
    "Short Story Set", "Box Set", "Short Story", "Combo Set", "Ultimate Set"
]

def extract_romaji_title(html_text):
    if not html_text: return "ไม่พบข้อมูล"
    all_brackets = re.findall(r'\((.*?)\)', html_text)
    if not all_brackets: return "ไม่พบวงเล็บ"
    
    potential_titles = []
    for text in all_brackets:
        text = text.strip()
        if len(text) < 4: continue
        if not re.search(r'[a-zA-Z]', text): continue
        forbidden_words = r'มังงะ|ไลท์โนเวล|พิมพ์ครั้ง|เล่ม|ฉบับ'
        if re.search(forbidden_words, text, re.IGNORECASE): continue
        potential_titles.append(text)

    if potential_titles:
        raw_title = potential_titles[0] 
        clean_title = re.sub(r'(?i)\s*vol\.?\s*[0-9\-]+$', '', raw_title)
        return clean_title.strip()
    return "ไม่พบข้อมูลภาษาอังกฤษ"

def process_title(raw_text):
    media_type = "Manga"
    if re.search(r'^\(LN\)', raw_text, re.IGNORECASE):
        media_type = "Light Novel"
    elif re.search(r'^\(มังงะ\)', raw_text, re.IGNORECASE):
        media_type = "Manga"
    
    clean_name = re.sub(r'^\(มังงะ\) |^\(LN\) ', '', raw_text)
    pattern = r"|".join(map(re.escape, PREMIUM_KEYWORDS))
    clean_name = re.sub(pattern, "", clean_name, flags=re.IGNORECASE)
    clean_name = re.sub(r"\s+", " ", clean_name).strip()

    return clean_name, media_type

def match_tile_vol(clean_name):
    title_match = re.search(r'(.*?)\s+\(จบในเล่ม\)', clean_name)
    if title_match:
        th_title = title_match.group(1).strip() if title_match else clean_name
        return th_title, 1, "1"

    title_match = re.search(r'(.*?)\s+เล่ม\s*(\d+)', clean_name)
    th_title = title_match.group(1).strip() if title_match else clean_name
    vol_match = re.search(r'เล่ม\s*(\d+)(?:[-\s]*(\d+))?', clean_name)

    if vol_match:
        v1 = vol_match.group(1)
        v2 = vol_match.group(2)
        th_vol = int(v2) if v2 else int(v1)
        raw_vol = f"{v1}-{v2}" if v2 else str(v1)
    else:
        th_vol = 1
        raw_vol = "1"

    return th_title, th_vol, raw_vol

def find_th_release_date(detail_soup):
    label_span = detail_soup.find('span', string=lambda text: text and "วันวางจำหน่าย" in text)
    if label_span:
        date_span = label_span.find_next_sibling('span')
        if date_span:
            raw_date_text = date_span.get_text(strip=True)
            clean_date_str = raw_date_text.replace(":", "").strip()
            try:
                dt_obj = datetime.strptime(clean_date_str, "%d-%m-%Y")
                return dt_obj.strftime("%Y-%m-%dT00:00:00Z")
            except ValueError:
                return None
    return None

def find_price(detail_soup):
    th_price = 0.0
    old_price_div = detail_soup.find('div', class_=re.compile(r'old-price'))

    if old_price_div:
        price_span = old_price_div.find('span', class_='price')
        if price_span:
            raw_price_text = price_span.get_text(strip=True)
            clean_price_str = re.sub(r'[^\d.]', '', raw_price_text)
            try:
                th_price = float(clean_price_str)
            except ValueError:
                pass

    if th_price == 0.0:
        price_meta = detail_soup.find('meta', itemprop='price')
        if price_meta and price_meta.has_attr('content'):
            try:
                th_price = float(price_meta['content'])
            except ValueError:
                pass
    return th_price

def process_description(detail_soup):
    en_title = "ไม่พบข้อมูลภาษาอังกฤษ"
    has_premium = 0
    premium_type = "None"
    description = detail_soup.find('div', class_='prose')

    if description:
        raw_html = str(description)
        desc_text = re.sub(r'<[^>]+>', ' ', raw_html)
        desc_text = re.sub(r'\s+', ' ', desc_text).strip()
                
        for kw in PREMIUM_KEYWORDS:
            if kw.lower() in desc_text.lower():
                has_premium = 1
                premium_type = kw
                break
                
        en_title = extract_romaji_title(desc_text)

    return en_title, has_premium, premium_type

def save_json_safely(data, final_filename):
    os.makedirs(os.path.dirname(final_filename), exist_ok=True)
    temp_filename = final_filename + ".tmp"
    with open(temp_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    os.rename(temp_filename, final_filename)
    
    latest_filename = os.path.join(os.path.dirname(final_filename), "parsed_phoenix_latest.json")
    shutil.copyfile(final_filename, latest_filename)

def parse_split_html():
    today_str = datetime.now().strftime("%Y%m%d")
    input_folder = f"data/raw_lake/{today_str}"
    output_file = f"data/bronze/parsed_phoenix_{today_str}.json"
    
    if not os.path.exists(input_folder):
        print(f"Not Found {input_folder}")
        return
        
    # 🌟 เปลี่ยนมาอ่านไฟล์ .json แทน
    files = [f for f in os.listdir(input_folder) if f.endswith('.json')]
    parsed_data = []
    
    print(f"Start Parsing {len(files)} ไฟล์...")

    for filename in tqdm(files, desc="Parsing", unit="file"):
        file_path = os.path.join(input_folder, filename)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                item_data = json.load(f)
                
            url = item_data.get("url", "Unknown")
            raw_title = item_data.get("raw_title", "Unknown")
            html_content = item_data.get("raw_html", "")
            
            soup = BeautifulSoup(html_content, 'lxml')
            
            clean_name, type_media = process_title(raw_title)
            th_title, th_vol, raw_vol = match_tile_vol(clean_name)
            release_date_th = find_th_release_date(soup)
            th_price = find_price(soup)
            en_title, has_premium, premium_type = process_description(soup)
            
            parsed_data.append({
                "url": url,
                "title_th": th_title,
                "vol_th": th_vol,
                "vol_raw": raw_vol,
                "title_en": en_title,
                "has_premium": has_premium,
                "premium_type": premium_type,
                "media_type" : type_media,
                "price": th_price,
                "th_release_date": release_date_th,
            })
                
        except Exception as e:
            tqdm.write(f"Error at file {filename}: {e}")

    print(f"\nDone. Parsing all {len(parsed_data)} records")
    save_json_safely(parsed_data, output_file)
    print("Save to JSON")

if __name__ == "__main__":
    parse_split_html()