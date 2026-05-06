# ไฟล์: 4_enrich_jikan.py
import os
import json
import time
import requests
import shutil
from tqdm import tqdm

def save_json_safely(data, final_filename):
    os.makedirs(os.path.dirname(final_filename), exist_ok=True)
    temp_filename = final_filename + ".tmp"
    with open(temp_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    os.replace(temp_filename, final_filename)
    
    # อัปเดตไฟล์ latest
    latest_filename = os.path.join(os.path.dirname(final_filename), "enriched_jikan_latest.json")
    shutil.copyfile(final_filename, latest_filename)

def enrich_with_jikan():
    pointer_file = "data/raw_lake/_latest_run.txt"
    if not os.path.exists(pointer_file):
        print(f"Not Found {pointer_file}")
        return
        
    with open(pointer_file, 'r', encoding='utf-8') as f:
        target_date = f.read().strip()

    cleaned_file = "data/bronze/parsed_phoenix_cleaned.json"
    latest_bronze_file = "data/bronze/parsed_phoenix_latest.json"
    input_file = cleaned_file if os.path.exists(cleaned_file) else latest_bronze_file
    
    output_folder = "data/silver"
    output_file = f"{output_folder}/enriched_jikan_{target_date}.json"

    print(f"Reding Data From: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        manga_list = json.load(f)

    enriched_data = []
    processed_urls = set()

    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            enriched_data = json.load(f)
            processed_urls = {m['url'] for m in enriched_data}
        print(f"Found Old Data. Skip{len(processed_urls)} Records.")

    items_to_process = [m for m in manga_list if m['url'] not in processed_urls]
    
    if not items_to_process:
        print("Jikan Up-to-date")
        return
        
    print(f"Found Jikan: {len(items_to_process)} Records")

    save_counter = 0

    for manga in tqdm(items_to_process, desc="🔍 Jikan API", unit="manga"):
        title_en = manga.get("title_en", "")
        
        if not title_en or "ไม่พบ" in title_en or title_en == "Unknown":
            manga["jikan_status"] = "PENDING_MU"
            manga["genres"] = []
            manga["authors"] = []
            manga["title_jp"] = ""
            manga["jp_total_vols"] = 0
            enriched_data.append(manga)
            continue

        jikan_url = f"https://api.jikan.moe/v4/manga?q={title_en}&limit=1"
        
        try:
            jikan_res = requests.get(jikan_url)
            
            if jikan_res.status_code == 200:
                jikan_data = jikan_res.json().get("data", [])

                if len(jikan_data) > 0:
                    first_result = jikan_data[0]
                    status = first_result.get("status")
                    volumes = first_result.get("volumes")
                    
                    genre_list = [g['name'] for g in first_result.get("genres", [])]
                    author_list = [a['name'] for a in first_result.get("authors", [])]
                    
                    manga["genres"] = genre_list
                    manga["authors"] = author_list
                    manga["title_jp"] = first_result.get("title_japanese", "")

                    vols_count = volumes if volumes is not None else 0
                    manga["jp_total_vols"] = vols_count

                    if vols_count > 0:
                        if status == "Finished":
                            manga["jikan_status"] = "FINISHED"
                        elif status == "Publishing":
                            manga["jikan_status"] = "ONGOING"
                        else:
                            manga["jikan_status"] = "UNKNOWN"
                        tqdm.write(f"   Found Data [{status}] Japanese: {vols_count} | {title_en}")
                    else:
                        manga["jikan_status"] = "PENDING_MU" 
                        tqdm.write(f"   Foud Data but No Japanese vol, send to PENDING_MU | {title_en}")

                else:
                    tqdm.write(f"   Not foud in Jikan send to PENDING_MU | {title_en}")
                    manga["jikan_status"] = "PENDING_MU"
                    manga["genres"] = []
                    manga["authors"] = []
                    manga["title_jp"] = ""
                    manga["jp_total_vols"] = 0

            elif jikan_res.status_code == 429:
                tqdm.write("   Jikan Rate Limit (429)!")
                time.sleep(5)
                continue 
                
            else:
                manga["jikan_status"] = "API_ERROR"
                tqdm.write(f"   API Error {jikan_res.status_code} for {title_en}")

            enriched_data.append(manga)
            save_counter += 1
            
            time.sleep(1.5)

            if save_counter % 50 == 0:
                save_json_safely(enriched_data, output_file)

        except Exception as e:
            tqdm.write(f"   Error: {e}")
            time.sleep(2)

    print(f"\nJikan connection successful! A total of  {len(enriched_data)} items have been accumulated in the Silver Layer.")
    save_json_safely(enriched_data, output_file)

if __name__ == "__main__":
    enrich_with_jikan()