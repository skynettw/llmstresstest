"""
測試二 - 多用戶並發測試配置和數據結構
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime
import random

@dataclass
class MultiUserTestConfig:
    """多用戶並發測試配置"""
    model: str                          # 測試的模型名稱
    user_count: int                     # 模擬用戶數量 (1-10)
    queries_per_user: int               # 每個用戶的查詢次數
    test_duration_minutes: Optional[int] = None  # 測試持續時間（分鐘），如果設定則忽略queries_per_user
    
    # 提示詞相關
    use_random_prompts: bool = True     # 是否使用隨機提示詞
    custom_prompts: List[str] = None    # 自定義提示詞列表
    
    # 測試控制
    concurrent_limit: int = 10          # 最大並發限制
    delay_between_queries: float = 0.5  # 查詢間隔（秒）
    
    # 監控選項
    enable_tpm_monitoring: bool = True  # 啟用TPM監控
    enable_detailed_logging: bool = False  # 詳細日誌
    
    def __post_init__(self):
        """驗證配置參數"""
        if self.user_count < 1 or self.user_count > 10:
            raise ValueError("用戶數量必須在1-10之間")
        
        if self.queries_per_user < 1:
            raise ValueError("每用戶查詢次數必須大於0")
        
        if self.custom_prompts and len(self.custom_prompts) == 0:
            raise ValueError("自定義提示詞列表不能為空")

@dataclass
class UserSession:
    """用戶會話信息"""
    user_id: int
    assigned_prompts: List[str]
    completed_queries: int = 0
    failed_queries: int = 0
    total_tokens: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    response_times: List[float] = None
    
    def __post_init__(self):
        if self.response_times is None:
            self.response_times = []

@dataclass
class QueryResult:
    """單次查詢結果"""
    user_id: int
    prompt: str
    response_text: str
    tokens_count: int
    response_time: float
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None

@dataclass
class MultiUserTestResult:
    """多用戶測試結果"""
    test_id: str
    config: MultiUserTestConfig
    start_time: datetime
    end_time: Optional[datetime] = None
    
    # 用戶會話
    user_sessions: Dict[int, UserSession] = None
    
    # 查詢結果
    query_results: List[QueryResult] = None
    
    # 統計數據
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    total_tokens: int = 0
    
    # TPM統計
    tpm_samples: List[Dict] = None  # 每分鐘的token統計樣本
    average_tpm: float = 0.0
    peak_tpm: float = 0.0
    
    # 性能統計
    average_response_time: float = 0.0
    min_response_time: float = 0.0
    max_response_time: float = 0.0
    
    def __post_init__(self):
        if self.user_sessions is None:
            self.user_sessions = {}
        if self.query_results is None:
            self.query_results = []
        if self.tpm_samples is None:
            self.tpm_samples = []

# 50組常用提示詞庫
COMMON_PROMPTS = [
    # 基礎問答類 (1-10)
    "請用繁體中文回答：什麼是人工智慧？",
    "請解釋機器學習的基本概念。",
    "請描述深度學習的應用領域。",
    "什麼是自然語言處理？請舉例說明。",
    "請說明大語言模型的工作原理。",
    "什麼是神經網絡？它如何運作？",
    "請解釋監督學習和無監督學習的差異。",
    "什麼是強化學習？請提供實際應用例子。",
    "請描述計算機視覺的主要技術。",
    "什麼是數據科學？它包含哪些領域？",
    
    # 技術解釋類 (11-20)
    "請解釋什麼是雲端運算及其優勢。",
    "什麼是區塊鏈技術？它如何確保安全性？",
    "請說明物聯網(IoT)的概念和應用。",
    "什麼是5G技術？它與4G有什麼不同？",
    "請解釋虛擬實境(VR)和擴增實境(AR)的差異。",
    "什麼是量子計算？它的潛在應用有哪些？",
    "請描述邊緣運算的概念和優勢。",
    "什麼是微服務架構？它有什麼好處？",
    "請解釋DevOps的理念和實踐方法。",
    "什麼是容器化技術？Docker是如何運作的？",
    
    # 生活應用類 (21-30)
    "請推薦一些提高工作效率的方法。",
    "如何培養良好的時間管理習慣？",
    "請分享一些健康飲食的建議。",
    "如何保持身心健康的平衡？",
    "請推薦一些適合初學者的運動項目。",
    "如何改善睡眠品質？",
    "請分享一些有效的學習方法。",
    "如何建立良好的人際關係？",
    "請推薦一些紓解壓力的方式。",
    "如何培養創造力和創新思維？",
    
    # 知識問答類 (31-40)
    "請介紹太陽系的八大行星。",
    "什麼是溫室效應？它對地球有什麼影響？",
    "請解釋光合作用的過程。",
    "什麼是DNA？它在生物體中的作用是什麼？",
    "請描述水循環的過程。",
    "什麼是進化論？達爾文的貢獻是什麼？",
    "請解釋重力的概念和牛頓的貢獻。",
    "什麼是原子結構？電子、質子、中子的作用？",
    "請介紹元素週期表的組織原理。",
    "什麼是能量守恆定律？請舉例說明。",
    
    # 創意思考類 (41-50)
    "如果你能發明一項新技術，你會發明什麼？為什麼？",
    "請想像一下2050年的世界會是什麼樣子。",
    "如果你是一位城市規劃師，你會如何設計理想城市？",
    "請創作一個關於友誼的短故事。",
    "如果你能與歷史上任何一位人物對話，你會選擇誰？為什麼？",
    "請設計一個解決環境污染的創新方案。",
    "如果你能改變世界上的一件事，你會改變什麼？",
    "請想像一種全新的交通工具，並描述它的特點。",
    "如果你是一位教育家，你會如何改革現有的教育制度？",
    "請描述你心目中完美的一天是什麼樣子。"
]

def get_random_prompts(count: int) -> List[str]:
    """獲取指定數量的隨機提示詞"""
    if count > len(COMMON_PROMPTS):
        # 如果需要的數量超過可用提示詞，則重複使用
        return random.choices(COMMON_PROMPTS, k=count)
    return random.sample(COMMON_PROMPTS, count)

def assign_prompts_to_users(user_count: int, queries_per_user: int) -> Dict[int, List[str]]:
    """為每個用戶分配提示詞"""
    user_prompts = {}
    
    for user_id in range(1, user_count + 1):
        # 每個用戶獲得不同的隨機提示詞
        user_prompts[user_id] = get_random_prompts(queries_per_user)
    
    return user_prompts

def calculate_tpm(query_results: List[QueryResult], time_window_minutes: int = 1) -> List[Dict]:
    """計算每分鐘Token數量(TPM)"""
    if not query_results:
        return []
    
    # 按時間排序
    sorted_results = sorted(query_results, key=lambda x: x.timestamp)
    
    start_time = sorted_results[0].timestamp
    end_time = sorted_results[-1].timestamp
    
    tpm_samples = []
    current_time = start_time
    
    while current_time <= end_time:
        window_end = current_time.replace(second=0, microsecond=0)
        window_start = window_end.replace(minute=window_end.minute - time_window_minutes if window_end.minute >= time_window_minutes else 0)
        
        # 計算時間窗口內的token總數
        tokens_in_window = sum(
            result.tokens_count for result in sorted_results
            if window_start <= result.timestamp < window_end and result.success
        )
        
        tpm_samples.append({
            'timestamp': window_end,
            'tokens_per_minute': tokens_in_window,
            'queries_count': len([r for r in sorted_results if window_start <= r.timestamp < window_end])
        })
        
        # 移動到下一分鐘
        current_time = window_end.replace(minute=window_end.minute + 1)
    
    return tpm_samples
