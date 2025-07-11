#!/usr/bin/env python3
"""
測試雙測試界面的簡單腳本
"""

import requests
import time
from bs4 import BeautifulSoup

def test_dual_interface():
    """測試雙測試界面功能"""
    base_url = "http://localhost:5000"
    
    print("🧪 開始測試雙測試界面...")
    
    # 1. 檢查主頁是否正常載入
    try:
        response = requests.get(base_url, timeout=10)
        if response.status_code != 200:
            print("❌ 主頁載入失敗")
            return False
        print("✅ 主頁載入成功")
    except Exception as e:
        print(f"❌ 無法連接到服務器: {e}")
        return False
    
    # 2. 解析HTML內容
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 檢查是否有兩個測試表單
        test_form_1 = soup.find('form', {'id': 'test-form'})
        test_form_2 = soup.find('form', {'id': 'test-form-2'})
        
        if not test_form_1:
            print("❌ 測試一表單未找到")
            return False
        print("✅ 測試一表單存在")
        
        if not test_form_2:
            print("❌ 測試二表單未找到")
            return False
        print("✅ 測試二表單存在")
        
    except Exception as e:
        print(f"❌ HTML解析失敗: {e}")
        return False
    
    # 3. 檢查測試一的關鍵元素
    print("\n📋 檢查測試一的元素...")
    test1_elements = [
        'model-select',
        'concurrent-requests', 
        'total-requests',
        'test-prompt',
        'start-test-btn',
        'stop-test-btn'
    ]
    
    for element_id in test1_elements:
        element = soup.find(attrs={'id': element_id})
        if element:
            print(f"  ✅ {element_id}: 存在")
        else:
            print(f"  ❌ {element_id}: 缺失")
    
    # 4. 檢查測試二的關鍵元素
    print("\n📋 檢查測試二的元素...")
    test2_elements = [
        'model-select-2',
        'test-mode-2',
        'initial-concurrent-2',
        'max-concurrent-2', 
        'test-duration-2',
        'ramp-interval-2',
        'test-prompts-2',
        'start-test-btn-2',
        'stop-test-btn-2',
        'preview-config-btn-2'
    ]
    
    for element_id in test2_elements:
        element = soup.find(attrs={'id': element_id})
        if element:
            print(f"  ✅ {element_id}: 存在")
        else:
            print(f"  ❌ {element_id}: 缺失")
    
    # 5. 檢查CSS類別
    print("\n🎨 檢查CSS樣式...")
    test_config_cards = soup.find_all(class_='test-config-card')
    if len(test_config_cards) >= 2:
        print(f"  ✅ 找到 {len(test_config_cards)} 個測試配置卡片")
    else:
        print(f"  ⚠️ 只找到 {len(test_config_cards)} 個測試配置卡片")
    
    # 6. 檢查功能提示
    development_notice = soup.find(class_='development-notice')
    if development_notice:
        print("  ✅ 功能開發中提示存在")
    else:
        print("  ❌ 功能開發中提示缺失")
    
    # 7. 檢查JavaScript文件
    print("\n📜 檢查JavaScript文件...")
    try:
        js_response = requests.get(f"{base_url}/static/js/app_simple.js", timeout=5)
        if js_response.status_code == 200:
            print("  ✅ JavaScript文件載入成功")
            
            # 檢查是否包含測試二相關函數
            js_content = js_response.text
            test2_functions = [
                'setupTest2EventListeners',
                'refreshModelsForTest2',
                'startAdvancedTest',
                'previewAdvancedTestConfig'
            ]
            
            for func_name in test2_functions:
                if func_name in js_content:
                    print(f"    ✅ {func_name}: 存在")
                else:
                    print(f"    ❌ {func_name}: 缺失")
        else:
            print("  ❌ JavaScript文件載入失敗")
    except Exception as e:
        print(f"  ❌ JavaScript文件檢查失敗: {e}")
    
    print("\n" + "="*50)
    print("🎉 雙測試界面檢查完成！")
    print("💡 您現在可以在瀏覽器中查看新的雙測試界面")
    print("🌐 請訪問: http://localhost:5000")
    print("="*50)
    
    return True

def main():
    """主函數"""
    print("=" * 50)
    print("🚀 Ollama 壓力測試 - 雙測試界面檢查")
    print("=" * 50)
    
    success = test_dual_interface()
    
    if success:
        print("\n✨ 界面檢查通過！")
        print("\n📝 功能說明:")
        print("  • 測試一: 基礎壓力測試 (完全功能)")
        print("  • 測試二: 進階性能測試 (界面完成，功能開發中)")
        print("\n🔧 測試二功能:")
        print("  • 漸增負載測試")
        print("  • 突發負載測試") 
        print("  • 耐久性測試")
        print("  • 混合負載測試")
        print("  • 系統資源監控")
        print("  • 詳細日誌記錄")
        print("  • 自動匯出結果")
    else:
        print("\n❌ 界面檢查失敗")
        print("🔧 請檢查服務器日誌以獲取更多信息")

if __name__ == "__main__":
    main()
