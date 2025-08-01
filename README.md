# Ollama 壓力測試工具

這是一個基於Flask + Bootstrap 5的Ollama模型壓力測試網頁應用，提供兩種不同的測試模式來全面評估Ollama模型在您系統上的性能表現。系統具備完整的硬體監控、歷史記錄管理和互動式圖表分析功能。

## 🎯 測試模式概覽

### 測試一：基礎壓力測試 - 系統負載與穩定性評估
**目標**：評估模型在高並發負載下的穩定性和回應時間分布
**原理**：使用相同提示詞進行大量並發請求，模擬系統峰值負載情況
**適用場景**：系統容量規劃、性能基準測試、穩定性驗證

### 測試二：多用戶並發測試 - 真實使用場景模擬
**目標**：評估模型在多用戶真實使用場景下的吞吐量和服務品質
**原理**：模擬多個用戶使用不同提示詞同時查詢，計算TPM(每分鐘Token數)性能指標
**適用場景**：生產環境評估、用戶體驗預測、資源配置優化

## 🔧 核心功能特色

### 系統監控與管理
- **即時硬體監控**: CPU、記憶體、GPU使用率的進度條顯示
- **模型管理**: 自動檢測並列出本機可用的Ollama模型
- **歷史記錄管理**: SQLite資料庫存儲所有測試記錄，支援篩選和圖表重繪
- **響應式設計**: Bootstrap 5框架，支援各種設備和螢幕尺寸

### 測試執行與控制
- **智能狀態管理**: 測試期間自動禁用控制項，防止衝突操作
- **即時進度追蹤**: AJAX輪詢技術提供毫秒級進度更新
- **安全停止機制**: 支援測試中途安全停止，保留部分結果
- **錯誤處理**: 完整的異常處理和錯誤報告機制

### 數據分析與視覺化
- **互動式圖表**: 使用Plotly.js生成可縮放、可互動的測試結果圖表
- **多維度統計**: 回應時間、成功率、TPM、用戶分布等多項指標
- **歷史對比**: 支援選擇歷史記錄重新繪製圖表進行對比分析
- **數據導出**: 完整的測試配置和結果數據保存

## 系統需求

- Python 3.8+
- Ollama 服務器正在運行
- 支援的作業系統: Windows, Linux, macOS

## 安裝步驟

1. **克隆或下載專案**
   ```bash
   git clone <repository-url>
   cd llmstresstest
   ```

2. **安裝依賴**
   ```bash
   pip install -r requirements.txt
   ```

3. **確保Ollama服務器運行**
   ```bash
   ollama serve
   ```

4. **啟動應用**
   ```bash
   python app_simple.py
   ```

5. **開啟瀏覽器**
   訪問 `http://localhost:5001`

## 使用方法

### 1. 查看硬體資訊
- 頁面載入時會直接顯示系統硬體資訊
- 包括CPU、記憶體、GPU、系統、網路資訊等
- 可點擊「重新整理」按鈕動態更新資訊

### 2. 選擇測試類型
系統提供兩種測試模式，每種都有其特定的測試目標和應用場景：

## 📊 測試一：基礎壓力測試

### 測試原理與邏輯
**核心概念**：通過大量並發的相同請求來測試系統的極限負載能力
**執行邏輯**：
1. **任務分配**：將總請求數平均分配給指定數量的並發線程
2. **並發執行**：使用ThreadPoolExecutor管理並發請求，確保線程安全
3. **實時監控**：每完成一個請求立即更新進度和統計資料
4. **結果收集**：記錄每個請求的回應時間、成功狀態、錯誤信息

### 測試目標與應用
- **性能基準測試**：建立模型在特定硬體上的性能基線
- **系統容量規劃**：確定系統能承受的最大並發負載
- **穩定性驗證**：檢測模型在高負載下是否會出現錯誤或崩潰
- **回應時間分析**：分析回應時間的分布特徵和異常值

### 配置參數說明
- **模型選擇**：測試目標模型（影響計算複雜度和資源消耗）
- **並發請求數**：同時執行的線程數量（1-20，建議從CPU核心數開始）
- **總請求數**：測試的總樣本數量（1-1000，影響統計準確性）
- **測試提示詞**：統一的測試內容（建議使用中等長度的提示詞）

### 統計指標與圖表
- **回應時間分布直方圖**：顯示回應時間的統計分布
- **成功率餅圖**：視覺化成功與失敗請求的比例
- **回應時間趨勢線**：按時間順序顯示回應時間變化
- **統計摘要**：平均值、中位數、最大值、最小值、標準差

## 🎯 測試二：多用戶並發測試

