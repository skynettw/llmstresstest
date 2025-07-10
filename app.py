from flask import Flask, render_template, request, jsonify
import threading
import time
import json
import plotly
import plotly.graph_objs as go
import plotly.utils
from datetime import datetime
from hardware_info import get_hardware_info
from ollama_client import OllamaClient
from stress_test_simple import StressTestManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ollama-stress-test-secret-key'

# 全局變量
stress_test_manager = StressTestManager()
ollama_client = OllamaClient()

@app.route('/')
def index():
    """首頁 - 顯示硬體資訊和測試表單"""
    hardware_info = get_hardware_info()
    models = ollama_client.get_available_models()
    return render_template('index_simple.html', 
                         hardware_info=hardware_info, 
                         models=models)

@app.route('/api/hardware')
def api_hardware():
    """API端點 - 獲取硬體資訊"""
    return jsonify(get_hardware_info())

@app.route('/api/models')
def api_models():
    """API端點 - 獲取可用模型列表"""
    return jsonify(ollama_client.get_available_models())

@app.route('/api/start_test', methods=['POST'])
def start_test():
    """開始壓力測試"""
    test_config = request.json
    
    # 驗證測試配置
    required_fields = ['model', 'concurrent_requests', 'total_requests', 'prompt']
    for field in required_fields:
        if field not in test_config:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # 開始測試
    test_id = stress_test_manager.start_test(test_config)
    
    return jsonify({
        'success': True,
        'test_id': test_id,
        'message': 'Test started successfully'
    })

@app.route('/api/stop_test', methods=['POST'])
def stop_test():
    """停止壓力測試"""
    test_id = request.json.get('test_id')
    if not test_id:
        return jsonify({'error': 'Missing test_id'}), 400
    
    success = stress_test_manager.stop_test(test_id)
    
    return jsonify({
        'success': success,
        'message': 'Test stopped' if success else 'Test not found or already stopped'
    })

@app.route('/api/test_status/<test_id>')
def test_status(test_id):
    """獲取測試狀態"""
    status = stress_test_manager.get_test_status(test_id)
    if status:
        return jsonify(status)
    else:
        return jsonify({'error': 'Test not found'}), 404

@app.route('/api/test_charts/<test_id>')
def test_charts(test_id):
    """獲取測試圖表數據"""
    status = stress_test_manager.get_test_status(test_id)
    if not status:
        return jsonify({'error': 'Test not found'}), 404

    # 獲取測試結果數據 - 優先使用完整結果，否則使用當前結果
    results = status.get('final_results', status.get('current_results', []))
    if not results:
        return jsonify({'error': 'No test results available'}), 404

    # 生成圖表
    charts = generate_test_charts(results, status.get('statistics', {}))
    return jsonify(charts)

