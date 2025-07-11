"""
測試Ollama連接和模型可用性
"""

import requests
import json

def test_ollama_connection():
    print("🔍 測試Ollama連接...")
    
    # 1. 測試Ollama服務器
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"  ✅ Ollama服務器正常運行")
            print(f"  📋 可用模型數量: {len(models.get('models', []))}")
            
            for model in models.get('models', [])[:5]:  # 顯示前5個模型
                print(f"    - {model.get('name', 'N/A')}")
                
            # 檢查llama3:8b是否存在
            model_names = [m.get('name', '') for m in models.get('models', [])]
            if 'llama3:8b' in model_names:
                print(f"  ✅ llama3:8b 模型可用")
            else:
                print(f"  ❌ llama3:8b 模型不可用")
                print(f"  💡 建議使用: {model_names[0] if model_names else 'N/A'}")
                
        else:
            print(f"  ❌ Ollama服務器響應錯誤: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 無法連接到Ollama服務器: {e}")
        print(f"  💡 請確保Ollama正在運行: ollama serve")
    
    # 2. 測試簡單查詢
    print("\n🧪 測試簡單查詢...")
    try:
        # 獲取第一個可用模型
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            if models:
                test_model = models[0]['name']
                print(f"  🎯 使用模型: {test_model}")
                
                # 發送測試查詢
                query_data = {
                    "model": test_model,
                    "prompt": "Hello, this is a test. Please respond with 'Test successful'.",
                    "stream": False
                }
                
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json=query_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"  ✅ 查詢成功!")
                    print(f"  📝 響應: {result.get('response', 'N/A')[:100]}...")
                else:
                    print(f"  ❌ 查詢失敗: {response.status_code}")
                    print(f"  📄 錯誤: {response.text}")
            else:
                print(f"  ❌ 沒有可用模型")
    except Exception as e:
        print(f"  ❌ 查詢測試失敗: {e}")

if __name__ == "__main__":
    test_ollama_connection()
