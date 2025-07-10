import requests
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        """
        初始化Ollama客戶端
        
        Args:
            base_url: Ollama服務器的基礎URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 30
    
    def is_server_available(self) -> bool:
        """檢查Ollama服務器是否可用"""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_available_models(self) -> List[Dict]:
        """獲取可用的模型列表"""
        try:
            if not self.is_server_available():
                return []
            
            response = self.session.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            
            data = response.json()
            models = []
            
            for model in data.get('models', []):
                models.append({
                    'name': model.get('name', ''),
                    'size': model.get('size', 0),
                    'digest': model.get('digest', ''),
                    'modified_at': model.get('modified_at', ''),
                    'details': model.get('details', {})
                })
            
            return models
        
        except Exception as e:
            print(f"Error getting models: {e}")
            return []
    
    def generate_response(self, model: str, prompt: str, stream: bool = False) -> Dict:
        """
        生成回應
        
        Args:
            model: 模型名稱
            prompt: 輸入提示
            stream: 是否使用流式回應
            
        Returns:
            包含回應資訊的字典
        """
        start_time = time.time()
        
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            
            response = self.session.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=120
            )
            
            response.raise_for_status()
            
            if stream:
                # 處理流式回應
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode('utf-8'))
                            if 'response' in data:
                                full_response += data['response']
                            if data.get('done', False):
                                break
                        except json.JSONDecodeError:
                            continue
                
                end_time = time.time()
                return {
                    'success': True,
                    'response': full_response,
                    'model': model,
                    'prompt': prompt,
                    'response_time': end_time - start_time,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # 處理非流式回應
                data = response.json()
                end_time = time.time()
                
                return {
                    'success': True,
                    'response': data.get('response', ''),
                    'model': model,
                    'prompt': prompt,
                    'response_time': end_time - start_time,
                    'timestamp': datetime.now().isoformat(),
                    'context': data.get('context', []),
                    'done': data.get('done', False)
                }
        
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'Request timeout',
                'model': model,
                'prompt': prompt,
                'response_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
        
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'Request error: {str(e)}',
                'model': model,
                'prompt': prompt,
                'response_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'model': model,
                'prompt': prompt,
                'response_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    def test_model_performance(self, model: str, prompt: str, iterations: int = 1) -> List[Dict]:
        """
        測試模型性能
        
        Args:
            model: 模型名稱
            prompt: 測試提示
            iterations: 測試次數
            
        Returns:
            測試結果列表
        """
        results = []
        
        for i in range(iterations):
            print(f"Testing iteration {i+1}/{iterations} for model {model}")
            result = self.generate_response(model, prompt)
            result['iteration'] = i + 1
            results.append(result)
            
            # 在測試之間稍作停頓
            if i < iterations - 1:
                time.sleep(0.5)
        
        return results
    
    def get_model_info(self, model: str) -> Dict:
        """獲取特定模型的詳細資訊"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except Exception as e:
            return {'error': f'Failed to get model info: {str(e)}'}

if __name__ == "__main__":
    # 測試Ollama客戶端
    client = OllamaClient()
    
    print("Checking server availability...")
    if client.is_server_available():
        print("✓ Ollama server is available")
        
        print("\nGetting available models...")
        models = client.get_available_models()
        for model in models:
            print(f"  - {model['name']} ({model['size']} bytes)")
        
        if models:
            # 測試第一個模型
            test_model = models[0]['name']
            print(f"\nTesting model: {test_model}")
            result = client.generate_response(test_model, "Hello, how are you?")
            print(f"Response time: {result['response_time']:.2f}s")
            print(f"Success: {result['success']}")
    else:
        print("✗ Ollama server is not available")
