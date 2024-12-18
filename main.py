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
    login_data = {
        'username': username,
        'password': password
    }
    response = requests.post(f'{API_URL}/login', data=login_data)
    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"การล็อคอินล้มเหลวสำหรับ {username}")
        return None

# ฟังก์ชันสำหรับดึงข้อมูลสินค้า
def get_service_data(api_key, token, service):
    headers = {
        'Authorization': f'Bearer {token}',
        'API-Key': api_key  # ใช้ API_KEY ของสมาชิกใน header
    }
    params = {
        'key': api_key,
        'action': service
    }
    response = requests.post(f'{API_URL}/service', headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"ไม่สามารถดึงข้อมูลบริการสำหรับ service {service}: {response.status_code}")
        return None

# ฟังก์ชันหลักสำหรับเมนู
def main():
    print("ยินดีต้อนรับสู่ระบบจัดการบริการ!")
    print("กรุณาล็อคอินเพื่อดำเนินการต่อ")
    
    # รับข้อมูลล็อคอินจากผู้ใช้
    username = input("กรุณากรอกชื่อผู้ใช้: ")
    password = input("กรุณากรอกรหัสผ่าน: ")
    
    # ค้นหาผู้ใช้ใน USERS
    user = next((user for user in USERS if user['username'] == username), None)
    
    if user:
        # ล็อคอินและรับ token
        token = login(username, password)
        if token:
            print(f"\nล็อคอินสำเร็จสำหรับ {username}.")
            show_platform_menu(user, token)
        else:
            print("การล็อคอินล้มเหลว กรุณาตรวจสอบชื่อผู้ใช้และรหัสผ่าน.")
    else:
        print("ไม่พบชื่อผู้ใช้นี้ในระบบ.")

# ฟังก์ชันสำหรับแสดงเมนูเลือกแพลตฟอร์ม
def show_platform_menu(user, token):
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
            show_service_data(user, token, platform)
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่.")
            show_platform_menu(user, token)
    except ValueError:
        print("ข้อมูลไม่ถูกต้อง กรุณากรอกหมายเลข.")
        show_platform_menu(user, token)

# ฟังก์ชันสำหรับแสดงข้อมูลบริการของแพลตฟอร์ม
def show_service_data(user, token, platform):
    services = user['products'][platform]
    print(f"กำลังดึงข้อมูลบริการสำหรับ {platform}...")
    
    for service in services:
        print(f"\nService ID: {service}")
        
        # ดึงข้อมูลสินค้า
        service_data_result = get_service_data(user['api_key'], token, service)
        if service_data_result:
            for item in service_data_result:
                print(f"ชื่อบริการ: {item['name']}")
                # คุณสามารถแสดงข้อมูลเพิ่มเติมที่ต้องการได้ที่นี่
        else:
            print(f"ไม่พบข้อมูลบริการสำหรับ Service ID {service}.")

if __name__ == '__main__':
    main()
