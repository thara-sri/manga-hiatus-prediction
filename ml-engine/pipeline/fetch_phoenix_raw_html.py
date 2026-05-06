# ไฟล์: 1_fetch_raw_html_split.py
import os
import requests
import time
import json
from datetime import datetime
from bs4 import BeautifulSoup

TARGET_CATEGORIES = [
    "https://www.phoenixnext.com/manga.html?p="
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def fetch_html_split():
    today_str = datetime.now().strftime("%Y%m%d")
    folder_path = f"data/raw_lake/{today_str}"
    os.makedirs(folder_path, exist_ok=True)
    
    item_count = 0
    
    for base_url in TARGET_CATEGORIES:
        print(f"\nScanning the categories: {base_url}")
        page = 1
        first_page_first_item_url = None
        
        while True:
            print(f"URL page {page}...")
            res = requests.get(f"{base_url}{page}", headers=HEADERS)
            
            if res.status_code != 200:
                print(f"Error {res.status_code} Stop searching.")
                break
            
            soup = BeautifulSoup(res.text, 'lxml')
            items = soup.find_all('a', class_='product-item-link line-clamp-2')
            
            if not items:
                print(f"Not Found Page {page} Finshing.")
                break

            current_first_item_url = items[0]['href']
            
            if page == 1:
                first_page_first_item_url = current_first_item_url
            elif current_first_item_url == first_page_first_item_url:
                print(f"Fisnished at page{page - 1}")
                break
                
            if page > 150:
                print("Something Wrong.")
                break

            for a_tag in items:
                url = a_tag['href']
                raw_title = a_tag.text.strip()
                item_count += 1
                
                file_path = os.path.join(folder_path, f"item_{item_count:05d}.json")
                
                if os.path.exists(file_path):
                    print(f"Skip (Loaded): item_{item_count:05d}.json")
                    continue

                try:
                    detail_res = requests.get(url, headers=HEADERS)
                    
                    data_to_save = {
                        "url": url,
                        "raw_title": raw_title,
                        "raw_html": detail_res.text
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(data_to_save, f, ensure_ascii=False)
                        
                    print(f"Saved [{item_count}]: {raw_title}")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error at {url}: {e}")
                    
            page += 1

    print(f"\nData scan complete. All {item_count} files have been downloaded and saved.")

    pointer_path = "data/raw_lake/_latest_run.txt"
    with open(pointer_path, 'w', encoding='utf-8') as f:
        f.write(today_str)
    
    print(f"Target file created successfully. (Pointing to: {today_str})")

if __name__ == "__main__":
    fetch_html_split()