### 測試原理與邏輯
**核心概念**：模擬真實的多用戶使用場景，評估系統的實際服務能力
**執行邏輯**：
1. **用戶會話創建**：為每個模擬用戶創建獨立的會話和提示詞列表
2. **提示詞分配**：從50組內建提示詞中隨機分配，確保用戶間的多樣性
3. **並發控制**：使用信號量限制最大並發數，模擬真實的資源限制
4. **TPM計算**：實時計算每分鐘Token產出量，評估吞吐量性能
5. **用戶統計**：追蹤每個用戶的查詢成功率和回應時間

### 測試目標與應用
- **生產環境評估**：預測模型在實際多用戶環境下的表現
- **用戶體驗預測**：評估不同用戶數量下的服務品質
- **資源配置優化**：確定最佳的用戶數與資源配置比例
- **TPM性能測試**：測量模型的實際Token產出能力

### 配置參數說明
- **模擬用戶數量**：1-10個虛擬用戶（建議從2-3個開始測試）
- **每用戶查詢次數**：每個用戶執行的查詢數量（影響測試持續時間）
- **最大並發限制**：系統允許的最大同時查詢數（防止資源耗盡）
- **查詢間隔**：用戶查詢間的等待時間（模擬真實使用節奏）
- **提示詞策略**：
  - **隨機提示詞**：從50組預設提示詞中隨機選擇（推薦）
  - **自定義提示詞**：使用用戶提供的特定提示詞列表

### 內建提示詞庫設計
系統內建50組精心設計的提示詞，涵蓋5個主要類別：
- **基礎問答類**（10組）：AI、機器學習等技術概念
- **技術解釋類**（10組）：雲端運算、區塊鏈等新興技術
- **生活應用類**（10組）：健康、學習、時間管理等實用建議
- **知識問答類**（10組）：科學、自然等知識性問題
- **創意思考類**（10組）：開放性問題，測試模型創造力

### 統計指標與圖表
- **TPM趨勢圖**：顯示每分鐘Token產出量的時間變化
- **用戶查詢分布圖**：各用戶的查詢數量和Token數量對比
- **用戶成功率圖**：各用戶的查詢成功率比較
- **綜合統計**：總查詢數、成功率、平均TPM、峰值TPM等

#### 執行測試
- 點擊「開始多用戶測試」按鈕啟動測試
- 系統會為每個用戶分配不同的隨機提示詞
- 實時顯示測試進度、當前TPM、活躍用戶數
- 可隨時停止測試
- 測試完成後顯示詳細的TPM統計和性能分析

### 5. 查看結果
- 測試完成後會顯示詳細的統計結果和視覺化圖表
- **測試一**: 成功率、回應時間統計、每秒請求數
  - 📊 回應時間分布直方圖
  - 🥧 請求成功率餅圖
  - 📈 回應時間趨勢圖
  - 📦 回應時間統計箱線圖
- **測試二**: TPM統計、多用戶性能分析、Token吞吐量報告
  - 🚀 TPM (每分鐘Token數) 趨勢圖
  - 👥 各用戶查詢統計圖
  - ✅ 各用戶成功率比較圖
  - 🎯 響應時間 vs Token數量散點圖
- 圖表會根據測試類型自動切換顯示
- 所有操作都會記錄在即時日誌中

## 🏗️ 系統架構與技術實現

### 核心架構
```
llmstresstest/
├── app.py                     # Flask主應用程式
├── database.py                # SQLite資料庫管理
├── hardware_info.py           # 硬體資訊檢測模組
├── ollama_client.py           # Ollama API客戶端
├── stress_test_simple.py      # 基礎壓力測試管理器
├── multi_user_stress_test.py  # 多用戶測試管理器
├── multi_user_test_config.py  # 多用戶測試配置和數據結構
├── requirements.txt           # Python依賴列表
├── templates/
│   ├── index.html             # 主頁面模板
│   ├── history.html           # 歷史記錄管理頁面
│   └── navbar.html            # 導覽列組件
├── static/js/
│   ├── app_simple.js          # 主頁面JavaScript
│   ├── history.js             # 歷史記錄頁面邏輯
│   └── history_charts.js      # 歷史記錄圖表生成
└── db.sqlite3                 # SQLite資料庫文件
```

### 技術棧
- **後端框架**：Flask (Python 3.8+)
- **資料庫**：SQLite 3 (輕量級，無需額外配置)
- **前端框架**：Bootstrap 5 + Plotly.js
- **並發處理**：ThreadPoolExecutor + threading.Lock
- **API通信**：RESTful API + AJAX輪詢
- **圖表引擎**：Plotly.js (支援互動式圖表)

### 關鍵技術實現

#### 並發控制與線程安全
- **基礎測試**：使用ThreadPoolExecutor管理固定數量的工作線程
- **多用戶測試**：使用Semaphore控制最大並發數，模擬真實資源限制
- **狀態同步**：threading.Lock確保測試狀態的線程安全更新
- **任務隊列**：queue.Queue實現線程間的任務分配

