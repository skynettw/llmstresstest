#!/usr/bin/env python3
"""
簡單的Flask應用測試
"""

from flask import Flask, jsonify
from database import TestHistoryDatabase

app = Flask(__name__)

@app.route('/')
def index():
    return "Flask應用正在運行！"

@app.route('/test-db')
def test_db():
    try:
        db = TestHistoryDatabase()
        records = db.get_test_history(limit=1)
        
        if records:
            test_id = records[0]['test_id']
            detail = db.get_test_detail(test_id)
            
            return jsonify({
                'success': True,
                'message': '數據庫連接正常',
                'record_count': len(records),
                'sample_record': {
                    'test_id': detail.get('test_id'),
                    'test_name': detail.get('test_name'),
                    'test_type': detail.get('test_type'),
                    'has_hardware_info': bool(detail.get('hardware_info')),
                    'has_test_config': bool(detail.get('test_config'))
                }
            })
        else:
            return jsonify({
                'success': True,
                'message': '數據庫連接正常，但沒有記錄',
                'record_count': 0
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    print("🚀 啟動簡單Flask測試應用...")
    print("📍 訪問 http://127.0.0.1:5001 測試基本功能")
    print("📍 訪問 http://127.0.0.1:5001/test-db 測試數據庫")
    app.run(host='0.0.0.0', port=5001, debug=True)
