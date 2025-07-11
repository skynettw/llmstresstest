"""
測試二 - 多用戶並發測試演示腳本
展示如何使用新的多用戶測試功能
"""

import requests
import json
import time

def demo_multi_user_test():
    base_url = "http://localhost:5000"
    
    print("🎯 測試二 - 多用戶並發測試演示")
    print("=" * 50)
    
    # 演示配置
    demo_configs = [
        {
            "name": "小規模測試 (2用戶)",
            "config": {
                "model": "llama3:8b",
                "user_count": 2,
                "queries_per_user": 3,
                "concurrent_limit": 2,
                "delay_between_queries": 0.5,
                "use_random_prompts": True,
                "enable_tpm_monitoring": True,
                "enable_detailed_logging": False
            }
        },
        {
            "name": "中規模測試 (5用戶)",
            "config": {
                "model": "llama3:8b",
                "user_count": 5,
                "queries_per_user": 4,
                "concurrent_limit": 3,
                "delay_between_queries": 0.3,
                "use_random_prompts": True,
                "enable_tpm_monitoring": True,
                "enable_detailed_logging": False
            }
        }
    ]
    
    for demo in demo_configs:
        print(f"\n🧪 {demo['name']}")
        print("-" * 30)
        
        config = demo['config']
        print(f"📋 配置:")
        print(f"  - 用戶數量: {config['user_count']}")
        print(f"  - 每用戶查詢: {config['queries_per_user']}")
        print(f"  - 並發限制: {config['concurrent_limit']}")
        print(f"  - 查詢間隔: {config['delay_between_queries']}秒")
        
        # 啟動測試
        try:
            response = requests.post(
                f"{base_url}/api/start_multi_user_test",
                json=config,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    test_id = result.get('test_id')
                    print(f"✅ 測試啟動成功! ID: {test_id[:8]}...")
                    
                    # 監控進度
                    start_time = time.time()
                    last_progress = 0
                    
                    while True:
                        try:
                            status_response = requests.get(
                                f"{base_url}/api/multi_user_test_status/{test_id}",
                                timeout=5
                            )
                            
                            if status_response.status_code == 200:
                                status = status_response.json()
                                progress = status.get('progress', 0)
                                
                                # 只在進度有變化時顯示
                                if progress != last_progress:
                                    print(f"📊 進度: {progress:.1f}% | 狀態: {status.get('status', 'unknown')}")
                                    last_progress = progress
                                
                                if status.get('status') in ['completed', 'error', 'stopped']:
                                    elapsed_time = time.time() - start_time
                                    print(f"🎯 測試完成! 耗時: {elapsed_time:.1f}秒")
                                    
                                    if 'statistics' in status:
                                        stats = status['statistics']
                                        print(f"📈 結果統計:")
                                        print(f"  - 總查詢數: {stats.get('total_queries', 0)}")
                                        print(f"  - 成功查詢: {stats.get('successful_queries', 0)}")
                                        print(f"  - 成功率: {(stats.get('successful_queries', 0) / max(stats.get('total_queries', 1), 1) * 100):.1f}%")
                                        print(f"  - 總Token數: {stats.get('total_tokens', 0)}")
                                        print(f"  - 平均TPM: {stats.get('average_tpm', 0):.1f} tokens/分鐘")
                                        print(f"  - 峰值TPM: {stats.get('peak_tpm', 0):.1f} tokens/分鐘")
                                        print(f"  - 平均響應時間: {stats.get('average_response_time', 0):.2f}秒")
                                    break
                            else:
                                print(f"❌ 狀態查詢失敗: {status_response.status_code}")
                                break
                                
                        except Exception as e:
                            print(f"❌ 狀態查詢異常: {e}")
                            break
                        
                        time.sleep(2)
                        
                        # 超時保護
                        if time.time() - start_time > 300:  # 5分鐘超時
                            print("⏰ 測試超時，停止監控")
                            break
                    
                else:
                    print(f"❌ 測試啟動失敗: {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ API返回錯誤: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 請求失敗: {e}")
        
        print("\n" + "=" * 50)
    
    print("\n🎉 演示完成!")
    print("\n💡 使用說明:")
    print("1. 在瀏覽器中打開 http://localhost:5000")
    print("2. 選擇「測試二 - 多用戶並發測試」")
    print("3. 配置測試參數:")
    print("   - 選擇模型 (建議: llama3:8b)")
    print("   - 設定用戶數量 (1-10)")
    print("   - 設定每用戶查詢次數")
    print("   - 調整並發限制和查詢間隔")
    print("4. 選擇使用內建50組隨機提示詞或自定義提示詞")
    print("5. 點擊「開始多用戶測試」")
    print("6. 觀察實時進度和TPM統計")

if __name__ == "__main__":
    demo_multi_user_test()
