"""
測試llama3:8b模型
"""

import requests
import json

def test_llama3():
    print("🧪 測試llama3:8b模型...")
    
    try:
        query_data = {
            "model": "llama3:8b",
            "prompt": "Hello, this is a test. Please respond with 'Test successful'.",
            "stream": False
        }
        
        print(f"  📤 發送查詢...")
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=query_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✅ 查詢成功!")
            print(f"  📝 響應: {result.get('response', 'N/A')}")
            print(f"  ⏱️ 總時間: {result.get('total_duration', 0) / 1e9:.2f} 秒")
            print(f"  🔢 評估計數: {result.get('eval_count', 0)}")
        else:
            print(f"  ❌ 查詢失敗: {response.status_code}")
            print(f"  📄 錯誤: {response.text}")
            
    except Exception as e:
        print(f"  ❌ 查詢測試失敗: {e}")

if __name__ == "__main__":
    test_llama3()
