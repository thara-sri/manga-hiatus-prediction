# ไฟล์: 5_enrich_mu.py
import os
import json
import time
import requests
import shutil
import re
from tqdm import tqdm

def save_json_safely(data, final_filename):
    os.makedirs(os.path.dirname(final_filename), exist_ok=True)
    temp_filename = final_filename + ".tmp"
    with open(temp_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    os.replace(temp_filename, final_filename)
    
    latest_filename = os.path.join(os.path.dirname(final_filename), "enriched_mu_latest.json")
    shutil.copyfile(final_filename, latest_filename)

def enrich_with_mangaupdates():
    pointer_file = "data/raw_lake/_latest_run.txt"
    if not os.path.exists(pointer_file):
        print(f"Not Found {pointer_file}")
        return
        
    with open(pointer_file, 'r', encoding='utf-8') as f:
        target_date = f.read().strip()

    input_file = f"data/silver/enriched_jikan_{target_date}.json"
    output_file = f"data/silver/enriched_mu_{target_date}.json"

    if os.path.exists(output_file):
        print("🔄 พบไฟล์ Checkpoint ของ MangaUpdates กำลังอ่านข้อมูลเพื่อทำต่อ...")
        with open(output_file, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
    elif os.path.exists(input_file):
        print("📖 อ่านข้อมูลตั้งต้นจาก Jikan...")
        with open(input_file, 'r', encoding='utf-8') as f:
            full_data = json.load(f)
    else:
        print(f"Not Found {input_file}")
        return

    items_to_process = [m for m in full_data if m.get("jikan_status") == "PENDING_MU"]
    
    if not items_to_process:
        print("Up-to-Date")
        return
        
    print(f"Found MU (Final Step): {len(items_to_process)} Records")

    save_counter = 0

    try:
        for manga in tqdm(items_to_process, desc="MangaUpdates", unit="manga"):
            search_term = manga.get("title_jp")
            if not search_term:
                search_term = manga.get("title_en")
            
            if not search_term or search_term == "Unknown" or "ไม่พบ" in search_term:
                manga["jikan_status"] = "UNKNOWN"
                save_counter += 1
                continue

            search_url = "https://api.mangaupdates.com/v1/series/search"
            search_payload = {"search": search_term}

            try:
                mu_res = requests.post(search_url, json=search_payload)
                    
                if mu_res.status_code == 200:
                    results = mu_res.json().get("results", [])

                    if len(results) > 0:
                        series_id = results[0].get("record", {}).get("series_id")
                        
                        detail_url = f"https://api.mangaupdates.com/v1/series/{series_id}"
                        detail_res = requests.get(detail_url)
                        
                        if detail_res.status_code == 200:
                            detail_data = detail_res.json()
                            
                            mu_status_text = detail_data.get("status", "")
                            
                            vol_match = re.search(r'(\d+)\s+Volumes?', mu_status_text, re.IGNORECASE)
                            vols_count = int(vol_match.group(1)) if vol_match else 0
                            
                            if "Complete" in mu_status_text:
                                manga["jikan_status"] = "FINISHED"
                            elif "Ongoing" in mu_status_text:
                                manga["jikan_status"] = "ONGOING"
                            elif "Hiatus" in mu_status_text:
                                manga["jikan_status"] = "HIATUS"
                            else:
                                manga["jikan_status"] = "UNKNOWN"
                            
                            manga["jp_total_vols"] = vols_count

                            if vols_count > 0:
                                tqdm.write(f"   MU Found! Japanese vols: {vols_count} | {search_term}")
                            else:
                                tqdm.write(f"   MU Found But NO Volumes | {search_term}")
                        else:
                            manga["jikan_status"] = "API_ERROR"
                                
                    else:
                        manga["jikan_status"] = "NOT_FOUND"
                        tqdm.write(f"   MU Not Found | {search_term}")

                elif mu_res.status_code == 429:
                    tqdm.write("   MU Rate Limit!")
                    time.sleep(5)
                    continue 
                else:
                    manga["jikan_status"] = "API_ERROR"

            except Exception as e:
                tqdm.write(f"   API Error: {e}")

            save_counter += 1
            time.sleep(1.5)

            if save_counter % 50 == 0:
                save_json_safely(full_data, output_file)

    except KeyboardInterrupt:
        print("\nSudden stoppage.!")
    except Exception as e:
        print(f"\nError: {e}")
        
    finally:
        print(f"\nEmergency save system {len(full_data)} Records...")
        save_json_safely(full_data, output_file)
        print("Pipeline to Silver Layer successfully")

if __name__ == "__main__":
    enrich_with_mangaupdates()