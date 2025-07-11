"""
多用戶並發測試管理器
實現測試二的核心邏輯：模擬多個用戶同時使用不同提示詞查詢同一模型
"""

import threading
import time
import uuid
import queue
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

from multi_user_test_config import (
    MultiUserTestConfig, UserSession, QueryResult,
    MultiUserTestResult, COMMON_PROMPTS, assign_prompts_to_users,
    calculate_tpm
)
from ollama_client import OllamaClient
from database import db
from hardware_info import get_hardware_info


class MultiUserStressTestManager:
    """多用戶壓力測試管理器"""
    
    def __init__(self):
        self.active_tests = {}
        self.test_results = {}
        self.lock = threading.Lock()
    
    def start_multi_user_test(self, config_dict: Dict) -> str:
        """開始多用戶測試"""
        test_id = str(uuid.uuid4())
        
        try:
            # 創建測試配置
            config = self._create_config_from_dict(config_dict)
            
            # 初始化測試結果
            test_result = MultiUserTestResult(
                test_id=test_id,
                config=config,
                start_time=datetime.now()
            )
            
            with self.lock:
                self.active_tests[test_id] = {
                    'config': config,
                    'result': test_result,
                    'status': 'starting',
                    'progress': 0,
                    'stop_requested': False,
                    'current_tpm': 0.0,
                    'active_users': 0
                }
            
            # 在新線程中運行測試
            test_thread = threading.Thread(
                target=self._run_multi_user_test,
                args=(test_id, config, test_result),
                daemon=True
            )
            test_thread.start()
            
            return test_id
            
        except Exception as e:
            with self.lock:
                self.active_tests[test_id] = {
                    'status': 'error',
                    'error': str(e),
                    'progress': 0
                }
            raise e
    
    def _create_config_from_dict(self, config_dict: Dict) -> MultiUserTestConfig:
        """從字典創建配置對象"""
        # 處理提示詞
        custom_prompts = None
        if config_dict.get('use_random_prompts', True):
            # 使用隨機提示詞
            pass
        else:
            # 使用自定義提示詞
            custom_prompts_text = config_dict.get('custom_prompts', '')
            if custom_prompts_text:
                custom_prompts = [
                    prompt.strip() for prompt in custom_prompts_text.split('\n')
                    if prompt.strip()
                ]
        
        return MultiUserTestConfig(
            model=config_dict['model'],
            user_count=int(config_dict['user_count']),
            queries_per_user=int(config_dict['queries_per_user']),
            use_random_prompts=config_dict.get('use_random_prompts', True),
            custom_prompts=custom_prompts,
            concurrent_limit=int(config_dict.get('concurrent_limit', 10)),
            delay_between_queries=float(config_dict.get('delay_between_queries', 0.5)),
            enable_tpm_monitoring=config_dict.get('enable_tpm_monitoring', True),
            enable_detailed_logging=config_dict.get('enable_detailed_logging', False)
        )
    
    def _run_multi_user_test(self, test_id: str, config: MultiUserTestConfig, result: MultiUserTestResult):
        """運行多用戶測試的主邏輯"""
        try:
            with self.lock:
                self.active_tests[test_id]['status'] = 'running'
            
            # 創建Ollama客戶端
            ollama_client = OllamaClient()
            
            # 檢查服務器可用性
            if not ollama_client.is_server_available():
                raise Exception("Ollama server is not available")
            
            # 為每個用戶分配提示詞
            if config.use_random_prompts:
                user_prompts = assign_prompts_to_users(config.user_count, config.queries_per_user)
            else:
                user_prompts = self._assign_custom_prompts(config)
            
            # 初始化用戶會話
            for user_id in range(1, config.user_count + 1):
                result.user_sessions[user_id] = UserSession(
                    user_id=user_id,
                    assigned_prompts=user_prompts[user_id]
                )
            
            # 創建任務隊列
            task_queue = queue.Queue()
            total_tasks = config.user_count * config.queries_per_user
            
            # 為每個用戶的每個查詢創建任務
            for user_id in range(1, config.user_count + 1):
                for query_index, prompt in enumerate(user_prompts[user_id]):
                    task_queue.put({
                        'user_id': user_id,
                        'query_index': query_index,
                        'prompt': prompt
                    })
            
            # 執行並發測試
            self._execute_concurrent_queries(
                test_id, config, result, task_queue, total_tasks, ollama_client
            )
            
            # 計算最終統計
            self._calculate_final_statistics(result)
            
            with self.lock:
                self.active_tests[test_id]['status'] = 'completed'
                self.active_tests[test_id]['progress'] = 100
                self.test_results[test_id] = result

                # 保存測試結果到資料庫
                self._save_multi_user_test_to_database(test_id, config, result)

        except Exception as e:
            with self.lock:
                self.active_tests[test_id]['status'] = 'error'
                self.active_tests[test_id]['error'] = str(e)
    
    def _assign_custom_prompts(self, config: MultiUserTestConfig) -> Dict[int, List[str]]:
        """為用戶分配自定義提示詞"""
        user_prompts = {}
        prompts = config.custom_prompts or COMMON_PROMPTS
        
        for user_id in range(1, config.user_count + 1):
            # 每個用戶隨機選擇提示詞
            if len(prompts) >= config.queries_per_user:
                user_prompts[user_id] = random.sample(prompts, config.queries_per_user)
            else:
                # 如果提示詞不夠，則重複使用
                user_prompts[user_id] = random.choices(prompts, k=config.queries_per_user)
        
        return user_prompts
    
    def _execute_concurrent_queries(self, test_id: str, config: MultiUserTestConfig, 
                                  result: MultiUserTestResult, task_queue: queue.Queue,
                                  total_tasks: int, ollama_client: OllamaClient):
        """執行並發查詢"""
        completed_tasks = 0
        
        with ThreadPoolExecutor(max_workers=config.concurrent_limit) as executor:
            # 提交所有任務
            futures = []
            
            while not task_queue.empty() and not self.active_tests[test_id]['stop_requested']:
                try:
                    task = task_queue.get_nowait()
                    future = executor.submit(
                        self._execute_single_query,
                        test_id, config, task, ollama_client
                    )
                    futures.append(future)
                    
                    # 控制並發數量
                    if len(futures) >= config.concurrent_limit:
                        # 等待一些任務完成
                        for future in as_completed(futures[:config.concurrent_limit//2]):
                            query_result = future.result()
                            if query_result:
                                result.query_results.append(query_result)
                                completed_tasks += 1
                                
                                # 更新進度
                                progress = (completed_tasks / total_tasks) * 100
                                with self.lock:
                                    self.active_tests[test_id]['progress'] = progress
                        
                        # 移除已完成的futures
                        futures = [f for f in futures if not f.done()]
                    
                    # 查詢間隔
                    if config.delay_between_queries > 0:
                        time.sleep(config.delay_between_queries)
                        
                except queue.Empty:
                    break
            
            # 等待剩餘任務完成
            for future in as_completed(futures):
                if self.active_tests[test_id]['stop_requested']:
                    break
                    
                query_result = future.result()
                if query_result:
                    result.query_results.append(query_result)
                    completed_tasks += 1
                    
                    # 更新進度
                    progress = (completed_tasks / total_tasks) * 100
                    with self.lock:
                        self.active_tests[test_id]['progress'] = progress
    
    def _execute_single_query(self, test_id: str, config: MultiUserTestConfig, 
                            task: Dict, ollama_client: OllamaClient) -> Optional[QueryResult]:
        """執行單個查詢"""
        if self.active_tests[test_id]['stop_requested']:
            return None
        
        user_id = task['user_id']
        prompt = task['prompt']
        start_time = time.time()
        timestamp = datetime.now()
        
        try:
            # 更新活躍用戶數
            with self.lock:
                self.active_tests[test_id]['active_users'] = len(set(
                    task['user_id'] for task in [task]  # 簡化版本，實際應該追蹤所有活躍用戶
                ))
            
            # 執行查詢
            response_data = ollama_client.generate_response(config.model, prompt)
            response_time = time.time() - start_time

            # 檢查查詢是否成功
            if response_data.get('success', False):
                response_text = response_data.get('response', '')
                # 估算token數量（簡化版本，實際應該使用tokenizer）
                tokens_count = len(response_text.split()) if response_text else 0

                return QueryResult(
                    user_id=user_id,
                    prompt=prompt,
                    response_text=response_text,
                    tokens_count=tokens_count,
                    response_time=response_time,
                    timestamp=timestamp,
                    success=True
                )
            else:
                # 查詢失敗
                error_message = response_data.get('error', 'Unknown error')
                return QueryResult(
                    user_id=user_id,
                    prompt=prompt,
                    response_text="",
                    tokens_count=0,
                    response_time=response_time,
                    timestamp=timestamp,
                    success=False,
                    error_message=error_message
                )
            
        except Exception as e:
            response_time = time.time() - start_time
            return QueryResult(
                user_id=user_id,
                prompt=prompt,
                response_text="",
                tokens_count=0,
                response_time=response_time,
                timestamp=timestamp,
                success=False,
                error_message=str(e)
            )
    
    def _calculate_final_statistics(self, result: MultiUserTestResult):
        """計算最終統計數據"""
        if not result.query_results:
            return
        
        # 基本統計
        result.total_queries = len(result.query_results)
        result.successful_queries = sum(1 for r in result.query_results if r.success)
        result.failed_queries = result.total_queries - result.successful_queries
        result.total_tokens = sum(r.tokens_count for r in result.query_results if r.success)
        
        # 響應時間統計
        response_times = [r.response_time for r in result.query_results if r.success]
        if response_times:
            result.average_response_time = statistics.mean(response_times)
            result.min_response_time = min(response_times)
            result.max_response_time = max(response_times)
        
        # TPM統計
        if result.config.enable_tpm_monitoring:
            result.tpm_samples = calculate_tpm(result.query_results)
            if result.tpm_samples:
                tpm_values = [sample['tokens_per_minute'] for sample in result.tpm_samples]
                result.average_tpm = statistics.mean(tpm_values) if tpm_values else 0.0
                result.peak_tpm = max(tpm_values) if tpm_values else 0.0
        
        # 設置結束時間
        result.end_time = datetime.now()
    
    def stop_test(self, test_id: str) -> bool:
        """停止測試"""
        with self.lock:
            if test_id in self.active_tests:
                self.active_tests[test_id]['stop_requested'] = True
                return True
            return False
    
    def get_test_status(self, test_id: str) -> Optional[Dict]:
        """獲取測試狀態"""
        with self.lock:
            if test_id not in self.active_tests:
                # 檢查是否在已完成的測試中
                if test_id in self.test_results:
                    result = self.test_results[test_id]
                    return {
                        'test_id': test_id,
                        'status': 'completed',
                        'progress': 100,
                        'current_tpm': result.average_tpm,
                        'active_users': 0,
                        'statistics': {
                            'total_queries': result.total_queries,
                            'successful_queries': result.successful_queries,
                            'failed_queries': result.failed_queries,
                            'total_tokens': result.total_tokens,
                            'average_tpm': result.average_tpm,
                            'peak_tpm': result.peak_tpm,
                            'average_response_time': result.average_response_time
                        }
                    }
                return None

            test_info = self.active_tests[test_id]
            status = {
                'test_id': test_id,
                'status': test_info['status'],
                'progress': test_info['progress'],
                'current_tpm': test_info.get('current_tpm', 0.0),
                'active_users': test_info.get('active_users', 0)
            }

            if 'error' in test_info:
                status['error'] = test_info['error']

            if 'result' in test_info:
                result = test_info['result']
                # 實時計算當前統計
                self._update_real_time_statistics(result)

                status['statistics'] = {
                    'total_queries': result.total_queries,
                    'successful_queries': result.successful_queries,
                    'failed_queries': result.failed_queries,
                    'total_tokens': result.total_tokens,
                    'average_tpm': result.average_tpm,
                    'peak_tpm': result.peak_tpm,
                    'average_response_time': result.average_response_time
                }

            return status

    def _update_real_time_statistics(self, result: MultiUserTestResult):
        """更新實時統計數據"""
        if not result.query_results:
            return

        # 更新基本統計
        result.total_queries = len(result.query_results)
        result.successful_queries = sum(1 for r in result.query_results if r.success)
        result.failed_queries = result.total_queries - result.successful_queries
        result.total_tokens = sum(r.tokens_count for r in result.query_results if r.success)

        # 更新響應時間統計
        successful_results = [r for r in result.query_results if r.success]
        if successful_results:
            response_times = [r.response_time for r in successful_results]
            result.average_response_time = sum(response_times) / len(response_times)
            result.min_response_time = min(response_times)
            result.max_response_time = max(response_times)

        # 更新TPM統計
        if result.config.enable_tpm_monitoring and len(result.query_results) > 0:
            result.tpm_samples = calculate_tpm(result.query_results)
            if result.tpm_samples:
                tpm_values = [sample['tokens_per_minute'] for sample in result.tpm_samples]
                result.average_tpm = sum(tpm_values) / len(tpm_values) if tpm_values else 0.0
                result.peak_tpm = max(tpm_values) if tpm_values else 0.0

    def _save_multi_user_test_to_database(self, test_id: str, config: MultiUserTestConfig, result: MultiUserTestResult):
        """保存多用戶測試結果到資料庫"""
        try:
            # 獲取當前硬體資訊
            hardware_info = get_hardware_info()

            # 準備統計資料
            statistics = {
                'total_queries': result.total_queries,
                'successful_queries': result.successful_queries,
                'failed_queries': result.failed_queries,
                'total_tokens': result.total_tokens,
                'average_response_time': result.average_response_time,
                'min_response_time': result.min_response_time,
                'max_response_time': result.max_response_time,
                'average_tpm': result.average_tpm,
                'peak_tpm': result.peak_tpm,
                'user_count': config.user_count,
                'queries_per_user': config.queries_per_user
            }

            # 準備測試結果資料（用於重繪圖表）
            test_results_data = {
                'query_results': [
                    {
                        'user_id': r.user_id,
                        'query_index': r.query_index,
                        'prompt': r.prompt,
                        'response': r.response,
                        'success': r.success,
                        'response_time': r.response_time,
                        'tokens_count': r.tokens_count,
                        'timestamp': r.timestamp.isoformat() if r.timestamp else None,
                        'error_message': r.error_message
                    } for r in result.query_results
                ],
                'tpm_samples': [
                    {
                        'timestamp': sample['timestamp'].isoformat(),
                        'tokens_per_minute': sample['tokens_per_minute']
                    } for sample in (result.tpm_samples or [])
                ],
                'user_sessions': {
                    str(user_id): {
                        'user_id': session.user_id,
                        'assigned_prompts': session.assigned_prompts,
                        'completed_queries': session.completed_queries,
                        'failed_queries': session.failed_queries
                    } for user_id, session in result.user_sessions.items()
                }
            }

            # 準備保存的資料
            db_data = {
                'test_id': test_id,
                'test_name': f"多用戶並發測試_{result.start_time.strftime('%Y%m%d_%H%M%S')}",
                'test_type': 2,  # 多用戶並發測試
                'test_time': result.start_time,
                'model_name': config.model_name,
                'hardware_info': hardware_info,
                'test_config': {
                    'model_name': config.model_name,
                    'user_count': config.user_count,
                    'queries_per_user': config.queries_per_user,
                    'concurrent_limit': config.concurrent_limit,
                    'delay_between_queries': config.delay_between_queries,
                    'use_random_prompts': config.use_random_prompts,
                    'custom_prompts': config.custom_prompts,
                    'enable_tpm_monitoring': config.enable_tpm_monitoring,
                    'enable_detailed_logging': config.enable_detailed_logging
                },
                'test_results': test_results_data,
                'test_statistics': statistics,
                'duration_seconds': (result.end_time - result.start_time).total_seconds() if result.end_time else 0,
                'total_requests': result.total_queries,
                'successful_requests': result.successful_queries,
                'failed_requests': result.failed_queries,
                'avg_response_time': result.average_response_time
            }

            # 保存到資料庫
            success = db.save_test_result(db_data)
            if success:
                print(f"Multi-user test result saved to database: {test_id}")
            else:
                print(f"Failed to save multi-user test result to database: {test_id}")

        except Exception as e:
            print(f"Error saving multi-user test result to database: {e}")
