// 全局變量
let currentTestId = null;
let currentMultiUserTestId = null;
let progressInterval = null;
let multiUserProgressInterval = null;
let testResults = [];

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    setupEventListeners();
});

// 重新載入硬體資訊
function loadHardwareInfo() {
    fetch('/api/hardware')
        .then(response => response.json())
        .then(data => {
            displayHardwareInfo(data);
            addLog('硬體資訊已更新', 'success');
        })
        .catch(error => {
            console.error('載入硬體資訊失敗:', error);
            addLog('載入硬體資訊失敗', 'error');
        });
}

// 顯示硬體資訊
function displayHardwareInfo(hardwareInfo) {
    const container = document.getElementById('hardware-info');
    container.innerHTML = '';
    
    // CPU資訊
    if (hardwareInfo.cpu) {
        const cpuCard = createHardwareCard('CPU', 'bi-cpu', [
            `處理器: ${hardwareInfo.cpu.name || 'N/A'}`,
            `物理核心: ${hardwareInfo.cpu.cores_physical || 'N/A'}`,
            `邏輯核心: ${hardwareInfo.cpu.cores_logical || 'N/A'}`,
            `使用率: ${hardwareInfo.cpu.usage_percent || 'N/A'}%`
        ]);
        container.appendChild(cpuCard);
    }
    
    // 記憶體資訊
    if (hardwareInfo.memory) {
        const memoryCard = createHardwareCard('記憶體', 'bi-memory', [
            `總容量: ${hardwareInfo.memory.total_gb || 'N/A'} GB`,
            `可用: ${hardwareInfo.memory.available_gb || 'N/A'} GB`,
            `已使用: ${hardwareInfo.memory.used_gb || 'N/A'} GB`,
            `使用率: ${hardwareInfo.memory.usage_percent || 'N/A'}%`
        ]);
        container.appendChild(memoryCard);
    }
    
    // GPU資訊
    if (hardwareInfo.gpu && Array.isArray(hardwareInfo.gpu)) {
        hardwareInfo.gpu.forEach((gpu, index) => {
            const gpuCard = createHardwareCard(`GPU ${index + 1}`, 'bi-gpu-card', [
                `名稱: ${gpu.name || 'N/A'}`,
                `記憶體總量: ${gpu.memory_total_mb || 'N/A'} MB`,
                `記憶體使用: ${gpu.memory_used_mb || 'N/A'} MB`,
                `GPU使用率: ${gpu.gpu_usage_percent || 'N/A'}%`
            ]);
            container.appendChild(gpuCard);
        });
    } else if (hardwareInfo.gpu && hardwareInfo.gpu.message) {
        const gpuCard = createHardwareCard('GPU', 'bi-gpu-card', [hardwareInfo.gpu.message]);
        container.appendChild(gpuCard);
    }
    
    // 系統資訊
    if (hardwareInfo.system) {
        const systemCard = createHardwareCard('系統', 'bi-pc-display', [
            `作業系統: ${hardwareInfo.system.system || 'N/A'} ${hardwareInfo.system.release || ''}`,
            `架構: ${hardwareInfo.system.machine || 'N/A'}`,
            `Python版本: ${hardwareInfo.system.python_version || 'N/A'}`,
            `開機時間: ${hardwareInfo.system.boot_time || 'N/A'}`
        ]);
        container.appendChild(systemCard);
    }
}

// 創建硬體資訊卡片
function createHardwareCard(title, icon, items) {
    const col = document.createElement('div');
    col.className = 'col-md-6 col-lg-4 mb-3';
    
    col.innerHTML = `
        <div class="card hardware-card h-100">
            <div class="card-body">
                <h5 class="card-title">
                    <i class="bi ${icon}"></i> ${title}
                </h5>
                <ul class="list-unstyled mb-0">
                    ${items.map(item => `<li><small>${item}</small></li>`).join('')}
                </ul>
            </div>
        </div>
    `;
    
    return col;
}

// 設置事件監聽器
function setupEventListeners() {
    console.log('Setting up event listeners...');

    // 測試表單提交
    const form = document.getElementById('test-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submit event triggered');
            e.preventDefault();
            startTest(e);
            return false;
        });
        console.log('Form submit listener added');
    } else {
        console.error('Form element not found');
    }

    // 開始測試按鈕
    const startBtn = document.getElementById('start-test-btn');
    if (startBtn) {
        startBtn.addEventListener('click', function(e) {
            console.log('Start button clicked');
            e.preventDefault();
            startTest(e);
            return false;
        });
        console.log('Start button listener added');
    } else {
        console.error('Start button element not found');
    }

    // 停止測試按鈕
    const stopBtn = document.getElementById('stop-test-btn');
    if (stopBtn) {
        stopBtn.addEventListener('click', function(e) {
            console.log('Stop button clicked');
            e.preventDefault();
            stopTest();
            return false;
        });
        console.log('Stop button listener added');
    } else {
        console.error('Stop button element not found');
    }

    // 清除日誌按鈕
    const clearLogBtn = document.getElementById('clear-log-btn');
    if (clearLogBtn) {
        clearLogBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearLogs();
            return false;
        });
        console.log('Clear log button listener added');
    }

    // 測試二相關按鈕
    setupTest2EventListeners();

    console.log('Event listeners setup complete');
}