def generate_test_charts(results, statistics):
    """生成測試結果圖表"""
    charts = {}

    if not results:
        return charts

    # 分離成功和失敗的結果
    successful_results = [r for r in results if r.get('success', False)]
    failed_results = [r for r in results if not r.get('success', False)]

    print(f"Debug: Total results: {len(results)}, Successful: {len(successful_results)}, Failed: {len(failed_results)}")

    # 1. 回應時間分布直方圖
    if successful_results:
        response_times = [r['response_time'] for r in successful_results]

        fig_histogram = go.Figure(data=[
            go.Histogram(
                x=response_times,
                nbinsx=20,
                name='回應時間分布',
                marker_color='rgba(55, 128, 191, 0.7)',
                marker_line=dict(color='rgba(55, 128, 191, 1.0)', width=1)
            )
        ])

        fig_histogram.update_layout(
            title='回應時間分布',
            xaxis_title='回應時間 (秒)',
            yaxis_title='請求數量',
            bargap=0.1,
            template='plotly_white'
        )

        charts['response_time_histogram'] = plotly.utils.PlotlyJSONEncoder().encode(fig_histogram)
    else:
        # 如果沒有成功結果，創建空的直方圖
        fig_histogram = go.Figure()
        fig_histogram.update_layout(
            title='回應時間分布 (無成功請求)',
            xaxis_title='回應時間 (秒)',
            yaxis_title='請求數量',
            template='plotly_white',
            annotations=[{
                'text': '沒有成功的請求數據',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False,
                'font': {'size': 16, 'color': 'gray'}
            }]
        )
        charts['response_time_histogram'] = plotly.utils.PlotlyJSONEncoder().encode(fig_histogram)

    # 2. 回應時間時間序列圖
    if successful_results:
        task_ids = [r.get('task_id', i) for i, r in enumerate(successful_results)]
        response_times = [r['response_time'] for r in successful_results]

        fig_timeline = go.Figure()

        fig_timeline.add_trace(go.Scatter(
            x=task_ids,
            y=response_times,
            mode='lines+markers',
            name='回應時間',
            line=dict(color='rgb(55, 128, 191)', width=2),
            marker=dict(size=6)
        ))

        # 添加平均線
        if statistics.get('response_time_stats', {}).get('mean'):
            mean_time = statistics['response_time_stats']['mean']
            fig_timeline.add_hline(
                y=mean_time,
                line_dash="dash",
                line_color="red",
                annotation_text=f"平均值: {mean_time:.2f}s"
            )

        fig_timeline.update_layout(
            title='回應時間趨勢',
            xaxis_title='請求序號',
            yaxis_title='回應時間 (秒)',
            template='plotly_white'
        )

        charts['response_time_timeline'] = plotly.utils.PlotlyJSONEncoder().encode(fig_timeline)
    else:
        # 如果沒有成功結果，創建空的時間序列圖
        fig_timeline = go.Figure()
        fig_timeline.update_layout(
            title='回應時間趨勢 (無成功請求)',
            xaxis_title='請求序號',
            yaxis_title='回應時間 (秒)',
            template='plotly_white',
            annotations=[{
                'text': '沒有成功的請求數據',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False,
                'font': {'size': 16, 'color': 'gray'}
            }]
        )
        charts['response_time_timeline'] = plotly.utils.PlotlyJSONEncoder().encode(fig_timeline)

    # 3. 成功率餅圖
    if results:
        success_count = len(successful_results)
        failed_count = len(failed_results)

        fig_pie = go.Figure(data=[
            go.Pie(
                labels=['成功', '失敗'],
                values=[success_count, failed_count],
                hole=0.3,
                marker_colors=['#28a745', '#dc3545']
            )
        ])

        fig_pie.update_layout(
            title='請求成功率',
            template='plotly_white'
        )

        charts['success_rate_pie'] = plotly.utils.PlotlyJSONEncoder().encode(fig_pie)

    # 4. 回應時間統計箱線圖
    if successful_results:
        response_times = [r['response_time'] for r in successful_results]

        fig_box = go.Figure()

        fig_box.add_trace(go.Box(
            y=response_times,
            name='回應時間',
            marker_color='rgba(55, 128, 191, 0.7)',
            boxpoints='outliers'
        ))

        fig_box.update_layout(
            title='回應時間統計分析',
            yaxis_title='回應時間 (秒)',
            template='plotly_white'
        )

        charts['response_time_box'] = plotly.utils.PlotlyJSONEncoder().encode(fig_box)
    else:
        # 如果沒有成功結果，創建空的箱線圖
        fig_box = go.Figure()
        fig_box.update_layout(
            title='回應時間統計分析 (無成功請求)',
            yaxis_title='回應時間 (秒)',
            template='plotly_white',
            annotations=[{
                'text': '沒有成功的請求數據',
                'xref': 'paper',
                'yref': 'paper',
                'x': 0.5,
                'y': 0.5,
                'showarrow': False,
                'font': {'size': 16, 'color': 'gray'}
            }]
        )
        charts['response_time_box'] = plotly.utils.PlotlyJSONEncoder().encode(fig_box)

    return charts

if __name__ == '__main__':
    print("Starting Ollama Stress Test Server (Simple Version)...")
    # print("Hardware Information:")
    # hw_info = get_hardware_info()
    # for key, value in hw_info.items():
    #     if key != 'disk':  # 跳過有錯誤的磁碟資訊
    #         print(f"  {key}: {value}")

    app.run(debug=True, host='0.0.0.0', port=5000)
