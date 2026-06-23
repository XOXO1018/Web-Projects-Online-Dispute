"""Full test: login -> list mediators with detailed error"""
import requests
import traceback

BASE = 'http://localhost:8000'

try:
    # 1. Login
    r = requests.post(f'{BASE}/api/v1/auth/login', json={
        'email': 'admin@zjfl.com',
        'password': 'admin123'
    }, timeout=5)
    print(f"Login status: {r.status_code}")
    login_data = r.json()
    print(f"Login response: {login_data}")
    
    if login_data.get('code') != 200:
        print("Login failed!")
        exit(1)
    
    token = login_data['data']['access_token']
    
    # 2. List mediators (exactly like frontend)
    r2 = requests.get(f'{BASE}/api/v1/admin/mediators', 
                       params={'page': 1, 'page_size': 50},
                       headers={'Authorization': f'Bearer {token}'},
                       timeout=5)
    print(f"\nMediators status: {r2.status_code}")
    print(f"Mediators response: {r2.text[:500]}")
    
    if r2.status_code == 200:
        data = r2.json()
        items = data.get('data', {}).get('data', [])
        print(f"\nMediators count: {len(items)}")
        for m in items[:2]:
            print(f"  Sample: {m}")
    
except Exception as e:
    traceback.print_exc()