// 設置測試二的事件監聽器
function setupTest2EventListeners() {
    console.log('Setting up Test 2 event listeners...');

    // 重新載入模型按鈕 (測試二)
    const refreshModelsBtn2 = document.getElementById('refresh-models-btn-2');
    if (refreshModelsBtn2) {
        refreshModelsBtn2.addEventListener('click', function(e) {
            e.preventDefault();
            refreshModelsForTest2();
            return false;
        });
        console.log('Test 2 refresh models button listener added');
    }

    // 開始進階測試按鈕
    const startTestBtn2 = document.getElementById('start-test-btn-2');
    if (startTestBtn2) {
        startTestBtn2.addEventListener('click', function(e) {
            e.preventDefault();
            startAdvancedTest();
            return false;
        });
        console.log('Test 2 start button listener added');
    }

    // 停止測試按鈕 (測試二)
    const stopTestBtn2 = document.getElementById('stop-test-btn-2');
    if (stopTestBtn2) {
        stopTestBtn2.addEventListener('click', function(e) {
            e.preventDefault();
            stopAdvancedTest();
            return false;
        });
        console.log('Test 2 stop button listener added');
    }

    // 預覽配置按鈕
    const previewConfigBtn2 = document.getElementById('preview-config-btn-2');
    if (previewConfigBtn2) {
        previewConfigBtn2.addEventListener('click', function(e) {
            e.preventDefault();
            previewAdvancedTestConfig();
            return false;
        });
        console.log('Test 2 preview config button listener added');
    }

    console.log('Test 2 event listeners setup complete');
}

// 開始測試
function startTest(event) {
    console.log('startTest function called');

    // 防止表單提交導致頁面重新載入
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }

    const model = document.getElementById('model-select').value;
    const concurrentRequests = parseInt(document.getElementById('concurrent-requests').value);
    const totalRequests = parseInt(document.getElementById('total-requests').value);
    const prompt = document.getElementById('test-prompt').value;

    console.log('Form values:', { model, concurrentRequests, totalRequests, prompt });

    if (!model || !prompt) {
        alert('請填寫所有必要欄位');
        console.log('Validation failed: missing model or prompt');
        return false;
    }

    // 立即更新按鈕狀態
    disableStartButton();
    clearLogs();
    addLog('正在啟動測試...', 'info');
    showProgressContainer();

    const testConfig = {
        model: model,
        concurrent_requests: concurrentRequests,
        total_requests: totalRequests,
        prompt: prompt
    };

    fetch('/api/start_test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(testConfig)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentTestId = data.test_id;
            addLog(`測試已開始 (ID: ${data.test_id})`, 'success');
            startProgressPolling();
        } else {
            addLog(`啟動測試失敗: ${data.error}`, 'error');
            enableStartButton(); // 恢復按鈕狀態
        }
    })
    .catch(error => {
        console.error('啟動測試失敗:', error);
        addLog('啟動測試失敗', 'error');
        enableStartButton(); // 恢復按鈕狀態
    });

    return false; // 防止表單提交
}

// 停止測試
function stopTest() {
    if (!currentTestId) {
        return;
    }

    // 更新停止按鈕狀態
    const stopBtn = document.getElementById('stop-test-btn');
    stopBtn.disabled = true;
    stopBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 停止中...';

    fetch('/api/stop_test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({test_id: currentTestId})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addLog('正在停止測試...', 'warning');
            updateTestStatus('停止中');
        } else {
            addLog(`停止測試失敗: ${data.message}`, 'error');
            // 恢復停止按鈕狀態
            stopBtn.disabled = false;
            stopBtn.innerHTML = '<i class="bi bi-stop-circle"></i> 停止測試';
        }
    })
    .catch(error => {
        console.error('停止測試失敗:', error);
        addLog('停止測試失敗', 'error');
        // 恢復停止按鈕狀態
        stopBtn.disabled = false;
        stopBtn.innerHTML = '<i class="bi bi-stop-circle"></i> 停止測試';
    });
}

// 開始進度輪詢
function startProgressPolling() {
    if (progressInterval) {
        clearInterval(progressInterval);
    }
    
    progressInterval = setInterval(() => {
        if (currentTestId) {
            checkTestProgress();
        }
    }, 1000); // 每秒檢查一次
}

// 停止進度輪詢
function stopProgressPolling() {
    if (progressInterval) {
        clearInterval(progressInterval);
        progressInterval = null;
    }
}