#### 實時監控與進度追蹤
- **AJAX輪詢**：前端每500ms查詢一次測試狀態
- **進度計算**：基於已完成任務數量的百分比計算
- **狀態管理**：starting → running → completed/error/stopped
- **資源監控**：即時獲取CPU、記憶體、GPU使用率

#### TPM計算算法
```python
def calculate_tpm(query_results, time_window_minutes=1):
    """
    基於滑動時間窗口的TPM計算
    1. 按時間戳排序所有查詢結果
    2. 以1分鐘為窗口，計算每個窗口內的Token總數
    3. 生成時間序列數據用於趨勢分析
    """
```

#### 資料庫設計
```sql
CREATE TABLE test_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id TEXT UNIQUE NOT NULL,
    test_name TEXT NOT NULL,
    test_type INTEGER NOT NULL,  -- 1:基礎測試, 2:多用戶測試
    test_time TIMESTAMP NOT NULL,
    model_name TEXT NOT NULL,
    hardware_info TEXT NOT NULL,  -- JSON格式
    test_config TEXT NOT NULL,    -- JSON格式
    test_results TEXT NOT NULL,   -- JSON格式
    test_statistics TEXT,         -- JSON格式
    -- 快速查詢欄位
    duration_seconds REAL,
    total_requests INTEGER,
    successful_requests INTEGER,
    failed_requests INTEGER,
    avg_response_time REAL
);
```

## 📡 API端點

### 基礎API
- `GET /` - 主頁面
- `GET /history` - 歷史記錄管理頁面
- `GET /api/hardware` - 獲取硬體資訊
- `GET /api/models` - 獲取可用模型列表

### 測試一API
- `POST /api/start_test` - 開始基礎壓力測試
- `POST /api/stop_test` - 停止基礎壓力測試
- `GET /api/test_status/<test_id>` - 獲取測試狀態
- `GET /api/test_charts/<test_id>` - 獲取測試圖表數據

### 測試二API
- `POST /api/start_multi_user_test` - 開始多用戶並發測試
- `POST /api/stop_multi_user_test` - 停止多用戶測試
- `GET /api/multi_user_test_status/<test_id>` - 獲取多用戶測試狀態
- `GET /api/multi_user_test_charts/<test_id>` - 獲取多用戶測試圖表數據

### 歷史記錄管理API
- `GET /api/history` - 獲取歷史記錄列表（支援分頁和篩選）
- `GET /api/history/<test_id>` - 獲取特定測試的詳細資料
- `DELETE /api/history/<test_id>` - 刪除測試記錄
- `GET /api/history/<test_id>/charts` - 獲取歷史測試的圖表數據

## 📊 歷史記錄管理

### 功能特色
- **完整記錄保存**：自動保存所有測試的配置、結果和硬體資訊
- **智能篩選**：支援按測試類型、模型名稱篩選歷史記錄
- **圖表重繪**：選擇任何歷史記錄可重新繪製原有圖表進行對比分析
- **統計儀表板**：顯示總記錄數、測試類型分布、最新測試時間等統計資訊
- **記錄管理**：支援刪除不需要的測試記錄

### 使用方法
1. **查看歷史記錄**：點擊導覽列的「歷史記錄」進入管理頁面
2. **篩選記錄**：使用測試類型和模型名稱篩選器快速找到目標記錄
3. **重繪圖表**：點擊任何記錄卡片，在頁面下方重新顯示原有圖表
4. **刪除記錄**：hover到記錄卡片上，點擊刪除按鈕移除不需要的記錄

### 數據保存內容
每個測試記錄包含：
- **基本資訊**：測試時間、測試類型、模型名稱、持續時間
- **硬體快照**：測試時的CPU、記憶體、GPU使用率和規格
- **測試配置**：完整的測試參數設定
- **原始結果**：所有查詢的詳細結果數據
- **統計摘要**：成功率、回應時間、TPM等關鍵指標

## 🎯 測試結果說明

### 基礎壓力測試指標
- **總請求數**: 執行的總請求數量
- **成功請求數**: 成功完成的請求數量
- **失敗請求數**: 失敗的請求數量
- **成功率**: 成功請求的百分比
- **最小/最大回應時間**: 最快和最慢的回應時間
- **平均回應時間**: 所有成功請求的平均回應時間
- **中位數回應時間**: 回應時間的中位數
- **標準差**: 回應時間的標準差
- **每秒請求數**: 平均每秒處理的請求數量

