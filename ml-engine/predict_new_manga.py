# ไฟล์: 7_predict_new_manga.py
import pandas as pd
import joblib
import os

def predict_manga_survival(price, jp_total_vols, genres):
    print("🤖 กำลังปลุก AI ให้ตื่นขึ้นมาทำนาย...")
    
    # 1. โหลดไฟล์สมองกลที่เราเซฟไว้
    try:
        model = joblib.load('notebook/models/manga_survival_model.pkl')
        mlb = joblib.load('notebook/models/genre_encoder.pkl')
        expected_features = joblib.load('notebook/models/model_features.pkl')
    except FileNotFoundError:
        print("❌ หาไฟล์โมเดลไม่เจอ! กรุณารันโค้ดเซฟโมเดลใน Jupyter Notebook ก่อนครับ")
        return

    # 2. แปลงหมวดหมู่ (Genres) ให้เป็น 0 กับ 1 ด้วยเครื่องมือที่ AI รู้จัก
    genres_encoded = mlb.transform([genres])
    
    # 3. สร้างตารางเบาะแสเปล่าๆ (ใส่ 0 ไว้ก่อน) ให้ตรงกับหน้าตาข้อสอบที่โมเดลเคยเรียน
    input_data = pd.DataFrame(0, index=[0], columns=expected_features)
    
    # 4. หยอดข้อมูลที่เรามี ณ วันนี้ลงไปในตาราง
    if 'avg_price' in input_data.columns:
        input_data['avg_price'] = price
    if 'jp_total_vols' in input_data.columns:
        input_data['jp_total_vols'] = jp_total_vols
        
    # หยอดข้อมูล Genres ที่แปลงเป็นตัวเลขแล้วลงไป
    genre_cols = [f"genre_{c}" for c in mlb.classes_]
    for col, val in zip(genre_cols, genres_encoded[0]):
        if col in input_data.columns:
            input_data[col] = val

    # 5. สั่งให้ AI ทำนาย!
    prediction = model.predict(input_data)[0]          # ผลลัพธ์: 0 (รอด) หรือ 1 (ดอง)
    probabilities = model.predict_proba(input_data)[0] # ดูเปอร์เซ็นต์ความมั่นใจ
    
    prob_safe = probabilities[0] * 100
    prob_drop = probabilities[1] * 100

    # 6. สรุปผลให้คนอ่านเข้าใจง่ายๆ
    print("\n" + "="*45)
    print("🔮 ผลคำทำนายจาก AI หมอดูมังงะ")
    print("="*45)
    print(f"💰 ราคา: {price} บาท")
    print(f"📚 จำนวนเล่มญี่ปุ่นล่าสุด: {jp_total_vols} เล่ม")
    print(f"🎭 หมวดหมู่: {', '.join(genres)}")
    print("-" * 45)
    
    if prediction == 1:
        print(f"🚨 สถานะฟันธง: มีความเสี่ยง 'โดนลอยแพ'")
        print(f"📉 AI มั่นใจว่าโดนดอง: {prob_drop:.1f}%")
        print(f"💡 คำแนะนำ: กำเงินไว้ก่อน รอให้ออกสัก 3-4 เล่มค่อยพิจารณาใหม่")
    else:
        print(f"✅ สถานะฟันธง: ปลอดภัย 'น่าจะรอด'")
        print(f"📈 AI มั่นใจว่าได้พิมพ์ต่อ: {prob_safe:.1f}%")
        print(f"💡 คำแนะนำ: เก็บเงินซื้อได้เลย โอกาสพิมพ์จบค่อนข้างสูง")
    print("="*45 + "\n")

if __name__ == "__main__":
    # 🎯 วิธีใช้งาน: สมมติว่าวันนี้สำนักพิมพ์ประกาศลิขสิทธิ์เรื่องใหม่ 2 เรื่อง 
    # คุณแค่มาเปลี่ยนตัวเลขในวงเล็บข้างล่างนี้ แล้วรันสคริปต์ได้เลย!
    
    print("เคสที่ 1: มังงะต่อสู้สายหลัก ต้นฉบับญี่ปุ่นปาไป 25 เล่มแล้ว แถมขายถูก")
    predict_manga_survival(
        price=145, 
        jp_total_vols=25, 
        genres=['Action', 'Adventure', 'Fantasy']
    )
    
    print("เคสที่ 2: มังงะเฉพาะกลุ่ม เล่มละเกือบ 200 บาท แต่ญี่ปุ่นเพิ่งมี 3 เล่ม")
    predict_manga_survival(
        price=185, 
        jp_total_vols=5, 
        genres=['Comedy', 'Girls Love']
    )

    print("เคสที่ 3: มังงะเฉพาะกลุ่ม เล่มละเกือบ  บาท แต่ญี่ปุ่นเพิ่งมี 3 เล่ม")
    predict_manga_survival(
        price=600, 
        jp_total_vols=12, 
        genres=['Girls Love']
    )