# Ollama 壓力測試工具 - 技術文檔

## 概述

本工具是一個專為 Ollama 大語言模型設計的壓力測試系統，用於評估不同模型在高並發場景下的性能表現。通過模擬多個並發請求，測試模型的回應時間、吞吐量和穩定性。

## 系統架構

### 核心組件

1. **Flask Web 應用程序** (`app.py`)
   - 提供 Web 界面和 RESTful API
   - 處理測試配置和狀態管理
   - 實時返回測試進度和結果

2. **壓力測試管理器** (`stress_test_simple.py`)
   - 核心測試邏輯實現
   - 多線程並發請求處理
   - 測試狀態追蹤和結果統計

3. **Ollama 客戶端** (`ollama_client.py`)
   - 與 Ollama 服務器通信
   - 處理模型請求和回應
   - 錯誤處理和超時管理

4. **硬體監控模組** (`hardware_info.py`)
   - 實時監控系統資源使用情況
   - CPU、記憶體、GPU 使用率追蹤
   - 為性能分析提供基礎數據

## 壓力測試原理

### 1. 並發模型

#### 線程池執行器 (ThreadPoolExecutor)
```python
with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
    futures = [executor.submit(worker) for _ in range(concurrent_requests)]
```

- **並發控制**：使用 Python 的 `concurrent.futures.ThreadPoolExecutor` 管理工作線程
- **線程數量**：等於用戶設定的並發請求數
- **任務分配**：每個線程從任務隊列中獲取請求任務

#### 任務隊列機制
```python
task_queue = queue.Queue()
for i in range(total_requests):
    task_queue.put(i)
```

- **FIFO 隊列**：使用 `queue.Queue` 實現先進先出的任務分配
- **線程安全**：確保多線程環境下的任務分配不會衝突
- **動態負載**：工作線程動態從隊列獲取任務，實現負載均衡

### 2. 測試執行流程

#### 階段一：初始化
1. **配置驗證**：檢查模型名稱、並發數、總請求數等參數
2. **服務器檢查**：驗證 Ollama 服務器可用性
3. **資源準備**：創建任務隊列和結果收集器

#### 階段二：並發執行
```python
def worker():
    while True:
        # 檢查停止信號
        if self.active_tests[test_id]['stop_requested']:
            break
        
        # 獲取任務
        task_id = task_queue.get_nowait()
        
        # 執行請求
        start_time = time.time()
        result = ollama_client.generate_response(model, prompt)
        end_time = time.time()
        
        # 記錄結果
        result['response_time'] = end_time - start_time
```

#### 階段三：結果統計
- **即時更新**：每完成一個請求立即更新進度
- **統計計算**：計算平均回應時間、成功率等指標
- **狀態同步**：線程安全地更新測試狀態

### 3. 性能指標

#### 回應時間統計
- **最小值 (Min)**：所有成功請求中的最短回應時間
- **最大值 (Max)**：所有成功請求中的最長回應時間
- **平均值 (Mean)**：所有成功請求回應時間的算術平均
- **中位數 (Median)**：排序後位於中間位置的回應時間
- **標準差 (Std Dev)**：衡量回應時間的離散程度

#### 吞吐量指標
```python
requests_per_second = successful_requests / total_response_time
```
- **每秒請求數 (RPS)**：系統每秒能處理的請求數量
- **成功率**：成功請求數與總請求數的比例

### 4. 並發控制策略

#### 線程同步
```python
with self.lock:
    self.active_tests[test_id]['progress'] = progress
    self.active_tests[test_id]['completed_requests'] = completed_count
```

- **互斥鎖 (Mutex)**：使用 `threading.Lock()` 保護共享資源
- **原子操作**：確保狀態更新的原子性
- **競態條件防護**：避免多線程同時修改共享數據

#### 優雅停止機制
```python
# 檢查停止信號
with self.lock:
    if self.active_tests[test_id]['stop_requested']:
        break
```

- **信號檢查**：工作線程定期檢查停止信號
- **資源清理**：確保測試停止時正確清理資源
- **狀態一致性**：維護測試狀態的一致性

## 技術實現細節

### 1. 異步處理架構

#### 前端輪詢機制
```javascript
progressInterval = setInterval(() => {
    if (currentTestId) {
        checkTestProgress();
    }
}, 1000); // 每秒檢查一次
```

- **定時輪詢**：前端每秒向後端查詢測試進度
- **非阻塞更新**：不影響用戶界面響應性
- **實時反饋**：提供即時的測試進度信息

#### 後端狀態管理
```python
self.active_tests[test_id] = {
    'config': config,
    'status': 'starting',
    'progress': 0,
    'completed_requests': 0,
    'failed_requests': 0,
    'results': []
}
```

### 2. 錯誤處理策略

#### 請求級錯誤處理
- **超時處理**：設置合理的請求超時時間
- **重試機制**：對於網路錯誤可選擇重試
- **錯誤分類**：區分不同類型的錯誤原因

#### 系統級錯誤處理
- **異常捕獲**：捕獲並記錄所有異常
- **優雅降級**：在部分功能失效時保持系統可用
- **資源保護**：防止資源洩漏和系統崩潰

### 3. 性能優化

#### 連接池管理
```python
self.session = requests.Session()
self.session.timeout = 30
```

- **會話復用**：使用 `requests.Session` 復用 HTTP 連接
- **連接池**：減少連接建立和關閉的開銷
- **超時控制**：避免長時間等待無響應的請求

