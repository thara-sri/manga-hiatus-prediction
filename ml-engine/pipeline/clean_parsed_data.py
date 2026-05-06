import os
import json

def fix_missing_english_titles():
    input_file = "data/bronze/parsed_phoenix_latest.json"
    
    output_file = "data/bronze/parsed_phoenix_cleaned.json"

    if not os.path.exists(input_file):
        print(f"Not Found {input_file}")
        return

    print(f"Reading Data From: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    title_mapping = {}
    
    invalid_keywords = ["ไม่พบข้อมูลภาษาอังกฤษ", "ไม่พบวงเล็บ", "ไม่พบข้อมูล", "Unknown"]

    for item in data:
        th_title = item.get("title_th")
        en_title = item.get("title_en")

        if en_title and not any(kw in en_title for kw in invalid_keywords):
            if th_title not in title_mapping:
                title_mapping[th_title] = en_title

    print(f"Learn all the correct English names of {len(title_mapping)} items")

    fixed_count = 0
    for item in data:
        th_title = item.get("title_th")
        en_title = item.get("title_en")

        if any(kw in en_title for kw in invalid_keywords) and th_title in title_mapping:
            correct_en_title = title_mapping[th_title]
            
            print(f"Editing: [{th_title}] Vol {item.get('vol_th')} | '{en_title}' -> '{correct_en_title}'")
            
            item["title_en"] = correct_en_title
            fixed_count += 1

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"\nEditing {fixed_count} Records")
    print(f"Save file to: {output_file}")

if __name__ == "__main__":
    fix_missing_english_titles()