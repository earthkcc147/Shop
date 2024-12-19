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
        print("การล็อคอินล้มเหลว.")
        return None

# ฟังก์ชันสำหรับดึงรายการบริการจาก API
def get_service_list(api_key):
    params = {
        'key': api_key,
        'action': 'service'
    }
    response = requests.post(API_URL, data=params)
    if response.status_code == 200:
        services = response.json()
        print("\nรายการบริการที่พร้อมใช้งาน:")
        for idx, service in enumerate(services, 1):
            print(f"{idx}. {service['name']} (ID: {service['service']})")
            print(f"   ประเภท: {service['type']}, หมวดหมู่: {service['category']}")
            print(f"   อัตรา: {service['rate']}, ขั้นต่ำ: {service['min']}, สูงสุด: {service['max']}")
            print(f"   เติมเงินได้: {'ใช่' if service['refill'] else 'ไม่ใช่'}, ยกเลิกได้: {'ใช่' if service['cancel'] else 'ไม่ใช่'}")
            print("-" * 50)
        return services
    else:
        print("ไม่สามารถดึงข้อมูลบริการได้.")
        return []

# ฟังก์ชันสำหรับสั่งซื้อสินค้า
def place_order(api_key, service_id, link, quantity):
    params = {
        'key': api_key,
        'action': 'add',
        'service': service_id,
        'link': link,
        'quantity': quantity
    }
    response = requests.post(API_URL, data=params)
    if response.status_code == 200:
        order_data = response.json()
        print(f"คำสั่งซื้อสำเร็จ! หมายเลขคำสั่งซื้อ: {order_data['order']}")
    else:
        print(f"การสั่งซื้อล้มเหลว: {response.text}")

# ฟังก์ชันหลัก
def main():
    print("ระบบจัดการคำสั่งซื้อ")
    username = input("ชื่อผู้ใช้: ")
    password = input("รหัสผ่าน: ")
    user = login(username, password)
    if user:
        services = get_service_list(user['Api_key'])
        if services:
            try:
                choice = int(input("เลือกบริการที่ต้องการ (ระบุหมายเลข): "))
                if 1 <= choice <= len(services):
                    selected_service = services[choice - 1]
                    link = input("กรอกลิงก์สำหรับคำสั่งซื้อ: ")
                    quantity = int(input(f"กรอกจำนวน (ขั้นต่ำ {selected_service['min']} สูงสุด {selected_service['max']}): "))
                    if selected_service['min'] <= quantity <= selected_service['max']:
                        place_order(user['Api_key'], selected_service['service'], link, quantity)
                    else:
                        print("จำนวนไม่อยู่ในช่วงที่กำหนด.")
                else:
                    print("ตัวเลือกไม่ถูกต้อง.")
            except ValueError:
                print("กรุณากรอกหมายเลขที่ถูกต้อง.")
        else:
            print("ไม่มีบริการที่พร้อมใช้งาน.")
    else:
        print("การเข้าสู่ระบบล้มเหลว.")

if __name__ == '__main__':
    main()