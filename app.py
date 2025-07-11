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
from multi_user_stress_test import MultiUserStressTestManager
from database import db

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ollama-stress-test-secret-key'

# 全局變量
stress_test_manager = StressTestManager()
multi_user_test_manager = MultiUserStressTestManager()
ollama_client = OllamaClient()

@app.route('/')
def index():
    """首頁 - 顯示硬體資訊和測試表單"""
    hardware_info = get_hardware_info()
    models = ollama_client.get_available_models()
    return render_template('index.html',
                         hardware_info=hardware_info,
                         models=models)

@app.route('/history')
def history():
    """歷史記錄頁面"""
    statistics = db.get_statistics()
    return render_template('history.html', statistics=statistics)

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

# ===== 測試二 - 多用戶並發測試 API =====

@app.route('/api/start_multi_user_test', methods=['POST'])
def start_multi_user_test():
    """開始多用戶並發測試"""
    test_config = request.json

    # 驗證測試配置
    required_fields = ['model', 'user_count', 'queries_per_user']
    for field in required_fields:
        if field not in test_config:
            return jsonify({'error': f'Missing required field: {field}'}), 400

    try:
        # 開始測試
        test_id = multi_user_test_manager.start_multi_user_test(test_config)

        return jsonify({
            'success': True,
            'test_id': test_id,
            'message': 'Multi-user test started successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stop_multi_user_test', methods=['POST'])
def stop_multi_user_test():
    """停止多用戶測試"""
    test_id = request.json.get('test_id')
    if not test_id:
        return jsonify({'error': 'Missing test_id'}), 400

    success = multi_user_test_manager.stop_test(test_id)

    return jsonify({
        'success': success,
        'message': 'Multi-user test stopped' if success else 'Test not found or already stopped'
    })

@app.route('/api/multi_user_test_status/<test_id>')
def multi_user_test_status(test_id):
    """獲取多用戶測試狀態"""
    status = multi_user_test_manager.get_test_status(test_id)
    if status:
        return jsonify(status)
    else:
        return jsonify({'error': 'Test not found'}), 404

@app.route('/api/multi_user_test_charts/<test_id>')
def multi_user_test_charts(test_id):
    """獲取多用戶測試圖表數據"""
    # 從多用戶測試管理器獲取測試結果
    test_info = multi_user_test_manager.active_tests.get(test_id)
    if not test_info:
        # 檢查是否在已完成的測試中
        test_result = multi_user_test_manager.test_results.get(test_id)
        if not test_result:
            return jsonify({'error': 'Test not found'}), 404

        # 生成多用戶測試圖表
        charts = generate_multi_user_test_charts(test_result)
        return jsonify(charts)

    # 如果測試還在進行中，檢查是否有結果數據
    if 'result' in test_info and test_info['result'].query_results:
        charts = generate_multi_user_test_charts(test_info['result'])
        return jsonify(charts)

    return jsonify({'error': 'No test results available'}), 404

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

def generate_multi_user_test_charts(test_result):
    """生成多用戶測試專用圖表"""
    charts = {}

    if not test_result or not test_result.query_results:
        return charts

    query_results = test_result.query_results
    successful_results = [r for r in query_results if r.success]
    failed_results = [r for r in query_results if not r.success]

    print(f"Debug Multi-user: Total results: {len(query_results)}, Successful: {len(successful_results)}, Failed: {len(failed_results)}")

    # 1. TPM趨勢圖 (測試二專用)
    if test_result.tpm_samples:
        timestamps = [sample['timestamp'].strftime('%H:%M:%S') for sample in test_result.tpm_samples]
        tpm_values = [sample['tokens_per_minute'] for sample in test_result.tpm_samples]

        fig_tpm = go.Figure()
        fig_tpm.add_trace(go.Scatter(
            x=timestamps,
            y=tpm_values,
            mode='lines+markers',
            name='TPM',
            line=dict(color='#28a745', width=3),
            marker=dict(size=6)
        ))

        fig_tpm.update_layout(
            title='TPM (每分鐘Token數) 趨勢',
            xaxis_title='時間',
            yaxis_title='TPM (tokens/分鐘)',
            template='plotly_white',
            hovermode='x unified'
        )

        charts['tpm_timeline'] = plotly.utils.PlotlyJSONEncoder().encode(fig_tpm)

    # 2. 用戶查詢分布圖
    if successful_results:
        user_stats = {}
        for result in successful_results:
            user_id = result.user_id
            if user_id not in user_stats:
                user_stats[user_id] = {'queries': 0, 'tokens': 0, 'avg_time': 0}
            user_stats[user_id]['queries'] += 1
            user_stats[user_id]['tokens'] += result.tokens_count

        # 計算平均響應時間
        for user_id in user_stats:
            user_results = [r for r in successful_results if r.user_id == user_id]
            if user_results:
                user_stats[user_id]['avg_time'] = sum(r.response_time for r in user_results) / len(user_results)

        users = [f'用戶 {uid}' for uid in user_stats.keys()]
        queries = [stats['queries'] for stats in user_stats.values()]
        tokens = [stats['tokens'] for stats in user_stats.values()]

        fig_users = go.Figure()

        # 查詢數量柱狀圖
        fig_users.add_trace(go.Bar(
            x=users,
            y=queries,
            name='查詢數量',
            marker_color='rgba(55, 128, 191, 0.8)',
            offsetgroup=1
        ))

        # Token數量柱狀圖
        fig_users.add_trace(go.Bar(
            x=users,
            y=tokens,
            name='Token數量',
            marker_color='rgba(255, 153, 51, 0.8)',
            offsetgroup=2
        ))

        fig_users.update_layout(
            title='各用戶查詢和Token統計',
            xaxis_title='用戶',
            yaxis_title='數量',
            template='plotly_white',
            barmode='group',
            bargap=0.15,
            bargroupgap=0.1
        )

        charts['user_distribution'] = plotly.utils.PlotlyJSONEncoder().encode(fig_users)

    # 3. 響應時間vs Token數量散點圖
    if successful_results:
        response_times = [r.response_time for r in successful_results]
        token_counts = [r.tokens_count for r in successful_results]
        user_colors = [r.user_id for r in successful_results]

        fig_scatter = go.Figure()
        fig_scatter.add_trace(go.Scatter(
            x=response_times,
            y=token_counts,
            mode='markers',
            marker=dict(
                size=8,
                color=user_colors,
                colorscale='viridis',
                showscale=True,
                colorbar=dict(title="用戶ID")
            ),
            text=[f'用戶 {r.user_id}' for r in successful_results],
            hovertemplate='<b>%{text}</b><br>響應時間: %{x:.2f}s<br>Token數: %{y}<extra></extra>'
        ))

        fig_scatter.update_layout(
            title='響應時間 vs Token數量',
            xaxis_title='響應時間 (秒)',
            yaxis_title='Token數量',
            template='plotly_white'
        )

        charts['response_vs_tokens'] = plotly.utils.PlotlyJSONEncoder().encode(fig_scatter)

    # 4. 多用戶成功率比較
    if query_results:
        user_success_stats = {}
        for result in query_results:
            user_id = result.user_id
            if user_id not in user_success_stats:
                user_success_stats[user_id] = {'total': 0, 'success': 0}
            user_success_stats[user_id]['total'] += 1
            if result.success:
                user_success_stats[user_id]['success'] += 1

        users = [f'用戶 {uid}' for uid in user_success_stats.keys()]
        success_rates = [(stats['success'] / stats['total']) * 100 for stats in user_success_stats.values()]

        fig_success = go.Figure()
        fig_success.add_trace(go.Bar(
            x=users,
            y=success_rates,
            marker_color=['#28a745' if rate == 100 else '#ffc107' if rate >= 80 else '#dc3545' for rate in success_rates],
            text=[f'{rate:.1f}%' for rate in success_rates],
            textposition='auto'
        ))

        fig_success.update_layout(
            title='各用戶查詢成功率',
            xaxis_title='用戶',
            yaxis_title='成功率 (%)',
            yaxis=dict(range=[0, 105]),
            template='plotly_white'
        )

        charts['user_success_rate'] = plotly.utils.PlotlyJSONEncoder().encode(fig_success)

    return charts

# ===== 歷史記錄管理 API =====

@app.route('/api/history')
def api_get_history():
    """獲取歷史記錄列表"""
    try:
        # 獲取查詢參數
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 12))
        test_type = request.args.get('test_type')
        model_name = request.args.get('model_name')

        # 計算偏移量
        offset = (page - 1) * limit

        # 轉換測試類型
        test_type_int = None
        if test_type:
            try:
                test_type_int = int(test_type)
            except ValueError:
                pass

        # 獲取歷史記錄
        records = db.get_test_history(
            limit=limit,
            offset=offset,
            test_type=test_type_int,
            model_name=model_name
        )

        # 獲取統計資訊
        statistics = db.get_statistics()

        # 計算分頁資訊
        total_records = statistics.get('total_records', 0)
        total_pages = (total_records + limit - 1) // limit

        return jsonify({
            'success': True,
            'records': records,
            'pagination': {
                'current_page': page,
                'total_pages': total_pages,
                'total_records': total_records,
                'limit': limit
            },
            'statistics': statistics
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/<test_id>')
def api_get_test_detail(test_id):
    """獲取特定測試的詳細資料"""
    try:
        record = db.get_test_detail(test_id)

        if record:
            return jsonify({
                'success': True,
                'record': record
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Test record not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/<test_id>', methods=['DELETE'])
def api_delete_test_record(test_id):
    """刪除測試記錄"""
    try:
        success = db.delete_test_record(test_id)

        if success:
            return jsonify({
                'success': True,
                'message': 'Test record deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Test record not found'
            }), 404

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/history/<test_id>/charts')
def api_get_test_charts(test_id):
    """獲取測試的圖表數據"""
    try:
        record = db.get_test_detail(test_id)

        if not record:
            return jsonify({
                'success': False,
                'error': 'Test record not found'
            }), 404

        # 根據測試類型生成圖表
        if record['test_type'] == 1:
            # 基礎壓力測試
            results = record['test_results'].get('results', [])
            statistics = record['test_statistics']
            charts = generate_test_charts(results, statistics)
        else:
            # 多用戶並發測試
            # 重構測試結果為MultiUserTestResult格式
            test_results = record['test_results']

            # 創建模擬的測試結果對象
            class MockTestResult:
                def __init__(self, data):
                    self.query_results = []
                    self.tpm_samples = []

                    # 轉換查詢結果
                    for result_data in data.get('query_results', []):
                        result_obj = type('QueryResult', (), {})()
                        for key, value in result_data.items():
                            setattr(result_obj, key, value)
                        self.query_results.append(result_obj)

                    # 轉換TPM樣本
                    for sample_data in data.get('tpm_samples', []):
                        sample = {
                            'timestamp': datetime.fromisoformat(sample_data['timestamp']),
                            'tokens_per_minute': sample_data['tokens_per_minute']
                        }
                        self.tpm_samples.append(sample)

            mock_result = MockTestResult(test_results)
            charts = generate_multi_user_test_charts(mock_result)

        return jsonify({
            'success': True,
            'charts': charts
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting Ollama Stress Test Server (Simple Version)...")
    # print("Hardware Information:")
    # hw_info = get_hardware_info()
    # for key, value in hw_info.items():
    #     if key != 'disk':  # 跳過有錯誤的磁碟資訊
    #         print(f"  {key}: {value}")

    app.run(debug=True, host='0.0.0.0', port=5000)
