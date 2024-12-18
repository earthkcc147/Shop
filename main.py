import os
import json
import requests
from dotenv import load_dotenv

# โหลดข้อมูลจากไฟล์ .env
load_dotenv()

# อ่านข้อมูลจาก .env
API_URL = os.getenv('API_URL')
USERS = json.loads(os.getenv('USERS'))  # แปลงค่า USERS เป็น list ของ dictionary

# ฟังก์ชันสำหรับล็อคอิน
def login(username, password):
    # ค้นหาผู้ใช้ที่ตรงกับ username และ password
    user = next((user for user in USERS if user['username'] == username and user['password'] == password), None)
    if user:
        print(f"ล็อคอินสำเร็จสำหรับ {username}")
        return user  # ส่งคืนข้อมูลของผู้ใช้ที่ล็อคอินสำเร็จ
    else:
        print(f"การล็อคอินล้มเหลวสำหรับ {username}")
        return None

# ฟังก์ชันสำหรับดึงข้อมูลบริการจาก API
def get_service_data(user, platform):
    api_key = user['Api_key']  # ใช้ api_key ของผู้ใช้
    params = {
        'key': api_key,
        'action': 'services'  # การกระทำคือดึงข้อมูลบริการ
    }
    # ส่งคำขอ POST ไปยัง API เพื่อดึงข้อมูลบริการ
    response = requests.post(f'{API_URL}/service', params=params)
    
    if response.status_code == 200:
        service_data = response.json()
        print(f"กำลังดึงข้อมูลบริการสำหรับ {platform}...")
        # แสดงข้อมูลบริการที่ได้จาก API
        for item in service_data:
            print(f"ชื่อบริการ: {item['name']}")
            print(f"ประเภท: {item['type']}")
            print(f"หมวดหมู่: {item['category']}")
            print(f"อัตรา: {item['rate']}")
            print(f"ขั้นต่ำ: {item['min']}")
            print(f"สูงสุด: {item['max']}")
            print(f"สามารถเติมเงินได้: {item['refill']}")
            print(f"สามารถยกเลิกได้: {item['cancel']}")
            print("-" * 50)
    else:
        print(f"ไม่สามารถดึงข้อมูลบริการสำหรับ {platform} จาก API: {response.status_code}")

# ฟังก์ชันหลักสำหรับเมนู
def main():
    print("ยินดีต้อนรับสู่ระบบจัดการบริการ!")
    print("กรุณาล็อคอินเพื่อดำเนินการต่อ")
    
    # รับข้อมูลล็อคอินจากผู้ใช้
    username = input("กรุณากรอกชื่อผู้ใช้: ")
    password = input("กรุณากรอกรหัสผ่าน: ")
    
    # ล็อคอินและตรวจสอบข้อมูลผู้ใช้
    user = login(username, password)
    
    if user:
        # แสดงเมนูแพลตฟอร์ม
        show_platform_menu(user)
    else:
        print("การล็อคอินล้มเหลว กรุณาตรวจสอบชื่อผู้ใช้และรหัสผ่าน.")

# ฟังก์ชันสำหรับแสดงเมนูเลือกแพลตฟอร์ม
def show_platform_menu(user):
    print("\nกรุณาเลือกแพลตฟอร์มที่ต้องการจัดการบริการ:")
    
    platforms = user['products'].keys()
    
    # แสดงรายการแพลตฟอร์ม
    for idx, platform in enumerate(platforms, 1):
        print(f"{idx}. {platform}")
    
    # รับข้อมูลจากผู้ใช้
    try:
        choice = int(input(f"\nกรุณากรอกหมายเลข (1-{len(platforms)}): "))
        
        if 1 <= choice <= len(platforms):
            platform = list(platforms)[choice - 1]
            print(f"\nคุณเลือกแพลตฟอร์ม {platform}.\n")
            show_service_data(user, platform)
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่.")
            show_platform_menu(user)
    except ValueError:
        print("ข้อมูลไม่ถูกต้อง กรุณากรอกหมายเลข.")
        show_platform_menu(user)

# ฟังก์ชันสำหรับแสดงข้อมูลบริการของแพลตฟอร์ม
def show_service_data(user, platform):
    services = user['products'].get(platform, [])
    print(f"กำลังดึงข้อมูลบริการสำหรับ {platform}...")
    
    for service in services:
        print(f"\nService ID: {service}")
        
        # ดึงข้อมูลบริการจาก API
        get_service_data(user, platform)

if __name__ == '__main__':
    main()