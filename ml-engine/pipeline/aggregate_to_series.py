# ไฟล์: 6_aggregate_to_series.py
import os
import json
import shutil
import pandas as pd
from datetime import datetime

def save_json_safely(data, final_filename):
    os.makedirs(os.path.dirname(final_filename), exist_ok=True)
    temp_filename = final_filename + ".tmp"
    with open(temp_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
    os.replace(temp_filename, final_filename)
    
    # อัปเดตไฟล์ latest 
    latest_filename = os.path.join(os.path.dirname(final_filename), "manga_series_latest.json")
    shutil.copyfile(final_filename, latest_filename)

def aggregate_to_series():
    input_file = "data/silver/enriched_mu_latest.json"
    
    if not os.path.exists(input_file):
        print(f"Not Found {input_file}")
        return

    print(f"Loading Data From Silver Layer: {input_file}")
    df_raw = pd.read_json(input_file)
    
    initial_count = len(df_raw)
    print(f"   Found {initial_count} Records")

    df_raw['th_release_date'] = pd.to_datetime(df_raw['th_release_date'], errors='coerce').dt.tz_localize(None)

    print("Processing Data...")

    df_series = df_raw.groupby('title_th').agg(
        url=('url', 'first'),
        title_en=('title_en', 'first'),
        title_jp=('title_jp', 'first'),
        authors=('authors', 'first'),
        genres=('genres', 'first'),
        media_type=('media_type', 'first'),
        jikan_status=('jikan_status', 'first'),
        jp_total_vols=('jp_total_vols', 'first'),
        
        # ฟีเจอร์ที่เกิดจากการคำนวณ
        max_vol_th=('vol_th', 'max'),             # เล่มล่าสุดของไทย
        avg_price=('price', 'mean'),              # ราคาเฉลี่ยของเรื่องนี้
        has_premium_count=('has_premium', 'sum'), # เคยทำพรีเมียมไปกี่เล่ม
        latest_th_release=('th_release_date', 'max'), # วันที่ออกเล่มล่าสุด
        first_th_release=('th_release_date', 'min')   # วันที่ออกเล่มแรกสุด
    ).reset_index()

    current_date = pd.to_datetime(datetime.now())

    df_series['vol_gap'] = df_series['jp_total_vols'] - df_series['max_vol_th']
    df_series['vol_gap'] = df_series['vol_gap'].apply(lambda x: x if x > 0 else 0)

    df_series['days_since_last_release'] = (current_date - df_series['latest_th_release']).dt.days

    df_series['latest_th_release'] = df_series['latest_th_release'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    df_series['first_th_release'] = df_series['first_th_release'].dt.strftime('%Y-%m-%dT%H:%M:%SZ')
    
    df_series = df_series.where(pd.notnull(df_series), None)

    final_data = df_series.to_dict(orient='records')
    
    today_str = datetime.now().strftime("%Y%m%d")
    output_file = f"data/gold/manga_series_{today_str}.json"
    
    save_json_safely(final_data, output_file)
    
    final_count = len(final_data)
    print(f"\nMerge Successful! from {initial_count} Reacords to {final_count} Records")
    print(f"Save to Gold Layer (for ML) at: {output_file}")

    csv_file = f"data/gold/manga_series_{today_str}.csv"
    latest_csv_file = "data/gold/manga_series_latest.csv"

    df_series.to_csv(csv_file, index=False, encoding='utf-8-sig')

    shutil.copyfile(csv_file, latest_csv_file)
    
    print(f"CSV Excel at: {csv_file}")
    print(f"Latest CSV Excel at: {latest_csv_file}")

if __name__ == "__main__":
    aggregate_to_series()