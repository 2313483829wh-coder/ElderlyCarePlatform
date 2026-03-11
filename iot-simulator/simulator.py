"""
IoT 设备模拟器
模拟智能手环、血压计等设备向后端发送健康数据
可通过 HTTP API 直接发送，无需 MQTT Broker
"""
import os
import sys
import time
import random
import json
import requests
from datetime import datetime
from decimal import Decimal

API_BASE = os.environ.get('API_BASE', 'http://127.0.0.1:8000/api')
USERNAME = os.environ.get('API_USER', 'admin')
PASSWORD = os.environ.get('API_PASS', 'admin123')

NORMAL_RANGES = {
    'heart_rate': (60, 100),
    'systolic_bp': (90, 140),
    'diastolic_bp': (60, 90),
    'blood_oxygen': (95.0, 100.0),
    'temperature': (36.0, 37.3),
    'blood_sugar': (3.9, 6.1),
    'steps': (0, 8000),
    'sleep_hours': (5.0, 9.0),
}

ANOMALY_CHANCE = 0.15


def get_token():
    resp = requests.post(f'{API_BASE}/system/login/', json={
        'username': USERNAME,
        'password': PASSWORD,
    })
    resp.raise_for_status()
    return resp.json()['access']


def get_devices(token):
    headers = {'Authorization': f'Bearer {token}'}
    resp = requests.get(f'{API_BASE}/health/devices/', headers=headers, params={'page_size': 100})
    resp.raise_for_status()
    data = resp.json()
    return data.get('results', data)


def generate_reading(anomaly=False):
    """生成一条健康数据，anomaly=True 时模拟异常"""
    data = {}
    for field, (lo, hi) in NORMAL_RANGES.items():
        if isinstance(lo, float):
            val = round(random.uniform(lo, hi), 1)
        else:
            val = random.randint(lo, hi)

        if anomaly and random.random() < 0.3:
            if field == 'heart_rate':
                val = random.choice([random.randint(35, 48), random.randint(125, 170)])
            elif field == 'systolic_bp':
                val = random.randint(165, 200)
            elif field == 'blood_oxygen':
                val = round(random.uniform(80.0, 89.0), 1)
            elif field == 'temperature':
                val = round(random.uniform(37.8, 39.5), 1)

        data[field] = val
    return data


def send_health_data(token, device):
    headers = {'Authorization': f'Bearer {token}'}
    is_anomaly = random.random() < ANOMALY_CHANCE
    reading = generate_reading(anomaly=is_anomaly)
    reading['elder'] = device['elder']
    reading['device_id'] = device['device_id']

    resp = requests.post(f'{API_BASE}/health/records/', headers=headers, json=reading)
    status = 'ANOMALY' if is_anomaly else 'NORMAL'
    elder_name = device.get('elder_name', 'Unknown')
    print(f'[{datetime.now().strftime("%H:%M:%S")}] [{status}] {elder_name} - '
          f'HR:{reading["heart_rate"]} BP:{reading["systolic_bp"]}/{reading["diastolic_bp"]} '
          f'SpO2:{reading["blood_oxygen"]} T:{reading["temperature"]}')
    return resp.status_code


def main():
    interval = int(os.environ.get('INTERVAL', '10'))
    print('=== IoT 设备模拟器启动 ===')
    print(f'API: {API_BASE}')
    print(f'发送间隔: {interval}秒')
    print(f'异常概率: {ANOMALY_CHANCE * 100}%')
    print()

    token = get_token()
    devices = get_devices(token)
    active_devices = [d for d in devices if d.get('elder')]
    print(f'找到 {len(active_devices)} 个绑定老人的设备\n')

    if not active_devices:
        print('没有可用设备，请先在系统中创建设备并绑定老人')
        return

    cycle = 0
    while True:
        cycle += 1
        print(f'--- 第 {cycle} 轮数据上报 ---')
        for device in active_devices:
            try:
                send_health_data(token, device)
            except requests.exceptions.RequestException as e:
                print(f'发送失败: {e}')
        print()
        time.sleep(interval)


if __name__ == '__main__':
    main()
