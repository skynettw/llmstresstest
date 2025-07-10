import psutil
import platform
import subprocess
import json
from datetime import datetime

def get_cpu_info():
    """獲取CPU資訊"""
    try:
        cpu_info = {
            'name': platform.processor(),
            'cores_physical': psutil.cpu_count(logical=False),
            'cores_logical': psutil.cpu_count(logical=True),
            'frequency_current': psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A',
            'frequency_max': psutil.cpu_freq().max if psutil.cpu_freq() else 'N/A',
            'usage_percent': psutil.cpu_percent(interval=1)
        }
        return cpu_info
    except Exception as e:
        return {'error': str(e)}

def get_memory_info():
    """獲取記憶體資訊"""
    try:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        memory_info = {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'usage_percent': memory.percent,
            'swap_total_gb': round(swap.total / (1024**3), 2),
            'swap_used_gb': round(swap.used / (1024**3), 2),
            'swap_percent': swap.percent
        }
        return memory_info
    except Exception as e:
        return {'error': str(e)}

def get_disk_info():
    """獲取磁碟資訊"""
    try:
        disk_info = []
        partitions = psutil.disk_partitions()

        for partition in partitions:
            try:
                partition_usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'file_system': partition.fstype,
                    'total_gb': round(partition_usage.total / (1024**3), 2),
                    'used_gb': round(partition_usage.used / (1024**3), 2),
                    'free_gb': round(partition_usage.free / (1024**3), 2),
                    'usage_percent': round((partition_usage.used / partition_usage.total) * 100, 2)
                })
            except (PermissionError, OSError):
                continue

        return disk_info
    except Exception as e:
        return {'error': str(e)}

def get_gpu_info():
    """獲取GPU資訊"""
    try:
        # 嘗試使用GPUtil獲取NVIDIA GPU資訊
        try:
            import GPUtil
            gpus = GPUtil.getGPUs()
            gpu_info = []
            
            for gpu in gpus:
                gpu_info.append({
                    'id': gpu.id,
                    'name': gpu.name,
                    'memory_total_mb': gpu.memoryTotal,
                    'memory_used_mb': gpu.memoryUsed,
                    'memory_free_mb': gpu.memoryFree,
                    'memory_usage_percent': round((gpu.memoryUsed / gpu.memoryTotal) * 100, 2),
                    'gpu_usage_percent': gpu.load * 100,
                    'temperature': gpu.temperature
                })
            
            if gpu_info:
                return gpu_info
        except ImportError:
            pass
        
        # 嘗試使用nvidia-smi命令
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu', '--format=csv,noheader,nounits'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                gpu_info = []
                for i, line in enumerate(lines):
                    parts = line.split(', ')
                    if len(parts) >= 6:
                        gpu_info.append({
                            'id': i,
                            'name': parts[0],
                            'memory_total_mb': int(parts[1]),
                            'memory_used_mb': int(parts[2]),
                            'memory_free_mb': int(parts[3]),
                            'memory_usage_percent': round((int(parts[2]) / int(parts[1])) * 100, 2),
                            'gpu_usage_percent': int(parts[4]),
                            'temperature': int(parts[5])
                        })
                return gpu_info
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return {'message': 'No GPU information available or GPU not detected'}
    
    except Exception as e:
        return {'error': str(e)}

def get_network_info():
    """獲取網路資訊"""
    try:
        network_info = {}
        net_io = psutil.net_io_counters()
        
        network_info = {
            'bytes_sent': net_io.bytes_sent,
            'bytes_recv': net_io.bytes_recv,
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv
        }
        
        return network_info
    except Exception as e:
        return {'error': str(e)}

def get_system_info():
    """獲取系統基本資訊"""
    try:
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        
        system_info = {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'boot_time': boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            'python_version': platform.python_version()
        }
        
        return system_info
    except Exception as e:
        return {'error': str(e)}

def get_hardware_info():
    """獲取完整的硬體資訊"""
    hardware_info = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'system': get_system_info(),
        'cpu': get_cpu_info(),
        'memory': get_memory_info(),
        'disk': get_disk_info(),
        'gpu': get_gpu_info(),
        'network': get_network_info()
    }
    
    return hardware_info

if __name__ == "__main__":
    # 測試硬體資訊獲取
    info = get_hardware_info()
    print(json.dumps(info, indent=2, ensure_ascii=False))
