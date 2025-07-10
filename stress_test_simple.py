import threading
import time
import uuid
import queue
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
from ollama_client import OllamaClient
import statistics

class StressTestManager:
    def __init__(self):
        self.active_tests = {}
        self.test_results = {}
        self.lock = threading.Lock()
    
    def start_test(self, config: Dict) -> str:
        """開始壓力測試"""
        test_id = str(uuid.uuid4())
        
        with self.lock:
            self.active_tests[test_id] = {
                'config': config,
                'status': 'starting',
                'start_time': datetime.now(),
                'progress': 0,
                'completed_requests': 0,
                'failed_requests': 0,
                'results': [],
                'stop_requested': False,
                'current_results': []
            }
        
        # 在新線程中運行測試
        test_thread = threading.Thread(
            target=self._run_stress_test,
            args=(test_id, config),
            daemon=True
        )
        test_thread.start()
        
        return test_id
    
    def stop_test(self, test_id: str) -> bool:
        """停止壓力測試"""
        with self.lock:
            if test_id in self.active_tests:
                self.active_tests[test_id]['stop_requested'] = True
                self.active_tests[test_id]['status'] = 'stopping'
                return True
            return False
    
    def get_test_status(self, test_id: str) -> Optional[Dict]:
        """獲取測試狀態"""
        with self.lock:
            if test_id in self.active_tests:
                return self.active_tests[test_id].copy()
            elif test_id in self.test_results:
                return self.test_results[test_id].copy()
            return None
    
    def _run_stress_test(self, test_id: str, config: Dict):
        """執行壓力測試的主要邏輯"""
        try:
            # 更新狀態為運行中
            with self.lock:
                self.active_tests[test_id]['status'] = 'running'
            
            # 執行測試
            self._execute_test(test_id, config)
            
        except Exception as e:
            with self.lock:
                self.active_tests[test_id]['status'] = 'error'
                self.active_tests[test_id]['error'] = str(e)
        
        finally:
            # 移動到結果存儲並清理活動測試
            with self.lock:
                if test_id in self.active_tests:
                    test_data = self.active_tests.pop(test_id)
                    test_data['end_time'] = datetime.now()
                    test_data['duration'] = (test_data['end_time'] - test_data['start_time']).total_seconds()
                    self.test_results[test_id] = test_data
    
    def _execute_test(self, test_id: str, config: Dict):
        """執行具體的測試邏輯"""
        model = config['model']
        concurrent_requests = config['concurrent_requests']
        total_requests = config['total_requests']
        prompt = config['prompt']
        
        # 創建Ollama客戶端
        ollama_client = OllamaClient()
        
        # 檢查服務器可用性
        if not ollama_client.is_server_available():
            raise Exception("Ollama server is not available")
        
        # 創建任務隊列
        task_queue = queue.Queue()
        for i in range(total_requests):
            task_queue.put(i)
        
        # 結果收集
        results = []
        completed_count = 0
        failed_count = 0
        
        def worker():
            """工作線程函數"""
            nonlocal completed_count, failed_count
            
            while True:
                try:
                    # 檢查是否需要停止
                    with self.lock:
                        if self.active_tests[test_id]['stop_requested']:
                            break
                    
                    # 獲取任務
                    try:
                        task_id = task_queue.get_nowait()
                    except queue.Empty:
                        break
                    
                    # 執行請求
                    start_time = time.time()
                    result = ollama_client.generate_response(model, prompt)
                    end_time = time.time()
                    
                    # 記錄結果
                    result['task_id'] = task_id
                    result['worker_thread'] = threading.current_thread().name
                    results.append(result)
                    
                    # 更新計數器
                    if result['success']:
                        completed_count += 1
                    else:
                        failed_count += 1
                    
                    # 更新進度
                    progress = ((completed_count + failed_count) / total_requests) * 100
                    
                    with self.lock:
                        self.active_tests[test_id]['progress'] = progress
                        self.active_tests[test_id]['completed_requests'] = completed_count
                        self.active_tests[test_id]['failed_requests'] = failed_count
                        self.active_tests[test_id]['current_results'] = results.copy()
                    
                    task_queue.task_done()
                    
                except Exception as e:
                    failed_count += 1
                    print(f"Worker error: {e}")
                    
                    with self.lock:
                        self.active_tests[test_id]['failed_requests'] = failed_count
        
        # 啟動工作線程
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(worker) for _ in range(concurrent_requests)]
            
            # 等待所有任務完成或停止請求
            while True:
                with self.lock:
                    if self.active_tests[test_id]['stop_requested']:
                        break
                
                if task_queue.empty() and all(f.done() for f in futures):
                    break
                
                time.sleep(0.1)
        
        # 計算統計資訊
        stats = self._calculate_statistics(results)
        
        # 更新最終狀態
        with self.lock:
            self.active_tests[test_id]['status'] = 'completed'
            self.active_tests[test_id]['progress'] = 100
            self.active_tests[test_id]['statistics'] = stats
            self.active_tests[test_id]['final_results'] = results  # 保存完整結果用於圖表
    
    def _calculate_statistics(self, results: List[Dict]) -> Dict:
        """計算測試統計資訊"""
        if not results:
            return {}
        
        successful_results = [r for r in results if r['success']]
        failed_results = [r for r in results if not r['success']]
        
        if successful_results:
            response_times = [r['response_time'] for r in successful_results]
            
            stats = {
                'total_requests': len(results),
                'successful_requests': len(successful_results),
                'failed_requests': len(failed_results),
                'success_rate': (len(successful_results) / len(results)) * 100,
                'response_time_stats': {
                    'min': min(response_times),
                    'max': max(response_times),
                    'mean': statistics.mean(response_times),
                    'median': statistics.median(response_times),
                    'std_dev': statistics.stdev(response_times) if len(response_times) > 1 else 0
                },
                'requests_per_second': len(successful_results) / sum(response_times) if sum(response_times) > 0 else 0
            }
        else:
            stats = {
                'total_requests': len(results),
                'successful_requests': 0,
                'failed_requests': len(failed_results),
                'success_rate': 0,
                'response_time_stats': {},
                'requests_per_second': 0
            }
        
        return stats

if __name__ == "__main__":
    # 測試壓力測試管理器
    manager = StressTestManager()
    
    # 模擬測試配置
    test_config = {
        'model': 'llama3:8b',
        'concurrent_requests': 2,
        'total_requests': 5,
        'prompt': 'Hello, this is a test prompt.'
    }
    
    print("Starting stress test...")
    test_id = manager.start_test(test_config)
    print(f"Test ID: {test_id}")
    
    # 監控測試進度
    while True:
        status = manager.get_test_status(test_id)
        if status:
            print(f"Status: {status['status']}, Progress: {status['progress']:.1f}%")
            if status['status'] in ['completed', 'error', 'stopped']:
                if 'statistics' in status:
                    print("Final statistics:", status['statistics'])
                break
        time.sleep(1)
    
    print("Test completed!")
