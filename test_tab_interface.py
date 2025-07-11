"""
測試Tab界面功能的腳本
驗證Tab切換和界面響應是否正常
"""

import requests
import time

def test_tab_interface():
    base_url = "http://localhost:5000"
    
    print("🎨 測試Tab界面功能...")
    print("=" * 50)
    
    # 測試主頁面是否正常載入
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code == 200:
            print("✅ 主頁面載入成功")
            
            # 檢查HTML內容是否包含Tab相關元素
            html_content = response.text
            
            # 檢查Tab導航
            if 'id="testTabs"' in html_content:
                print("✅ Tab導航元素存在")
            else:
                print("❌ Tab導航元素缺失")
            
            # 檢查測試一Tab
            if 'id="test1-tab"' in html_content and 'data-bs-target="#test1-pane"' in html_content:
                print("✅ 測試一Tab配置正確")
            else:
                print("❌ 測試一Tab配置有問題")
            
            # 檢查測試二Tab
            if 'id="test2-tab"' in html_content and 'data-bs-target="#test2-pane"' in html_content:
                print("✅ 測試二Tab配置正確")
            else:
                print("❌ 測試二Tab配置有問題")
            
            # 檢查Tab內容區域
            if 'id="test1-pane"' in html_content and 'id="test2-pane"' in html_content:
                print("✅ Tab內容區域存在")
            else:
                print("❌ Tab內容區域缺失")
            
            # 檢查表單元素
            if 'id="test-form"' in html_content and 'id="test-form-2"' in html_content:
                print("✅ 測試表單元素存在")
            else:
                print("❌ 測試表單元素缺失")
            
            # 檢查CSS樣式
            if '.nav-tabs' in html_content and '.tab-content' in html_content:
                print("✅ Tab CSS樣式已添加")
            else:
                print("❌ Tab CSS樣式缺失")
            
            # 檢查JavaScript事件處理
            if 'shown.bs.tab' in html_content:
                print("✅ Tab切換事件處理已添加")
            else:
                print("❌ Tab切換事件處理缺失")
                
        else:
            print(f"❌ 主頁面載入失敗: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 請求失敗: {e}")
    
    print("\n" + "=" * 50)
    
    # 測試API端點是否正常
    print("\n🔧 測試API端點...")
    
    # 測試模型列表API
    try:
        response = requests.get(f"{base_url}/api/models", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"✅ 模型API正常，獲取到 {len(models)} 個模型")
        else:
            print(f"❌ 模型API異常: {response.status_code}")
    except Exception as e:
        print(f"❌ 模型API請求失敗: {e}")
    
    # 測試硬體信息API
    try:
        response = requests.get(f"{base_url}/api/hardware", timeout=5)
        if response.status_code == 200:
            hardware = response.json()
            print("✅ 硬體信息API正常")
        else:
            print(f"❌ 硬體信息API異常: {response.status_code}")
    except Exception as e:
        print(f"❌ 硬體信息API請求失敗: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Tab界面測試完成!")
    
    print("\n💡 使用說明:")
    print("1. 在瀏覽器中訪問 http://localhost:5000")
    print("2. 您會看到一個統一的測試配置卡片")
    print("3. 卡片頂部有兩個Tab標籤：")
    print("   - 測試一 - 基礎壓力測試")
    print("   - 測試二 - 多用戶並發測試")
    print("4. 點擊不同的Tab可以切換測試類型")
    print("5. 每個Tab都有獨立的配置選項")
    print("6. 測試結果的圖表會根據測試類型自動切換")
    
    print("\n🎨 界面特色:")
    print("- 美觀的Tab設計，支援懸停效果")
    print("- 平滑的切換動畫")
    print("- 響應式佈局，適應不同螢幕尺寸")
    print("- 智能的圖表切換邏輯")
    print("- 統一的配置界面，減少視覺混亂")

if __name__ == "__main__":
    test_tab_interface()