// 檢查測試進度
function checkTestProgress() {
    fetch(`/api/test_status/${currentTestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addLog(`獲取測試狀態失敗: ${data.error}`, 'error');
                stopProgressPolling();
                enableStartButton();
                return;
            }
            
            updateProgress(data);
            
            if (data.status === 'completed') {
                addLog('測試完成！', 'success');
                updateTestStatus('已完成');
                if (data.statistics) {
                    showTestResults(data.statistics);
                }
                stopProgressPolling();
                enableStartButton();
            } else if (data.status === 'error') {
                addLog(`測試錯誤: ${data.error || '未知錯誤'}`, 'error');
                updateTestStatus('錯誤');
                stopProgressPolling();
                enableStartButton();
            } else if (data.status === 'stopped') {
                addLog('測試已停止', 'warning');
                updateTestStatus('已停止');
                stopProgressPolling();
                enableStartButton();
            }
        })
        .catch(error => {
            console.error('檢查測試進度失敗:', error);
            addLog('檢查測試進度失敗', 'error');
        });
}

// 更新進度
function updateProgress(data) {
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const completedCount = document.getElementById('completed-count');
    const failedCount = document.getElementById('failed-count');
    
    const progress = data.progress || 0;
    progressBar.style.width = `${progress}%`;
    progressBar.setAttribute('aria-valuenow', progress);
    progressText.textContent = `${progress.toFixed(1)}%`;
    completedCount.textContent = data.completed_requests || 0;
    failedCount.textContent = data.failed_requests || 0;
    
    // 計算平均回應時間
    if (data.current_results && data.current_results.length > 0) {
        const successfulResults = data.current_results.filter(r => r.success);
        if (successfulResults.length > 0) {
            const avgTime = successfulResults.reduce((sum, r) => sum + r.response_time, 0) / successfulResults.length;
            document.getElementById('avg-response-time').textContent = `${avgTime.toFixed(2)}s`;
            
            // 計算每秒請求數
            const totalTime = successfulResults.reduce((sum, r) => sum + r.response_time, 0);
            const rps = totalTime > 0 ? successfulResults.length / totalTime : 0;
            document.getElementById('requests-per-second').textContent = rps.toFixed(2);
        }
    }
    
    // 更新狀態
    if (data.status) {
        updateTestStatus(getStatusDisplayName(data.status));
    }
}

// 獲取狀態顯示名稱
function getStatusDisplayName(status) {
    const statusMap = {
        'starting': '啟動中',
        'running': '運行中',
        'completed': '已完成',
        'error': '錯誤',
        'stopping': '停止中',
        'stopped': '已停止'
    };
    return statusMap[status] || status;
}

// 顯示進度容器
function showProgressContainer() {
    document.getElementById('progress-container').style.display = 'block';
    testResults = [];
}

// 顯示測試結果
function showTestResults(statistics) {
    document.getElementById('test-results').style.display = 'block';

    // 切換到測試一圖表
    showTest1Charts();

    // 填充統計表格
    const tableBody = document.getElementById('statistics-table');
    tableBody.innerHTML = `
        <tr><td>總請求數</td><td>${statistics.total_requests || 0}</td></tr>
        <tr><td>成功請求數</td><td>${statistics.successful_requests || 0}</td></tr>
        <tr><td>失敗請求數</td><td>${statistics.failed_requests || 0}</td></tr>
        <tr><td>成功率</td><td>${(statistics.success_rate || 0).toFixed(2)}%</td></tr>
        <tr><td>最小回應時間</td><td>${statistics.response_time_stats?.min?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>最大回應時間</td><td>${statistics.response_time_stats?.max?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>平均回應時間</td><td>${statistics.response_time_stats?.mean?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>中位數回應時間</td><td>${statistics.response_time_stats?.median?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>標準差</td><td>${statistics.response_time_stats?.std_dev?.toFixed(2) || 'N/A'}s</td></tr>
        <tr><td>每秒請求數</td><td>${(statistics.requests_per_second || 0).toFixed(2)}</td></tr>
    `;

    // 載入測試一圖表
    loadTestCharts();
}

// 更新測試狀態
function updateTestStatus(status) {
    const statusBadge = document.getElementById('test-status');
    statusBadge.textContent = status;
    
    // 根據狀態更改顏色
    statusBadge.className = 'badge status-badge ms-2';
    switch(status) {
        case '運行中':
        case '啟動中':
            statusBadge.classList.add('bg-primary');
            break;
        case '已完成':
            statusBadge.classList.add('bg-success');
            break;
        case '錯誤':
            statusBadge.classList.add('bg-danger');
            break;
        case '停止中':
        case '已停止':
            statusBadge.classList.add('bg-warning');
            break;
        default:
            statusBadge.classList.add('bg-secondary');
    }
}

// 啟用/禁用測試控制項
function disableStartButton() {
    const startBtn = document.getElementById('start-test-btn');
    const stopBtn = document.getElementById('stop-test-btn');

    // 禁用開始按鈕並更改文字
    startBtn.disabled = true;
    startBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 測試中...';

    // 啟用停止按鈕
    stopBtn.disabled = false;

    // 禁用表單控制項，防止測試期間修改配置
    document.getElementById('model-select').disabled = true;
    document.getElementById('concurrent-requests').disabled = true;
    document.getElementById('total-requests').disabled = true;
    document.getElementById('test-prompt').disabled = true;
}

function enableStartButton() {
    const startBtn = document.getElementById('start-test-btn');
    const stopBtn = document.getElementById('stop-test-btn');

    // 恢復開始按鈕
    startBtn.disabled = false;
    startBtn.innerHTML = '<i class="bi bi-play-circle"></i> 開始測試';

    // 禁用停止按鈕並恢復文字
    stopBtn.disabled = true;
    stopBtn.innerHTML = '<i class="bi bi-stop-circle"></i> 停止測試';

    // 重新啟用表單控制項
    document.getElementById('model-select').disabled = false;
    document.getElementById('concurrent-requests').disabled = false;
    document.getElementById('total-requests').disabled = false;
    document.getElementById('test-prompt').disabled = false;

    currentTestId = null;
}

// 日誌功能
function addLog(message, type = 'info') {
    const logContainer = document.getElementById('log-container');
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = document.createElement('div');
    
    let className = '';
    switch(type) {
        case 'success':
            className = 'text-success';
            break;
        case 'error':
            className = 'text-danger';
            break;
        case 'warning':
            className = 'text-warning';
            break;
        case 'info':
        default:
            className = 'text-info';
    }
    
    logEntry.innerHTML = `<span class="text-muted">[${timestamp}]</span> <span class="${className}">${message}</span>`;
    logContainer.appendChild(logEntry);
    logContainer.scrollTop = logContainer.scrollHeight;
}

function clearLogs() {
    document.getElementById('log-container').innerHTML = '';
}

// 重新整理功能
function refreshHardwareInfo() {
    addLog('正在重新載入硬體資訊...', 'info');
    loadHardwareInfo();
}

function refreshModels() {
    addLog('正在重新載入模型列表...', 'info');
    fetch('/api/models')
        .then(response => response.json())
        .then(models => {
            const select = document.getElementById('model-select');
            select.innerHTML = '<option value="">請選擇模型...</option>';
            models.forEach(model => {
                const option = document.createElement('option');
                option.value = model.name;
                option.textContent = model.name;
                select.appendChild(option);
            });
            addLog(`已載入 ${models.length} 個模型`, 'success');
        })
        .catch(error => {
            console.error('載入模型失敗:', error);
            addLog('載入模型失敗', 'error');
        });
}

// 載入測試圖表
function loadTestCharts() {
    if (!currentTestId) {
        console.error('No current test ID available for charts');
        return;
    }

    addLog('正在載入圖表...', 'info');

    // 顯示載入指示器
    showChartLoadingIndicators();

    fetch(`/api/test_charts/${currentTestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                console.error('載入圖表失敗:', data.error);
                addLog(`載入圖表失敗: ${data.error}`, 'error');
                showChartErrorMessage(data.error);
                return;
            }

            // 顯示圖表
            displayCharts(data);
            addLog('圖表載入完成', 'success');
        })
        .catch(error => {
            console.error('載入圖表失敗:', error);
            addLog('載入圖表失敗', 'error');
            showChartErrorMessage('載入圖表時發生錯誤');
        });
}

// 顯示圖表載入指示器
function showChartLoadingIndicators() {
    const chartIds = ['response-time-histogram', 'success-rate-pie', 'response-time-timeline', 'response-time-box'];

    chartIds.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.innerHTML = `
                <div class="chart-loading">
                    <div class="spinner-border text-primary me-2" role="status">
                        <span class="visually-hidden">載入中...</span>
                    </div>
                    載入圖表中...
                </div>
            `;
        }
    });
}

