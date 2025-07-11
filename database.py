import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestHistoryDatabase:
    """測試歷史記錄資料庫管理類"""
    
    def __init__(self, db_path: str = "db.sqlite3"):
        """
        初始化資料庫連接
        
        Args:
            db_path: 資料庫檔案路徑
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """初始化資料庫，創建必要的表格"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 創建測試歷史記錄表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS test_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        test_id TEXT UNIQUE NOT NULL,
                        test_name TEXT NOT NULL,
                        test_type INTEGER NOT NULL,  -- 1: 基礎壓力測試, 2: 多用戶並發測試
                        test_time TIMESTAMP NOT NULL,
                        model_name TEXT NOT NULL,
                        hardware_info TEXT NOT NULL,  -- JSON格式的硬體資訊
                        test_config TEXT NOT NULL,   -- JSON格式的測試配置
                        test_results TEXT NOT NULL,  -- JSON格式的測試結果
                        test_statistics TEXT,        -- JSON格式的統計資料
                        duration_seconds REAL,       -- 測試持續時間（秒）
                        total_requests INTEGER,      -- 總請求數
                        successful_requests INTEGER, -- 成功請求數
                        failed_requests INTEGER,     -- 失敗請求數
                        avg_response_time REAL,      -- 平均回應時間
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 創建索引以提高查詢效能
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_time ON test_history(test_time)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_type ON test_history(test_type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_model_name ON test_history(model_name)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_id ON test_history(test_id)')
                
                conn.commit()
                logger.info(f"Database initialized successfully at {self.db_path}")
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    def save_test_result(self, test_data: Dict[str, Any]) -> bool:
        """
        保存測試結果到資料庫
        
        Args:
            test_data: 包含測試資料的字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 準備資料
                test_id = test_data.get('test_id')
                test_name = test_data.get('test_name', f"Test_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                test_type = test_data.get('test_type', 1)
                test_time = test_data.get('test_time', datetime.now())
                model_name = test_data.get('model_name', '')
                hardware_info = json.dumps(test_data.get('hardware_info', {}), ensure_ascii=False)
                test_config = json.dumps(test_data.get('test_config', {}), ensure_ascii=False)
                test_results = json.dumps(test_data.get('test_results', {}), ensure_ascii=False)
                test_statistics = json.dumps(test_data.get('test_statistics', {}), ensure_ascii=False)
                
                # 統計資料
                duration_seconds = test_data.get('duration_seconds', 0)
                total_requests = test_data.get('total_requests', 0)
                successful_requests = test_data.get('successful_requests', 0)
                failed_requests = test_data.get('failed_requests', 0)
                avg_response_time = test_data.get('avg_response_time', 0)
                
                # 插入資料
                cursor.execute('''
                    INSERT OR REPLACE INTO test_history 
                    (test_id, test_name, test_type, test_time, model_name, hardware_info, 
                     test_config, test_results, test_statistics, duration_seconds, 
                     total_requests, successful_requests, failed_requests, avg_response_time,
                     updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (
                    test_id, test_name, test_type, test_time, model_name, hardware_info,
                    test_config, test_results, test_statistics, duration_seconds,
                    total_requests, successful_requests, failed_requests, avg_response_time
                ))
                
                conn.commit()
                logger.info(f"Test result saved successfully: {test_id}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save test result: {e}")
            return False
    
    def get_test_history(self, limit: int = 100, offset: int = 0, 
                        test_type: Optional[int] = None,
                        model_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        獲取測試歷史記錄
        
        Args:
            limit: 限制返回記錄數
            offset: 偏移量
            test_type: 測試類型篩選 (1 或 2)
            model_name: 模型名稱篩選
            
        Returns:
            List[Dict]: 測試歷史記錄列表
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # 使結果可以像字典一樣訪問
                cursor = conn.cursor()
                
                # 構建查詢條件
                where_conditions = []
                params = []
                
                if test_type is not None:
                    where_conditions.append("test_type = ?")
                    params.append(test_type)
                
                if model_name:
                    where_conditions.append("model_name LIKE ?")
                    params.append(f"%{model_name}%")
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                # 執行查詢
                query = f'''
                    SELECT id, test_id, test_name, test_type, test_time, model_name,
                           duration_seconds, total_requests, successful_requests, 
                           failed_requests, avg_response_time, created_at
                    FROM test_history 
                    {where_clause}
                    ORDER BY test_time DESC 
                    LIMIT ? OFFSET ?
                '''
                
                params.extend([limit, offset])
                cursor.execute(query, params)
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to get test history: {e}")
            return []
    
    def get_test_detail(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        獲取特定測試的詳細資料
        
        Args:
            test_id: 測試ID
            
        Returns:
            Dict: 測試詳細資料，如果不存在則返回None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM test_history WHERE test_id = ?
                ''', (test_id,))
                
                row = cursor.fetchone()
                if row:
                    result = dict(row)
                    # 解析JSON欄位
                    result['hardware_info'] = json.loads(result['hardware_info'])
                    result['test_config'] = json.loads(result['test_config'])
                    result['test_results'] = json.loads(result['test_results'])
                    result['test_statistics'] = json.loads(result['test_statistics']) if result['test_statistics'] else {}
                    return result
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get test detail: {e}")
            return None
    
    def delete_test_record(self, test_id: str) -> bool:
        """
        刪除測試記錄
        
        Args:
            test_id: 測試ID
            
        Returns:
            bool: 刪除是否成功
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM test_history WHERE test_id = ?', (test_id,))
                
                if cursor.rowcount > 0:
                    conn.commit()
                    logger.info(f"Test record deleted successfully: {test_id}")
                    return True
                else:
                    logger.warning(f"Test record not found: {test_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to delete test record: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        獲取資料庫統計資訊
        
        Returns:
            Dict: 統計資訊
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 總記錄數
                cursor.execute('SELECT COUNT(*) FROM test_history')
                total_records = cursor.fetchone()[0]
                
                # 按測試類型統計
                cursor.execute('''
                    SELECT test_type, COUNT(*) 
                    FROM test_history 
                    GROUP BY test_type
                ''')
                type_stats = dict(cursor.fetchall())
                
                # 按模型統計
                cursor.execute('''
                    SELECT model_name, COUNT(*) 
                    FROM test_history 
                    GROUP BY model_name 
                    ORDER BY COUNT(*) DESC 
                    LIMIT 10
                ''')
                model_stats = dict(cursor.fetchall())
                
                # 最近的測試時間
                cursor.execute('SELECT MAX(test_time) FROM test_history')
                latest_test = cursor.fetchone()[0]
                
                return {
                    'total_records': total_records,
                    'type_statistics': type_stats,
                    'model_statistics': model_stats,
                    'latest_test_time': latest_test
                }
                
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}

# 創建全局資料庫實例
db = TestHistoryDatabase()
