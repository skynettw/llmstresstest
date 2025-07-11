"""
測試圖表功能的腳本
驗證測試一和測試二的圖表是否正常工作
"""

import requests
import json
import time

def test_charts_functionality():
    base_url = "http://localhost:5000"
    
    print("🎨 測試圖表功能...")
    print("=" * 50)
    
    # 測試一：基礎壓力測試圖表
    print("\n📊 測試一 - 基礎壓力測試圖表")
    print("-" * 30)
    
    test1_config = {
        "model": "llama3:8b",
        "concurrent_requests": 2,
        "total_requests": 6,
        "prompt": "請用繁體中文簡短回答：什麼是人工智慧？"
    }
    
    try:
        # 啟動測試一
        response = requests.post(f"{base_url}/api/start_test", json=test1_config, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                test1_id = result.get('test_id')
                print(f"✅ 測試一啟動成功! ID: {test1_id[:8]}...")
                
                # 等待測試完成
                wait_for_test_completion(base_url, test1_id, "test_status")
                
                # 測試圖表API
                print("📈 測試圖表API...")
                chart_response = requests.get(f"{base_url}/api/test_charts/{test1_id}", timeout=10)
                if chart_response.status_code == 200:
                    charts = chart_response.json()
                    print(f"✅ 測試一圖表載入成功!")
                    print(f"  - 可用圖表: {list(charts.keys())}")
                else:
                    print(f"❌ 測試一圖表載入失敗: {chart_response.status_code}")
            else:
                print(f"❌ 測試一啟動失敗: {result.get('error')}")
        else:
            print(f"❌ 測試一API錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ 測試一異常: {e}")
    
    print("\n" + "=" * 50)
    
    # 測試二：多用戶並發測試圖表
    print("\n🎯 測試二 - 多用戶並發測試圖表")
    print("-" * 30)
    
    test2_config = {
        "model": "llama3:8b",
        "user_count": 2,
        "queries_per_user": 3,
        "concurrent_limit": 2,
        "delay_between_queries": 0.5,
        "use_random_prompts": True,
        "enable_tpm_monitoring": True,
        "enable_detailed_logging": False
    }
    
    try:
        # 啟動測試二
        response = requests.post(f"{base_url}/api/start_multi_user_test", json=test2_config, timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                test2_id = result.get('test_id')
                print(f"✅ 測試二啟動成功! ID: {test2_id[:8]}...")
                
                # 等待測試完成
                wait_for_test_completion(base_url, test2_id, "multi_user_test_status")
                
                # 測試圖表API
                print("📈 測試多用戶圖表API...")
                chart_response = requests.get(f"{base_url}/api/multi_user_test_charts/{test2_id}", timeout=10)
                if chart_response.status_code == 200:
                    charts = chart_response.json()
                    print(f"✅ 測試二圖表載入成功!")
                    print(f"  - 可用圖表: {list(charts.keys())}")
                    
                    # 檢查特定圖表
                    expected_charts = ['tpm_timeline', 'user_distribution', 'user_success_rate', 'response_vs_tokens']
                    for chart_name in expected_charts:
                        if chart_name in charts:
                            print(f"  ✅ {chart_name} 圖表已生成")
                        else:
                            print(f"  ❌ {chart_name} 圖表缺失")
                else:
                    print(f"❌ 測試二圖表載入失敗: {chart_response.status_code}")
                    print(f"  錯誤內容: {chart_response.text}")
            else:
                print(f"❌ 測試二啟動失敗: {result.get('error')}")
        else:
            print(f"❌ 測試二API錯誤: {response.status_code}")
    except Exception as e:
        print(f"❌ 測試二異常: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 圖表功能測試完成!")
    
    print("\n💡 使用建議:")
    print("1. 在瀏覽器中訪問 http://localhost:5000")
    print("2. 執行測試一，完成後查看基礎壓力測試圖表")
    print("3. 執行測試二，完成後查看多用戶並發測試圖表")
    print("4. 圖表會根據測試類型自動切換顯示")

def wait_for_test_completion(base_url, test_id, status_endpoint):
    """等待測試完成"""
    print("⏳ 等待測試完成...")
    
    for i in range(60):  # 最多等待60次
        try:
            if status_endpoint == "test_status":
                status_response = requests.get(f"{base_url}/api/{status_endpoint}/{test_id}", timeout=5)
            else:
                status_response = requests.get(f"{base_url}/api/{status_endpoint}/{test_id}", timeout=5)
            
            if status_response.status_code == 200:
                status = status_response.json()
                progress = status.get('progress', 0)
                test_status = status.get('status', 'unknown')
                
                if i % 5 == 0:  # 每5次顯示一次進度
                    print(f"  📊 進度: {progress:.1f}% | 狀態: {test_status}")
                
                if test_status in ['completed', 'error', 'stopped']:
                    print(f"  🎯 測試完成! 最終狀態: {test_status}")
                    return True
            else:
                print(f"  ❌ 狀態查詢失敗: {status_response.status_code}")
                return False
                
        except Exception as e:
            print(f"  ❌ 狀態查詢異常: {e}")
            return False
        
        time.sleep(2)
    
    print("  ⏰ 測試超時")
    return False

if __name__ == "__main__":
    test_charts_functionality()