#### 記憶體管理
- **結果緩存**：合理控制結果數據的記憶體使用
- **垃圾回收**：及時清理完成的測試數據
- **資源限制**：設置合理的並發數上限

## 使用場景

### 1. 模型性能評估
- **基準測試**：建立模型性能基準線
- **版本比較**：比較不同版本模型的性能差異
- **配置優化**：找到最佳的並發配置參數

### 2. 系統容量規劃
- **負載預測**：預測系統在實際負載下的表現
- **瓶頸識別**：識別系統性能瓶頸
- **擴容決策**：為系統擴容提供數據支持

### 3. 穩定性測試
- **長時間運行**：測試系統長時間運行的穩定性
- **異常恢復**：測試系統在異常情況下的恢復能力
- **資源洩漏檢測**：檢測潛在的資源洩漏問題

## 最佳實踐

### 1. 測試參數設置
- **並發數**：建議從小到大逐步增加，找到最佳值
- **總請求數**：確保有足夠的樣本數據進行統計分析
- **測試時長**：平衡測試準確性和執行時間

### 2. 結果分析
- **多次測試**：進行多次測試取平均值，提高結果可靠性
- **環境控制**：保持測試環境的一致性
- **指標關注**：重點關注平均回應時間和 95% 分位數

### 3. 系統監控
- **資源監控**：同時監控 CPU、記憶體、GPU 使用情況
- **網路監控**：關注網路延遲和帶寬使用
- **日誌分析**：分析錯誤日誌找出問題根因

## 圖表可視化功能

### 1. Plotly 圖表集成

本系統集成了 Plotly.js 來提供豐富的互動式圖表，幫助用戶更直觀地分析測試結果。

#### 圖表類型

**1. 回應時間分布直方圖**
```python
fig_histogram = go.Figure(data=[
    go.Histogram(
        x=response_times,
        nbinsx=20,
        name='回應時間分布',
        marker_color='rgba(55, 128, 191, 0.7)'
    )
])
```
- **用途**：顯示回應時間的分布情況
- **分析價值**：識別性能模式和異常值
- **互動功能**：縮放、平移、數據點詳情

**2. 回應時間趨勢圖**
```python
fig_timeline = go.Figure()
fig_timeline.add_trace(go.Scatter(
    x=task_ids,
    y=response_times,
    mode='lines+markers',
    name='回應時間'
))
```
- **用途**：顯示回應時間隨請求序號的變化
- **分析價值**：識別性能趨勢和系統穩定性
- **特色功能**：包含平均線參考

**3. 請求成功率餅圖**
```python
fig_pie = go.Figure(data=[
    go.Pie(
        labels=['成功', '失敗'],
        values=[success_count, failed_count],
        hole=0.3,
        marker_colors=['#28a745', '#dc3545']
    )
])
```
- **用途**：直觀顯示成功和失敗請求的比例
- **分析價值**：快速評估系統可靠性
- **視覺特色**：使用語義化顏色（綠色/紅色）

**4. 回應時間統計箱線圖**
```python
fig_box = go.Figure()
fig_box.add_trace(go.Box(
    y=response_times,
    name='回應時間',
    boxpoints='outliers'
))
```
- **用途**：顯示回應時間的統計分布
- **分析價值**：識別中位數、四分位數和異常值
- **統計信息**：包含最小值、最大值、中位數等

### 2. 圖表數據流程

#### 後端數據處理
```python
def generate_test_charts(results, statistics):
    """生成測試結果圖表"""
    charts = {}

    # 分離成功和失敗的結果
    successful_results = [r for r in results if r.get('success', False)]
    failed_results = [r for r in results if not r.get('success', False)]

    # 生成各種圖表...
    return charts
```

#### 前端圖表渲染
```javascript
function displayCharts(chartsData) {
    // 解析 JSON 數據並使用 Plotly 渲染
    const histogramData = JSON.parse(chartsData.response_time_histogram);
    Plotly.newPlot('response-time-histogram', histogramData.data, histogramData.layout, {
        responsive: true,
        displayModeBar: true
    });
}
```

### 3. 用戶體驗優化

#### 響應式設計
- **自適應佈局**：圖表自動適應不同螢幕尺寸
- **互動控制**：提供縮放、平移、重置等功能
- **載入指示器**：顯示圖表載入進度

#### 錯誤處理
- **優雅降級**：圖表載入失敗時顯示友好錯誤訊息
- **數據驗證**：確保圖表數據的完整性
- **異常恢復**：提供重新載入圖表的選項

## 擴展功能

### 1. 高級統計
- **分位數統計**：P50、P95、P99 回應時間
- **時間序列分析**：回應時間隨時間的變化趨勢
- **熱力圖**：可視化性能分布

### 2. 測試場景
- **漸增負載**：逐步增加並發數的測試
- **突發負載**：模擬突然增加的負載情況
- **混合負載**：不同類型請求的混合測試

### 3. 報告生成
- **PDF 報告**：生成詳細的測試報告
- **圖表導出**：支持 PNG、SVG、PDF 格式導出
- **歷史比較**：與歷史測試結果的比較分析

### 4. 進階圖表功能
- **實時更新圖表**：測試進行中的動態圖表更新
- **多測試比較**：同時顯示多個測試結果的對比圖表
- **自定義圖表**：用戶可選擇顯示的圖表類型和參數
