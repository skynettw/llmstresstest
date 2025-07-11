// 歷史記錄圖表生成函數

// 生成基礎測試圖表
function generateBasicTestCharts(results, statistics) {
    const successfulResults = results.filter(r => r.success);
    const failedResults = results.filter(r => !r.success);
    
    // 1. 回應時間分布直方圖
    if (successfulResults.length > 0) {
        const responseTimes = successfulResults.map(r => r.response_time);
        
        const histogramData = [{
            x: responseTimes,
            type: 'histogram',
            nbinsx: 20,
            name: '回應時間分布',
            marker: {
                color: 'rgba(55, 128, 191, 0.7)',
                line: {
                    color: 'rgba(55, 128, 191, 1.0)',
                    width: 1
                }
            }
        }];
        
        const histogramLayout = {
            title: '回應時間分布',
            xaxis: { title: '回應時間 (秒)' },
            yaxis: { title: '請求數量' },
            bargap: 0.1,
            template: 'plotly_white'
        };
        
        Plotly.newPlot('response-time-histogram', histogramData, histogramLayout);
    }
    
    // 2. 成功率餅圖
    if (results.length > 0) {
        const pieData = [{
            labels: ['成功', '失敗'],
            values: [successfulResults.length, failedResults.length],
            type: 'pie',
            hole: 0.3,
            marker: {
                colors: ['#28a745', '#dc3545']
            }
        }];
        
        const pieLayout = {
            title: '請求成功率',
            template: 'plotly_white'
        };
        
        Plotly.newPlot('success-rate-pie', pieData, pieLayout);
    }
    
    // 3. 回應時間趨勢圖
    if (successfulResults.length > 0) {
        const taskIds = successfulResults.map((r, i) => r.task_id || i);
        const responseTimes = successfulResults.map(r => r.response_time);
        
        const timelineData = [{
            x: taskIds,
            y: responseTimes,
            type: 'scatter',
            mode: 'lines+markers',
            name: '回應時間',
            line: { color: 'rgb(55, 128, 191)', width: 2 },
            marker: { size: 6 }
        }];
        
        // 添加平均線
        if (statistics.response_time_stats && statistics.response_time_stats.mean) {
            const meanTime = statistics.response_time_stats.mean;
            timelineData.push({
                x: taskIds,
                y: new Array(taskIds.length).fill(meanTime),
                type: 'scatter',
                mode: 'lines',
                name: `平均值: ${meanTime.toFixed(2)}s`,
                line: { color: 'red', dash: 'dash' }
            });
        }
        
        const timelineLayout = {
            title: '回應時間趨勢',
            xaxis: { title: '請求序號' },
            yaxis: { title: '回應時間 (秒)' },
            template: 'plotly_white'
        };
        
        Plotly.newPlot('response-time-timeline', timelineData, timelineLayout);
    }
}

// 生成多用戶測試圖表
function generateMultiUserTestCharts(queryResults, tpmSamples) {
    const successfulResults = queryResults.filter(r => r.success);
    
    // 1. TPM趨勢圖
    if (tpmSamples && tpmSamples.length > 0) {
        const timestamps = tpmSamples.map(sample => {
            const date = new Date(sample.timestamp);
            return date.toLocaleTimeString('zh-TW');
        });
        const tpmValues = tpmSamples.map(sample => sample.tokens_per_minute);
        
        const tpmData = [{
            x: timestamps,
            y: tpmValues,
            type: 'scatter',
            mode: 'lines+markers',
            name: 'TPM',
            line: { color: '#28a745', width: 3 },
            marker: { size: 6 }
        }];
        
        const tpmLayout = {
            title: 'TPM (每分鐘Token數) 趨勢',
            xaxis: { title: '時間' },
            yaxis: { title: 'TPM (tokens/分鐘)' },
            template: 'plotly_white',
            hovermode: 'x unified'
        };
        
        Plotly.newPlot('tpm-timeline', tpmData, tpmLayout);
    }
    
    // 2. 用戶查詢分布圖
    if (successfulResults.length > 0) {
        const userStats = {};
        
        // 統計每個用戶的數據
        successfulResults.forEach(result => {
            const userId = result.user_id;
            if (!userStats[userId]) {
                userStats[userId] = { queries: 0, tokens: 0 };
            }
            userStats[userId].queries += 1;
            userStats[userId].tokens += result.tokens_count || 0;
        });
        
        const users = Object.keys(userStats).map(id => `用戶 ${id}`);
        const queries = Object.values(userStats).map(stats => stats.queries);
        const tokens = Object.values(userStats).map(stats => stats.tokens);
        
        const userDistData = [
            {
                x: users,
                y: queries,
                type: 'bar',
                name: '查詢數量',
                marker: { color: 'rgba(55, 128, 191, 0.8)' },
                offsetgroup: 1
            },
            {
                x: users,
                y: tokens,
                type: 'bar',
                name: 'Token數量',
                marker: { color: 'rgba(255, 153, 51, 0.8)' },
                offsetgroup: 2,
                yaxis: 'y2'
            }
        ];
        
        const userDistLayout = {
            title: '各用戶查詢和Token統計',
            xaxis: { title: '用戶' },
            yaxis: { title: '查詢數量', side: 'left' },
            yaxis2: { title: 'Token數量', side: 'right', overlaying: 'y' },
            template: 'plotly_white',
            barmode: 'group',
            bargap: 0.15,
            bargroupgap: 0.1
        };
        
        Plotly.newPlot('user-distribution', userDistData, userDistLayout);
    }
    
    // 3. 用戶成功率比較
    if (queryResults.length > 0) {
        const userSuccessStats = {};
        
        // 統計每個用戶的成功率
        queryResults.forEach(result => {
            const userId = result.user_id;
            if (!userSuccessStats[userId]) {
                userSuccessStats[userId] = { total: 0, success: 0 };
            }
            userSuccessStats[userId].total += 1;
            if (result.success) {
                userSuccessStats[userId].success += 1;
            }
        });
        
        const users = Object.keys(userSuccessStats).map(id => `用戶 ${id}`);
        const successRates = Object.values(userSuccessStats).map(stats => 
            (stats.success / stats.total) * 100
        );
        
        const successRateData = [{
            x: users,
            y: successRates,
            type: 'bar',
            marker: {
                color: successRates.map(rate => 
                    rate === 100 ? '#28a745' : 
                    rate >= 80 ? '#ffc107' : '#dc3545'
                )
            },
            text: successRates.map(rate => `${rate.toFixed(1)}%`),
            textposition: 'auto'
        }];
        
        const successRateLayout = {
            title: '各用戶查詢成功率',
            xaxis: { title: '用戶' },
            yaxis: { title: '成功率 (%)', range: [0, 105] },
            template: 'plotly_white'
        };
        
        Plotly.newPlot('user-success-rate', successRateData, successRateLayout);
    }
}