### 多用戶測試指標
- **總查詢數**: 所有用戶執行的查詢總數
- **成功查詢數**: 成功完成的查詢數量
- **總Token數**: 所有回應的Token總數
- **平均TPM**: 整個測試期間的平均每分鐘Token數
- **峰值TPM**: 測試期間的最高每分鐘Token數
- **用戶統計**: 每個用戶的查詢數量、成功率、Token數量
- **回應時間分析**: 最小、最大、平均回應時間

## 🔧 故障排除

### 常見問題

1. **Ollama服務器連接失敗**
   - 確保Ollama服務器正在運行: `ollama serve`
   - 檢查服務器地址是否正確 (預設: http://localhost:11434)

2. **沒有可用模型**
   - 確保已下載Ollama模型: `ollama pull <model-name>`
   - 檢查模型列表: `ollama list`

3. **硬體資訊顯示錯誤**
   - 某些硬體資訊可能需要管理員權限
   - GPU資訊需要安裝相應的驅動程式

4. **測試執行緩慢**
   - 降低並發請求數
   - 選擇較小的模型進行測試
   - 檢查系統資源使用情況

5. **歷史記錄無法顯示**
   - 檢查db.sqlite3文件是否存在且可讀寫
   - 確認測試已完全完成（狀態為completed）
   - 重新啟動應用程式重新初始化資料庫

6. **多用戶測試TPM為0**
   - 確認模型回應包含有效的Token數據
   - 檢查測試持續時間是否足夠長（建議至少1分鐘）
   - 驗證查詢是否成功完成

## 🚀 性能優化建議

### 硬體配置建議
- **CPU**: 多核心處理器，建議8核心以上
- **記憶體**: 16GB以上，大型模型需要32GB+
- **GPU**: 支援CUDA的NVIDIA顯卡（可選，但能顯著提升性能）
- **儲存**: SSD硬碟，提升模型載入速度

### 測試配置建議
- **基礎測試**: 並發數建議從CPU核心數開始，逐步增加
- **多用戶測試**: 用戶數建議從2-3個開始，觀察系統負載
- **測試時長**: 建議每次測試至少持續1-2分鐘以獲得穩定數據
- **提示詞選擇**: 使用中等長度的提示詞（50-200字）獲得平衡的測試結果

## 📈 測試結果解讀

### 基礎壓力測試結果分析
- **回應時間分布**: 正常分布表示系統穩定，長尾分布可能表示資源瓶頸
- **成功率**: 95%以上為優秀，90-95%為良好，低於90%需要調整配置
- **回應時間趨勢**: 平穩趨勢表示穩定，上升趨勢可能表示記憶體洩漏或過熱

### 多用戶測試結果分析
- **TPM趨勢**: 穩定的TPM表示良好的吞吐量，波動大可能表示資源競爭
- **用戶成功率**: 各用戶成功率應該相近，差異大表示負載不均
- **回應時間vs用戶數**: 線性增長正常，指數增長表示系統接近極限

## 🛠️ 開發與擴展

### 核心模組說明
- **stress_test_simple.py**: 基礎壓力測試的核心邏輯，使用ThreadPoolExecutor實現並發控制
- **multi_user_stress_test.py**: 多用戶測試管理器，實現用戶會話管理和TPM計算
- **multi_user_test_config.py**: 數據結構定義和50組內建提示詞庫
- **database.py**: SQLite資料庫操作，支援測試記錄的CRUD操作
- **hardware_info.py**: 跨平台硬體資訊檢測，支援CPU、記憶體、GPU監控
- **ollama_client.py**: Ollama API客戶端，處理模型查詢和回應解析

### 擴展建議
- **測試類型**: 可添加更多測試模式，如長時間穩定性測試、記憶體洩漏測試
- **監控指標**: 增加網路延遲、磁碟I/O、溫度監控等指標
- **圖表功能**: 添加更多圖表類型，如熱力圖、3D散點圖等
- **報告生成**: 支援PDF、Excel格式的測試報告導出
- **多模型對比**: 支援同時測試多個模型並進行性能對比
- **自動化測試**: 支援定時測試和CI/CD整合

### 貢獻指南
1. Fork本專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟Pull Request

## 📄 授權條款

本專案採用MIT授權條款。詳見 [LICENSE](LICENSE) 文件。

## 🤝 社群與支援

- **GitHub Issues**: 報告Bug或提出功能請求
- **Discussions**: 技術討論和使用經驗分享
- **Wiki**: 詳細的使用教學和最佳實踐

## 🙏 致謝

感謝以下開源專案的支持：
- [Ollama](https://ollama.ai/) - 本地LLM運行環境
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [Bootstrap](https://getbootstrap.com/) - UI框架
- [Plotly.js](https://plotly.com/javascript/) - 圖表庫
- [psutil](https://psutil.readthedocs.io/) - 系統監控庫

---

**版本**: 2.0
**最後更新**: 2025年7月
**維護狀態**: 積極維護中 🚀
