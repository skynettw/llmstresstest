"""
測試多用戶API的簡單腳本
"""

import requests
import json
import time

def test_multi_user_api():
    base_url = "http://localhost:5000"
    
    print("🧪 測試多用戶API...")
    
    # 1. 測試模型列表API
    print("\n1. 測試模型列表API...")
    try:
        response = requests.get(f"{base_url}/api/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"  ✅ 獲取到 {len(models)} 個模型")
            if models:
                print(f"  📋 第一個模型: {models[0].get('name', 'N/A')}")
        else:
            print(f"  ❌ API返回錯誤: {response.status_code}")
    except Exception as e:
        print(f"  ❌ 請求失敗: {e}")
    
    # 2. 測試多用戶測試配置
    print("\n2. 測試多用戶測試配置...")
    test_config = {
        "model": "llama3:8b",  # 假設這個模型存在
        "user_count": 2,
        "queries_per_user": 3,
        "concurrent_limit": 2,
        "delay_between_queries": 0.5,
        "use_random_prompts": True,
        "enable_tpm_monitoring": True,
        "enable_detailed_logging": False
    }
    
    print(f"  📝 測試配置: {json.dumps(test_config, indent=2, ensure_ascii=False)}")
    
    # 3. 啟動多用戶測試
    print("\n3. 啟動多用戶測試...")
    try:
        response = requests.post(
            f"{base_url}/api/start_multi_user_test",
            json=test_config,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                test_id = result.get('test_id')
                print(f"  ✅ 測試啟動成功! Test ID: {test_id}")
                
                # 4. 監控測試進度
                print("\n4. 監控測試進度...")
                for i in range(30):  # 最多監控30次
                    try:
                        status_response = requests.get(
                            f"{base_url}/api/multi_user_test_status/{test_id}",
                            timeout=5
                        )
                        
                        if status_response.status_code == 200:
                            status = status_response.json()
                            print(f"  📊 進度: {status.get('progress', 0):.1f}% | 狀態: {status.get('status', 'unknown')}")
                            
                            if status.get('status') in ['completed', 'error', 'stopped']:
                                print(f"  🎯 測試完成! 最終狀態: {status.get('status')}")
                                if 'statistics' in status:
                                    stats = status['statistics']
                                    print(f"  📈 統計結果:")
                                    print(f"    - 總查詢數: {stats.get('total_queries', 0)}")
                                    print(f"    - 成功查詢: {stats.get('successful_queries', 0)}")
                                    print(f"    - 平均TPM: {stats.get('average_tpm', 0):.1f}")
                                break
                        else:
                            print(f"  ❌ 狀態查詢失敗: {status_response.status_code}")
                            break
                            
                    except Exception as e:
                        print(f"  ❌ 狀態查詢異常: {e}")
                        break
                    
                    time.sleep(2)  # 等待2秒再查詢
                
            else:
                print(f"  ❌ 測試啟動失敗: {result.get('error', 'Unknown error')}")
        else:
            print(f"  ❌ API返回錯誤: {response.status_code}")
            print(f"  📄 響應內容: {response.text}")
            
    except Exception as e:
        print(f"  ❌ 請求失敗: {e}")
    
    print("\n🎉 API測試完成!")

if __name__ == "__main__":
    test_multi_user_api()