// 顯示圖表錯誤訊息
function showChartErrorMessage(message) {
    const chartIds = ['response-time-histogram', 'success-rate-pie', 'response-time-timeline', 'response-time-box'];

    chartIds.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            container.innerHTML = `
                <div class="chart-loading text-danger">
                    <i class="bi bi-exclamation-triangle me-2"></i>
                    ${message}
                </div>
            `;
        }
    });
}

// 顯示圖表
function displayCharts(chartsData) {
    console.log('Displaying charts:', chartsData);

    // 回應時間分布直方圖
    if (chartsData.response_time_histogram) {
        try {
            const container = document.getElementById('response-time-histogram');
            container.innerHTML = ''; // 清除載入指示器

            const histogramData = JSON.parse(chartsData.response_time_histogram);
            Plotly.newPlot('response-time-histogram', histogramData.data, histogramData.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        } catch (error) {
            console.error('Error displaying histogram:', error);
            showChartError('response-time-histogram', '載入直方圖時發生錯誤');
        }
    }

    // 成功率餅圖
    if (chartsData.success_rate_pie) {
        try {
            const container = document.getElementById('success-rate-pie');
            container.innerHTML = ''; // 清除載入指示器

            const pieData = JSON.parse(chartsData.success_rate_pie);
            Plotly.newPlot('success-rate-pie', pieData.data, pieData.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        } catch (error) {
            console.error('Error displaying pie chart:', error);
            showChartError('success-rate-pie', '載入餅圖時發生錯誤');
        }
    }

    // 回應時間趨勢圖
    if (chartsData.response_time_timeline) {
        try {
            const container = document.getElementById('response-time-timeline');
            container.innerHTML = ''; // 清除載入指示器

            const timelineData = JSON.parse(chartsData.response_time_timeline);
            Plotly.newPlot('response-time-timeline', timelineData.data, timelineData.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        } catch (error) {
            console.error('Error displaying timeline:', error);
            showChartError('response-time-timeline', '載入趨勢圖時發生錯誤');
        }
    }

    // 回應時間統計箱線圖
    if (chartsData.response_time_box) {
        try {
            const container = document.getElementById('response-time-box');
            container.innerHTML = ''; // 清除載入指示器

            const boxData = JSON.parse(chartsData.response_time_box);
            Plotly.newPlot('response-time-box', boxData.data, boxData.layout, {
                responsive: true,
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d']
            });
        } catch (error) {
            console.error('Error displaying box plot:', error);
            showChartError('response-time-box', '載入箱線圖時發生錯誤');
        }
    }
}

// 顯示單個圖表錯誤
function showChartError(chartId, message) {
    const container = document.getElementById(chartId);
    if (container) {
        container.innerHTML = `
            <div class="chart-loading text-danger">
                <i class="bi bi-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }
}

// 清除日誌
function clearLogs() {
    const logContainer = document.getElementById('log-messages');
    if (logContainer) {
        logContainer.innerHTML = '';
        addLog('日誌已清除', 'info');
    }
}

// ===== 測試二相關函數 (暫未實作) =====

// 重新載入模型 (測試二)
function refreshModelsForTest2() {
    addLog('正在重新載入模型列表 (測試二)...', 'info');

    fetch('/api/models')
        .then(response => response.json())
        .then(models => {
            const select = document.getElementById('model-select-2');
            if (select) {
                select.innerHTML = '<option value="">請選擇模型...</option>';
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.name;
                    option.textContent = model.name;
                    select.appendChild(option);
                });
                addLog(`已載入 ${models.length} 個模型 (測試二)`, 'success');
            }
        })
        .catch(error => {
            console.error('載入模型失敗:', error);
            addLog('載入模型失敗 (測試二)', 'error');
        });
}

// 開始進階測試
function startAdvancedTest() {
    console.log('startAdvancedTest function called');

    // 獲取測試配置
    const config = getMultiUserTestConfig();

    // 詳細驗證配置
    const validation = validateMultiUserConfig(config);
    if (!validation.valid) {
        alert(`配置錯誤: ${validation.message}`);
        return;
    }

    // 立即更新按鈕狀態
    disableMultiUserTestButtons();
    clearLogs();
    addLog('正在啟動多用戶測試...', 'info');
    showProgressContainer();

    fetch('/api/start_multi_user_test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            currentMultiUserTestId = data.test_id;
            addLog(`多用戶測試已開始 (ID: ${data.test_id})`, 'success');
            addLog(`配置: ${config.user_count}個用戶，每用戶${config.queries_per_user}次查詢`, 'info');
            startMultiUserProgressPolling();
        } else {
            addLog(`啟動多用戶測試失敗: ${data.error}`, 'error');
            enableMultiUserTestButtons();
        }
    })
    .catch(error => {
        console.error('啟動多用戶測試失敗:', error);
        addLog('啟動多用戶測試失敗', 'error');
        enableMultiUserTestButtons();
    });
}

// 停止多用戶測試
function stopAdvancedTest() {
    if (!currentMultiUserTestId) {
        return;
    }

    // 更新停止按鈕狀態
    const stopBtn = document.getElementById('stop-test-btn-2');
    if (stopBtn) {
        stopBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 停止中...';
        stopBtn.disabled = true;
    }

    addLog('正在停止多用戶測試...', 'warning');

    fetch('/api/stop_multi_user_test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ test_id: currentMultiUserTestId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            addLog('多用戶測試已停止', 'warning');
        } else {
            addLog(`停止測試失敗: ${data.message}`, 'error');
        }
    })
    .catch(error => {
        console.error('停止測試失敗:', error);
        addLog('停止測試失敗', 'error');
    });

    // 停止進度輪詢
    if (multiUserProgressInterval) {
        clearInterval(multiUserProgressInterval);
        multiUserProgressInterval = null;
    }
}

// 預覽多用戶測試配置
function previewAdvancedTestConfig() {
    const config = getMultiUserTestConfig();

    // 創建更友好的配置顯示
    const configDisplay = {
        "模型": config.model || "未選擇",
        "用戶數量": config.user_count,
        "每用戶查詢次數": config.queries_per_user,
        "最大並發限制": config.concurrent_limit,
        "查詢間隔(秒)": config.delay_between_queries,
        "提示詞來源": config.use_random_prompts ? "內建50組隨機提示詞" : "自定義提示詞",
        "TPM監控": config.enable_tpm_monitoring ? "啟用" : "停用",
        "詳細日誌": config.enable_detailed_logging ? "啟用" : "停用"
    };

    if (!config.use_random_prompts && config.custom_prompts) {
        const prompts = config.custom_prompts.split('\n').filter(p => p.trim());
        configDisplay["自定義提示詞數量"] = prompts.length;
    }

    let configHtml = `
        <div class="modal fade" id="configPreviewModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="bi bi-people"></i> 多用戶測試配置預覽
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h6 class="text-primary">📋 測試配置</h6>
                                <table class="table table-sm">
                                    ${Object.entries(configDisplay).map(([key, value]) =>
                                        `<tr><td><strong>${key}:</strong></td><td>${value}</td></tr>`
                                    ).join('')}
                                </table>
                            </div>
                            <div class="col-md-6">
                                <h6 class="text-info">📊 預期結果</h6>
                                <ul class="list-unstyled">
                                    <li><i class="bi bi-check-circle text-success"></i> 總查詢數: ${config.user_count * config.queries_per_user}</li>
                                    <li><i class="bi bi-clock text-warning"></i> 預估時間: ${Math.ceil((config.user_count * config.queries_per_user * 3) / config.concurrent_limit)}秒</li>
                                    <li><i class="bi bi-speedometer text-primary"></i> 將測量TPM性能</li>
                                    <li><i class="bi bi-graph-up text-info"></i> 提供詳細統計報告</li>
                                </ul>
                            </div>
                        </div>

                        <div class="mt-3">
                            <h6 class="text-secondary">🔧 原始JSON配置</h6>
                            <pre class="bg-light p-3 rounded small">${JSON.stringify(config, null, 2)}</pre>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
                            <i class="bi bi-x-circle"></i> 關閉
                        </button>
                        <button type="button" class="btn btn-primary" onclick="copyConfigToClipboard()">
                            <i class="bi bi-clipboard"></i> 複製配置
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    // 移除舊的模態框
    const existingModal = document.getElementById('configPreviewModal');
    if (existingModal) {
        existingModal.remove();
    }

    // 添加新的模態框
    document.body.insertAdjacentHTML('beforeend', configHtml);

    // 顯示模態框
    const modal = new bootstrap.Modal(document.getElementById('configPreviewModal'));
    modal.show();
}

// 獲取多用戶測試配置
function getMultiUserTestConfig() {
    const useRandomPrompts = document.getElementById('use-random-prompts-2')?.checked || true;
    const customPrompts = document.getElementById('custom-prompts-2')?.value || '';

    return {
        model: document.getElementById('model-select-2')?.value || '',
        user_count: parseInt(document.getElementById('user-count-2')?.value) || 1,
        queries_per_user: parseInt(document.getElementById('queries-per-user-2')?.value) || 5,
        concurrent_limit: parseInt(document.getElementById('concurrent-limit-2')?.value) || 5,
        delay_between_queries: parseFloat(document.getElementById('query-delay-2')?.value) || 0.5,
        use_random_prompts: useRandomPrompts,
        custom_prompts: useRandomPrompts ? '' : customPrompts,
        enable_tpm_monitoring: document.getElementById('enable-tpm-monitoring-2')?.checked || true,
        enable_detailed_logging: document.getElementById('enable-detailed-logs-2')?.checked || false
    };
}

// 獲取進階測試配置 (保留原函數以兼容)
function getAdvancedTestConfig() {
    return getMultiUserTestConfig();
}

// 複製配置到剪貼板
function copyConfigToClipboard() {
    const config = getMultiUserTestConfig();
    const configText = JSON.stringify(config, null, 2);

    navigator.clipboard.writeText(configText).then(() => {
        addLog('配置已複製到剪貼板', 'success');
    }).catch(err => {
        console.error('複製失敗:', err);
        addLog('複製配置失敗', 'error');
    });
}

// ===== 多用戶測試專用函數 =====

// 禁用多用戶測試按鈕
function disableMultiUserTestButtons() {
    const startBtn = document.getElementById('start-test-btn-2');
    const stopBtn = document.getElementById('stop-test-btn-2');

    if (startBtn) {
        startBtn.innerHTML = '<i class="bi bi-hourglass-split"></i> 測試中...';
        startBtn.disabled = true;
    }

    if (stopBtn) {
        stopBtn.innerHTML = '<i class="bi bi-stop-circle"></i> 停止測試';
        stopBtn.disabled = false;
    }

    // 禁用表單控件
    disableFormControls('test-form-2');
}

// 啟用多用戶測試按鈕
function enableMultiUserTestButtons() {
    const startBtn = document.getElementById('start-test-btn-2');
    const stopBtn = document.getElementById('stop-test-btn-2');

    if (startBtn) {
        startBtn.innerHTML = '<i class="bi bi-people-fill"></i> 開始多用戶測試';
        startBtn.disabled = false;
    }

    if (stopBtn) {
        stopBtn.innerHTML = '<i class="bi bi-stop-circle"></i> 停止測試';
        stopBtn.disabled = true;
    }

    // 啟用表單控件
    enableFormControls('test-form-2');
}

// 開始多用戶進度輪詢
function startMultiUserProgressPolling() {
    if (multiUserProgressInterval) {
        clearInterval(multiUserProgressInterval);
    }

    multiUserProgressInterval = setInterval(checkMultiUserTestProgress, 2000);
    checkMultiUserTestProgress(); // 立即檢查一次
}

// 檢查多用戶測試進度
function checkMultiUserTestProgress() {
    if (!currentMultiUserTestId) {
        return;
    }

    fetch(`/api/multi_user_test_status/${currentMultiUserTestId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addLog(`獲取測試狀態失敗: ${data.error}`, 'error');
                return;
            }

            updateMultiUserTestStatus(data);

            if (data.status === 'completed' || data.status === 'error' || data.status === 'stopped') {
                // 測試完成
                if (multiUserProgressInterval) {
                    clearInterval(multiUserProgressInterval);
                    multiUserProgressInterval = null;
                }

                enableMultiUserTestButtons();

                if (data.status === 'completed') {
                    addLog('多用戶測試完成！', 'success');
                    if (data.statistics) {
                        showMultiUserTestResults(data.statistics);
                    }
                } else if (data.status === 'error') {
                    addLog(`測試發生錯誤: ${data.error}`, 'error');
                    // 即使出錯也嘗試顯示部分結果
                    if (data.statistics) {
                        showMultiUserTestResults(data.statistics);
                    }
                } else if (data.status === 'stopped') {
                    addLog('測試已停止', 'warning');
                    // 顯示已完成部分的結果
                    if (data.statistics) {
                        showMultiUserTestResults(data.statistics);
                    }
                }

                currentMultiUserTestId = null;
            }
        })
        .catch(error => {
            console.error('檢查測試進度失敗:', error);
            addLog('檢查測試進度失敗', 'error');
        });
}

// 更新多用戶測試狀態
function updateMultiUserTestStatus(data) {
    // 更新進度條
    updateProgress(data.progress || 0);

    // 更新狀態顯示
    updateTestStatus(data.status || 'unknown');

    // 顯示實時統計
    if (data.current_tpm !== undefined) {
        addLog(`當前TPM: ${data.current_tpm.toFixed(1)} tokens/分鐘`, 'info');
    }

    if (data.active_users !== undefined) {
        addLog(`活躍用戶數: ${data.active_users}`, 'info');
    }
}

// 顯示多用戶測試結果
function showMultiUserTestResults(statistics) {
    addLog('=== 多用戶測試結果 ===', 'success');
    addLog(`總查詢數: ${statistics.total_queries}`, 'info');
    addLog(`成功查詢: ${statistics.successful_queries}`, 'info');
    addLog(`失敗查詢: ${statistics.failed_queries}`, 'info');
    addLog(`總Token數: ${statistics.total_tokens}`, 'info');
    addLog(`平均TPM: ${statistics.average_tpm?.toFixed(1) || 0} tokens/分鐘`, 'info');
    addLog(`峰值TPM: ${statistics.peak_tpm?.toFixed(1) || 0} tokens/分鐘`, 'info');
    addLog(`平均響應時間: ${statistics.average_response_time?.toFixed(2) || 0} 秒`, 'info');

    // 顯示測試結果區域
    document.getElementById('test-results').style.display = 'block';

    // 切換到測試二圖表
    showTest2Charts();

    // 填充統計表格（重用現有的表格）
    const tableBody = document.getElementById('statistics-table');
    if (tableBody) {
        tableBody.innerHTML = `
            <tr><td>總查詢數</td><td>${statistics.total_queries}</td></tr>
            <tr><td>成功查詢</td><td>${statistics.successful_queries}</td></tr>
            <tr><td>失敗查詢</td><td>${statistics.failed_queries}</td></tr>
            <tr><td>成功率</td><td>${((statistics.successful_queries / statistics.total_queries) * 100).toFixed(1)}%</td></tr>
            <tr><td>總Token數</td><td>${statistics.total_tokens}</td></tr>
            <tr><td>平均TPM</td><td>${statistics.average_tpm?.toFixed(1) || 0} tokens/分鐘</td></tr>
            <tr><td>峰值TPM</td><td>${statistics.peak_tpm?.toFixed(1) || 0} tokens/分鐘</td></tr>
            <tr><td>平均響應時間</td><td>${statistics.average_response_time?.toFixed(2) || 0} 秒</td></tr>
        `;
    }

    // 載入測試二圖表
    if (currentMultiUserTestId) {
        loadMultiUserTestCharts(currentMultiUserTestId);
    }
}

// 驗證多用戶測試配置
function validateMultiUserConfig(config) {
    // 檢查必填欄位
    if (!config.model) {
        return { valid: false, message: '請選擇模型' };
    }

    if (!config.user_count || config.user_count < 1 || config.user_count > 10) {
        return { valid: false, message: '用戶數量必須在1-10之間' };
    }

    if (!config.queries_per_user || config.queries_per_user < 1 || config.queries_per_user > 50) {
        return { valid: false, message: '每用戶查詢次數必須在1-50之間' };
    }

    if (!config.concurrent_limit || config.concurrent_limit < 1 || config.concurrent_limit > 20) {
        return { valid: false, message: '並發限制必須在1-20之間' };
    }

    if (config.delay_between_queries < 0 || config.delay_between_queries > 10) {
        return { valid: false, message: '查詢間隔必須在0-10秒之間' };
    }

    // 檢查自定義提示詞
    if (!config.use_random_prompts) {
        if (!config.custom_prompts || config.custom_prompts.trim() === '') {
            return { valid: false, message: '使用自定義提示詞時，請輸入至少一個提示詞' };
        }

        const prompts = config.custom_prompts.split('\n').filter(p => p.trim());
        if (prompts.length === 0) {
            return { valid: false, message: '請輸入有效的自定義提示詞' };
        }
    }

    // 檢查總查詢數是否合理
    const totalQueries = config.user_count * config.queries_per_user;
    if (totalQueries > 200) {
        return {
            valid: false,
            message: `總查詢數 (${totalQueries}) 過多，建議減少用戶數量或查詢次數`
        };
    }

    // 檢查並發設定是否合理
    if (config.concurrent_limit > config.user_count) {
        return {
            valid: false,
            message: '並發限制不應超過用戶數量'
        };
    }

    return { valid: true, message: '配置驗證通過' };
}

// 禁用/啟用表單控件的輔助函數
function disableFormControls(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.disabled = true;
        });
    }
}

function enableFormControls(formId) {
    const form = document.getElementById(formId);
    if (form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.disabled = false;
        });
    }
}

// ===== 圖表管理函數 =====

// 顯示測試一圖表
function showTest1Charts() {
    const test1Charts = document.getElementById('test1-charts');
    const test2Charts = document.getElementById('test2-charts');
    const chartsTitle = document.getElementById('charts-title');

    if (test1Charts) test1Charts.style.display = 'block';
    if (test2Charts) test2Charts.style.display = 'none';
    if (chartsTitle) chartsTitle.textContent = '視覺化分析 - 基礎壓力測試';
}

// 顯示測試二圖表
function showTest2Charts() {
    const test1Charts = document.getElementById('test1-charts');
    const test2Charts = document.getElementById('test2-charts');
    const chartsTitle = document.getElementById('charts-title');

    if (test1Charts) test1Charts.style.display = 'none';
    if (test2Charts) test2Charts.style.display = 'block';
    if (chartsTitle) chartsTitle.textContent = '視覺化分析 - 多用戶並發測試';
}

// 載入多用戶測試圖表
function loadMultiUserTestCharts(testId) {
    addLog('正在載入測試圖表...', 'info');

    fetch(`/api/multi_user_test_charts/${testId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                addLog(`載入圖表失敗: ${data.error}`, 'error');
                return;
            }

            // 顯示各種圖表
            if (data.tpm_timeline) {
                const tpmChart = JSON.parse(data.tpm_timeline);
                Plotly.newPlot('tpm-timeline', tpmChart.data, tpmChart.layout, {responsive: true});
                addLog('TPM趨勢圖已載入', 'success');
            }

            if (data.user_distribution) {
                const userChart = JSON.parse(data.user_distribution);
                Plotly.newPlot('user-distribution', userChart.data, userChart.layout, {responsive: true});
                addLog('用戶分布圖已載入', 'success');
            }

            if (data.user_success_rate) {
                const successChart = JSON.parse(data.user_success_rate);
                Plotly.newPlot('user-success-rate', successChart.data, successChart.layout, {responsive: true});
                addLog('用戶成功率圖已載入', 'success');
            }

            if (data.response_vs_tokens) {
                const scatterChart = JSON.parse(data.response_vs_tokens);
                Plotly.newPlot('response-vs-tokens', scatterChart.data, scatterChart.layout, {responsive: true});
                addLog('響應時間vs Token分析圖已載入', 'success');
            }

            addLog('所有測試二圖表載入完成', 'success');
        })
        .catch(error => {
            console.error('載入圖表失敗:', error);
            addLog('載入圖表時發生錯誤', 'error');
        });
}
