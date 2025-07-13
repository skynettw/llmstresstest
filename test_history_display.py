#!/usr/bin/env python3
"""
測試歷史記錄頁面的硬體條件和測試條件顯示功能
"""

import requests
import json
from database import TestHistoryDatabase

def test_history_api():
    """測試歷史記錄API"""
    base_url = "http://127.0.0.1:5000"
    
    print("🔍 測試歷史記錄API...")
    
    # 1. 測試獲取歷史記錄列表
    print("\n1. 測試獲取歷史記錄列表...")
    try:
        response = requests.get(f"{base_url}/api/history", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                records = data.get('records', [])
                print(f"✅ 成功獲取 {len(records)} 條歷史記錄")
                
                if records:
                    # 測試第一條記錄的詳細資料
                    test_id = records[0]['test_id']
                    print(f"📋 測試記錄ID: {test_id}")
                    
                    # 2. 測試獲取測試詳細資料
                    print(f"\n2. 測試獲取測試詳細資料...")
                    detail_response = requests.get(f"{base_url}/api/history/{test_id}", timeout=10)
                    
                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if detail_data.get('success'):
                            record = detail_data.get('record')
                            print("✅ 成功獲取測試詳細資料")
                            
                            # 檢查硬體資訊
                            hardware_info = record.get('hardware_info', {})
                            test_config = record.get('test_config', {})
                            
                            print(f"\n📊 測試條件資訊:")
                            print(f"  - 測試類型: {record.get('test_type')}")
                            print(f"  - 模型名稱: {record.get('model_name')}")
                            print(f"  - 測試時間: {record.get('test_time')}")
                            
                            if test_config:
                                print(f"  - 測試配置: {json.dumps(test_config, indent=2, ensure_ascii=False)}")
                            
                            print(f"\n🖥️ 硬體條件資訊:")
                            if hardware_info:
                                cpu = hardware_info.get('cpu', {})
                                memory = hardware_info.get('memory', {})
                                gpu = hardware_info.get('gpu', [])
                                system = hardware_info.get('system', {})
                                
                                print(f"  - CPU: {cpu.get('name', 'N/A')}")
                                print(f"  - CPU核心: {cpu.get('cores_physical', 'N/A')}核/{cpu.get('cores_logical', 'N/A')}線程")
                                print(f"  - CPU使用率: {cpu.get('usage_percent', 'N/A')}%")
                                print(f"  - 記憶體總量: {memory.get('total_gb', 'N/A')}GB")
                                print(f"  - 記憶體使用率: {memory.get('usage_percent', 'N/A')}%")
                                print(f"  - 系統: {system.get('system', 'N/A')} {system.get('release', '')}")
                                
                                if gpu:
                                    print(f"  - GPU: {gpu[0].get('name', 'N/A')}")
                                    print(f"  - GPU記憶體: {gpu[0].get('memory_total_mb', 'N/A')}MB")
                            else:
                                print("  - 硬體資訊不可用")
                            
                            return True
                        else:
                            print(f"❌ 獲取測試詳細資料失敗: {detail_data.get('error')}")
                    else:
                        print(f"❌ API請求失敗: {detail_response.status_code}")
                else:
                    print("⚠️ 沒有找到測試記錄")
            else:
                print(f"❌ API返回錯誤: {data.get('error')}")
        else:
            print(f"❌ API請求失敗: {response.status_code}")
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
    
    return False

def test_database_direct():
    """直接測試數據庫中的資料"""
    print("\n🗄️ 直接測試數據庫資料...")
    
    try:
        db = TestHistoryDatabase()
        records = db.get_test_history(limit=1)
        
        if records:
            test_id = records[0]['test_id']
            detail = db.get_test_detail(test_id)
            
            if detail:
                print("✅ 數據庫資料結構正確")
                print(f"  - 測試ID: {detail.get('test_id')}")
                print(f"  - 測試名稱: {detail.get('test_name')}")
                print(f"  - 測試類型: {detail.get('test_type')}")
                print(f"  - 硬體資訊類型: {type(detail.get('hardware_info'))}")
                print(f"  - 測試配置類型: {type(detail.get('test_config'))}")
                return True
            else:
                print("❌ 無法獲取測試詳細資料")
        else:
            print("❌ 數據庫中沒有記錄")
    except Exception as e:
        print(f"❌ 數據庫測試失敗: {e}")
    
    return False

if __name__ == "__main__":
    print("🧪 開始測試歷史記錄頁面功能...")
    
    # 測試數據庫
    db_success = test_database_direct()
    
    # 測試API
    api_success = test_history_api()
    
    if db_success and api_success:
        print("\n🎉 所有測試通過！歷史記錄頁面應該能正確顯示硬體條件和測試條件。")
        print("\n📝 請在瀏覽器中訪問 http://127.0.0.1:5000/history 查看效果")
        print("   1. 選擇任一歷史記錄")
        print("   2. 查看圖表上方是否顯示測試條件和硬體條件")
    else:
        print("\n❌ 測試失敗，請檢查相關配置")
