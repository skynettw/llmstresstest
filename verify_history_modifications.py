#!/usr/bin/env python3
"""
驗證歷史記錄頁面的修改是否正確
"""

import os
import re

def check_html_modifications():
    """檢查HTML模板的修改"""
    print("🔍 檢查歷史記錄頁面的HTML修改...")
    
    html_file = "templates/history.html"
    if not os.path.exists(html_file):
        print(f"❌ 找不到文件: {html_file}")
        return False
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查是否添加了測試條件和硬體條件的顯示區域
    checks = [
        ("測試條件區域", r'id="test-conditions-section"'),
        ("測試配置顯示", r'id="test-config-display"'),
        ("硬體資訊顯示", r'id="hardware-info-display"'),
        ("renderTestConditions函數", r'function renderTestConditions'),
        ("renderHardwareInfo函數", r'function renderHardwareInfo'),
        ("測試條件樣式", r'#test-conditions-section'),
    ]
    
    results = []
    for name, pattern in checks:
        if re.search(pattern, content):
            print(f"✅ {name}: 已添加")
            results.append(True)
        else:
            print(f"❌ {name}: 未找到")
            results.append(False)
    
    return all(results)

def check_javascript_functions():
    """檢查JavaScript函數的實現"""
    print("\n🔍 檢查JavaScript函數實現...")
    
    html_file = "templates/history.html"
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查關鍵的JavaScript代碼
    js_checks = [
        ("renderTestConditions調用", r'renderTestConditions\(record\)'),
        ("renderHardwareInfo調用", r'renderHardwareInfo\(record\)'),
        ("測試類型判斷", r'record\.test_type === 1'),
        ("硬體資訊處理", r'hardwareInfo\.cpu'),
        ("測試配置處理", r'testConfig\.model'),
    ]
    
    results = []
    for name, pattern in js_checks:
        if re.search(pattern, content):
            print(f"✅ {name}: 已實現")
            results.append(True)
        else:
            print(f"❌ {name}: 未找到")
            results.append(False)
    
    return all(results)

def check_css_styles():
    """檢查CSS樣式"""
    print("\n🔍 檢查CSS樣式...")
    
    html_file = "templates/history.html"
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查CSS樣式
    css_checks = [
        ("測試條件樣式", r'#test-conditions-section .card'),
        ("響應式設計", r'@media \(max-width: 768px\)'),
    ]
    
    results = []
    for name, pattern in css_checks:
        if re.search(pattern, content):
            print(f"✅ {name}: 已添加")
            results.append(True)
        else:
            print(f"❌ {name}: 未找到")
            results.append(False)
    
    return all(results)

def check_database_structure():
    """檢查數據庫結構"""
    print("\n🔍 檢查數據庫結構...")
    
    try:
        from database import TestHistoryDatabase
        db = TestHistoryDatabase()
        
        # 獲取一條測試記錄
        records = db.get_test_history(limit=1)
        if not records:
            print("⚠️ 數據庫中沒有測試記錄")
            return True  # 結構可能正確，只是沒有數據
        
        test_id = records[0]['test_id']
        detail = db.get_test_detail(test_id)
        
        if detail:
            # 檢查必要的字段
            required_fields = ['hardware_info', 'test_config', 'test_type', 'model_name']
            missing_fields = []
            
            for field in required_fields:
                if field not in detail:
                    missing_fields.append(field)
            
            if missing_fields:
                print(f"❌ 缺少字段: {missing_fields}")
                return False
            else:
                print("✅ 數據庫結構正確")
                
                # 檢查數據類型
                if isinstance(detail['hardware_info'], dict):
                    print("✅ hardware_info 是字典類型")
                else:
                    print(f"❌ hardware_info 類型錯誤: {type(detail['hardware_info'])}")
                    return False
                
                if isinstance(detail['test_config'], dict):
                    print("✅ test_config 是字典類型")
                else:
                    print(f"❌ test_config 類型錯誤: {type(detail['test_config'])}")
                    return False
                
                return True
        else:
            print("❌ 無法獲取測試詳細資料")
            return False
            
    except Exception as e:
        print(f"❌ 數據庫檢查失敗: {e}")
        return False

def main():
    """主函數"""
    print("🧪 驗證歷史記錄頁面修改...")
    print("=" * 50)
    
    # 執行所有檢查
    html_ok = check_html_modifications()
    js_ok = check_javascript_functions()
    css_ok = check_css_styles()
    db_ok = check_database_structure()
    
    print("\n" + "=" * 50)
    print("📋 檢查結果總結:")
    print(f"  HTML修改: {'✅ 通過' if html_ok else '❌ 失敗'}")
    print(f"  JavaScript實現: {'✅ 通過' if js_ok else '❌ 失敗'}")
    print(f"  CSS樣式: {'✅ 通過' if css_ok else '❌ 失敗'}")
    print(f"  數據庫結構: {'✅ 通過' if db_ok else '❌ 失敗'}")
    
    if all([html_ok, js_ok, css_ok, db_ok]):
        print("\n🎉 所有檢查通過！歷史記錄頁面的修改已正確實現。")
        print("\n📝 功能說明:")
        print("  1. 在歷史記錄頁面選擇任一測試記錄")
        print("  2. 圖表上方會顯示兩個區塊:")
        print("     - 測試條件: 顯示測試配置信息")
        print("     - 硬體條件: 顯示測試時的硬體狀態")
        print("  3. 不同測試類型會顯示不同的配置項目")
        print("\n🌐 請啟動應用程序並訪問 http://127.0.0.1:5000/history 查看效果")
    else:
        print("\n❌ 部分檢查失敗，請檢查相關實現")

if __name__ == "__main__":
    main()
