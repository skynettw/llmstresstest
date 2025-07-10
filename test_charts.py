#!/usr/bin/env python3
"""
測試圖表功能的簡單腳本
"""

import requests
import json
import time

def test_charts_api():
    """測試圖表 API 功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 開始測試圖表功能...")
    
    # 1. 檢查服務器是否運行
    try:
        response = requests.get(f"{base_url}/api/models", timeout=5)
        if response.status_code != 200:
            print("❌ 服務器未正常運行")
            return False
        print("✅ 服務器運行正常")
    except Exception as e:
        print(f"❌ 無法連接到服務器: {e}")
        return False
    
    # 2. 獲取可用模型
    try:
        models = response.json()
        if not models:
            print("❌ 沒有可用的模型")
            return False
        
        test_model = models[0]['name']
        print(f"✅ 找到測試模型: {test_model}")
    except Exception as e:
        print(f"❌ 獲取模型列表失敗: {e}")
        return False
    
    # 3. 啟動測試
    test_config = {
        "model": test_model,
        "concurrent_requests": 2,
        "total_requests": 5,
        "prompt": "Hello, this is a test prompt for chart generation."
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/start_test",
            json=test_config,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"❌ 啟動測試失敗: {response.text}")
            return False
        
        result = response.json()
        if not result.get('success'):
            print(f"❌ 測試啟動失敗: {result}")
            return False
        
        test_id = result['test_id']
        print(f"✅ 測試已啟動，ID: {test_id}")
        
    except Exception as e:
        print(f"❌ 啟動測試時發生錯誤: {e}")
        return False
    
    # 4. 等待測試完成
    print("⏳ 等待測試完成...")
    max_wait_time = 120  # 最多等待2分鐘
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{base_url}/api/test_status/{test_id}", timeout=10)
            if response.status_code == 200:
                status = response.json()
                current_status = status.get('status', 'unknown')
                progress = status.get('progress', 0)
                
                print(f"📊 測試狀態: {current_status}, 進度: {progress:.1f}%")
                
                if current_status == 'completed':
                    print("✅ 測試完成！")
                    break
                elif current_status in ['error', 'stopped']:
                    print(f"❌ 測試異常結束: {current_status}")
                    return False
            
            time.sleep(2)  # 每2秒檢查一次
            
        except Exception as e:
            print(f"⚠️ 檢查測試狀態時發生錯誤: {e}")
            time.sleep(2)
    else:
        print("❌ 測試超時")
        return False
    
    # 5. 測試圖表 API
    print("📈 測試圖表 API...")
    try:
        response = requests.get(f"{base_url}/api/test_charts/{test_id}", timeout=30)
        
        if response.status_code != 200:
            print(f"❌ 獲取圖表數據失敗: {response.status_code} - {response.text}")
            return False
        
        charts_data = response.json()
        
        # 檢查圖表數據
        expected_charts = [
            'response_time_histogram',
            'response_time_timeline', 
            'success_rate_pie',
            'response_time_box'
        ]
        
        available_charts = []
        for chart_name in expected_charts:
            if chart_name in charts_data:
                available_charts.append(chart_name)
                # 驗證圖表數據是否為有效的 JSON
                try:
                    json.loads(charts_data[chart_name])
                    print(f"✅ {chart_name}: 數據格式正確")
                except json.JSONDecodeError:
                    print(f"❌ {chart_name}: 數據格式錯誤")
                    return False
            else:
                print(f"⚠️ {chart_name}: 圖表數據不存在")
        
        if available_charts:
            print(f"✅ 成功生成 {len(available_charts)} 個圖表")
            print(f"📊 可用圖表: {', '.join(available_charts)}")
            return True
        else:
            print("❌ 沒有生成任何圖表")
            return False
            
    except Exception as e:
        print(f"❌ 測試圖表 API 時發生錯誤: {e}")
        return False

def main():
    """主函數"""
    print("=" * 50)
    print("🚀 Ollama 壓力測試 - 圖表功能測試")
    print("=" * 50)
    
    success = test_charts_api()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 圖表功能測試通過！")
        print("💡 您現在可以在網頁界面中查看測試結果的圖表")
        print("🌐 請訪問: http://localhost:5000")
    else:
        print("❌ 圖表功能測試失敗")
        print("🔧 請檢查服務器日誌以獲取更多信息")
    print("=" * 50)

if __name__ == "__main__":
    main()
