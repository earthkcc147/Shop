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
    user = next((user for user in USERS if user['username'] == username and user['password'] == password), None)
    if user:
        print(f"ล็อคอินสำเร็จสำหรับ {username}")
        return user
    else:
        print("การล็อคอินล้มเหลว กรุณาตรวจสอบชื่อผู้ใช้และรหัสผ่าน.")
        return None

# ฟังก์ชันสำหรับดึงข้อมูลบริการจาก API
def get_services(api_key):
    params = {
        'key': api_key,
        'action': 'services'
    }
    
    try:
        response = requests.post(f'{API_URL}/v2', data=params)
        response.raise_for_status()  # ตรวจสอบว่าไม่มีข้อผิดพลาด HTTP
        response_data = response.json()
        
        # ตรวจสอบการตอบกลับจาก API
        if isinstance(response_data, list):
            return response_data
        else:
            print("ข้อมูลบริการไม่ถูกต้องหรือไม่ได้รับข้อมูลที่คาดหวังจาก API")
            return []
    except requests.exceptions.RequestException as e:
        print(f"ไม่สามารถเชื่อมต่อกับ API ได้: {e}")
        return []

# ฟังก์ชันสำหรับแสดงข้อมูลบริการ
def show_service_data(user, platform):
    services = user['products'].get(platform, [])
    print(f"\nข้อมูลบริการสำหรับ {platform}:")
    for idx, service_id in enumerate(services, 1):
        print(f"{idx}. Service ID: {service_id}")
    
    try:
        choice = int(input(f"\nกรุณากรอกหมายเลข Service (1-{len(services)}): "))
        if 1 <= choice <= len(services):
            service_id = services[choice - 1]
            print(f"\nคุณเลือก Service ID: {service_id}")
            # แสดงข้อมูลรายละเอียดของบริการที่เลือก
            service_details = get_services(user['Api_key'])
            service_detail = next((service for service in service_details if service['service'] == service_id), None)
            if service_detail:
                print(f"\nรายละเอียดบริการที่เลือก:")
                print(f"ชื่อบริการ: {service_detail['name']}")
                print(f"ประเภท: {service_detail['type']}")
                print(f"หมวดหมู่: {service_detail['category']}")
                print(f"อัตรา: {service_detail['rate']}")
                print(f"ขั้นต่ำ: {service_detail['min']}")
                print(f"สูงสุด: {service_detail['max']}")
                print(f"สามารถรีฟิล: {'ใช่' if service_detail['refill'] else 'ไม่ใช่'}")
                print(f"สามารถยกเลิก: {'ใช่' if service_detail['cancel'] else 'ไม่ใช่'}")
            else:
                print("ไม่พบข้อมูลบริการที่เลือก.")
            add_order(user, service_id)
        else:
            print("ตัวเลือกไม่ถูกต้อง กรุณาลองใหม่.")
            show_service_data(user, platform)
    except ValueError:
        print("ข้อมูลไม่ถูกต้อง กรุณากรอกหมายเลข.")
        show_service_data(user, platform)

# ฟังก์ชันสำหรับแสดงเมนูแพลตฟอร์ม
def show_platform_menu(user):
    print("\nกรุณาเลือกแพลตฟอร์มที่ต้องการจัดการบริการ:")
    platforms = user['products'].keys()
    for idx, platform in enumerate(platforms, 1):
        print(f"{idx}. {platform}")
    
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

# ฟังก์ชันหลัก
def main():
    print("ยินดีต้อนรับสู่ระบบจัดการบริการ!")
    print("กรุณาล็อคอินเพื่อดำเนินการต่อ")
    
    username = input("กรุณากรอกชื่อผู้ใช้: ")
    password = input("กรุณากรอกรหัสผ่าน: ")
    
    user = login(username, password)
    if user:
        show_platform_menu(user)

if __name__ == '__main__':
    main()