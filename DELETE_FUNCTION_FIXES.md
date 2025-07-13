# 歷史記錄刪除功能修正

## 問題描述
在歷史記錄頁面中，刪除記錄時會出現以下問題：
1. 程式確實刪除了記錄，但網頁顯示刪除錯誤訊息
2. 刪除後沒有重新整理頁面資料
3. 批量刪除功能不完整

## 修正內容

### 1. 改善錯誤處理和成功提示

**修正前：**
- 只有錯誤提示，沒有成功提示
- 錯誤處理不夠詳細

**修正後：**
- 添加了 `showSuccess()` 函數顯示成功訊息
- 改善了錯誤處理，包含HTTP狀態碼檢查
- 在刪除成功後顯示明確的成功訊息

### 2. 修正刪除後的頁面更新

**修正前：**
```javascript
.then(data => {
    if (data.success) {
        loadHistoryRecords(currentPage);
        // 隱藏圖表邏輯
    } else {
        showError('刪除記錄失敗: ' + data.error);
    }
})
```

**修正後：**
```javascript
.then(data => {
    if (data.success) {
        showSuccess('測試記錄已成功刪除');
        
        // 如果刪除的是當前查看圖表的記錄，隱藏圖表
        const chartSelectedCard = document.querySelector('.history-card.chart-selected');
        if (chartSelectedCard && chartSelectedCard.dataset.testId === testId) {
            document.getElementById('charts-section').style.display = 'none';
        }
        
        // 重新載入歷史記錄
        loadHistoryRecords(currentPage);
    } else {
        showError('刪除記錄失敗: ' + (data.error || '未知錯誤'));
    }
})
```

### 3. 完善批量刪除功能

**新增功能：**
- 為每個記錄添加複選框
- 實現 `toggleRecordSelection()` 函數處理複選框選擇
- 實現 `deleteSelectedRecords()` 函數處理批量刪除
- 實現 `confirmDelete()` 函數確認批量刪除
- 添加 `updateDeleteButtonState()` 函數更新刪除按鈕狀態

### 4. 改善選擇狀態管理

**修正前：**
- 只有一種選中狀態，用於圖表查看和批量操作

**修正後：**
- 分離圖表選中狀態（`.chart-selected`）和批量操作選中狀態（`.selected`）
- 圖表選中：藍色邊框，用於查看圖表
- 批量操作選中：紅色邊框，用於批量刪除

### 5. 改善用戶體驗

**新增功能：**
- 刪除按鈕顯示選中記錄數量
- 批量刪除前顯示確認對話框，列出要刪除的記錄
- 成功/錯誤訊息使用表情符號增強視覺效果
- 刪除後自動重新載入記錄列表

## 修正的文件

### templates/history.html
1. **CSS樣式修正：**
   - 添加 `.chart-selected` 樣式
   - 區分批量選擇和圖表選擇的視覺效果

2. **HTML結構修正：**
   - 為每個記錄添加複選框
   - 調整記錄卡片的佈局

3. **JavaScript函數修正：**
   - `showSuccess()` - 新增成功提示函數
   - `deleteRecord()` - 改善單個記錄刪除
   - `selectRecord()` - 修正為圖表選擇
   - `toggleRecordSelection()` - 新增批量選擇功能
   - `deleteSelectedRecords()` - 新增批量刪除功能
   - `confirmDelete()` - 新增批量刪除確認
   - `updateDeleteButtonState()` - 新增按鈕狀態更新

## 使用說明

### 單個記錄刪除
1. 點擊記錄卡片右上角的垃圾桶圖標
2. 確認刪除對話框
3. 系統顯示成功訊息並自動重新載入記錄

### 批量記錄刪除
1. 勾選要刪除的記錄前面的複選框
2. 點擊頁面上方的"刪除選中"按鈕
3. 在確認對話框中查看要刪除的記錄列表
4. 點擊"確認刪除"
5. 系統顯示刪除結果並自動重新載入記錄

### 查看圖表
1. 點擊記錄卡片（不是複選框）
2. 記錄卡片顯示藍色邊框表示已選中查看圖表
3. 圖表顯示在頁面下方

## 測試建議

1. **單個刪除測試：**
   - 刪除一個記錄，確認顯示成功訊息
   - 確認記錄從列表中消失
   - 如果刪除的是當前查看的記錄，確認圖表區域隱藏

2. **批量刪除測試：**
   - 選擇多個記錄，確認刪除按鈕狀態更新
   - 執行批量刪除，確認確認對話框顯示正確的記錄列表
   - 確認刪除後顯示正確的成功/失敗統計

3. **錯誤處理測試：**
   - 在網路斷開的情況下嘗試刪除，確認顯示適當的錯誤訊息
   - 嘗試刪除不存在的記錄，確認顯示適當的錯誤訊息

## 注意事項

- 所有修正都保持向後兼容
- 後端API沒有修改，只修正了前端邏輯
- 刪除操作不可逆，請謹慎使用
- 建議在生產環境中添加更詳細的日誌記錄
