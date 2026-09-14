"""
授权服务API模块
"""

import json
import uuid
import socket
import platform
from typing import Dict, Optional
from utils.logger import global_log

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class LicenseAPI:
    """授权API类"""
    
    def __init__(self, base_url: str = 'http://121.199.66.60:8788'):
        self.base_url = base_url
        self.log = global_log
        self.timeout = 10
        self.app_id = 'trae-laqu'
        self.device_fingerprint = self._generate_fingerprint()
    
    def _generate_fingerprint(self) -> str:
        """生成设备指纹"""
        components = [
            socket.gethostname(),
            platform.system(),
            platform.release(),
            str(uuid.getnode()),
        ]
        fingerprint_str = '-'.join(components)
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, fingerprint_str))
    
    def _get_system_info(self) -> Dict:
        """获取系统信息"""
        return {
            'hostname': socket.gethostname(),
            'platform': platform.system(),
            'platform_version': platform.release(),
            'architecture': platform.machine(),
            'processor': platform.processor(),
        }
    
    def _make_request(self, endpoint: str, method: str = 'POST', 
                     data: Optional[Dict] = None) -> Optional[Dict]:
        """发送HTTP请求"""
        if not HAS_REQUESTS:
            self.log.error("requests库未安装，无法发送HTTP请求")
            return None
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'POST':
                response = requests.post(
                    url, 
                    json=data, 
                    timeout=self.timeout,
                    headers={'Content-Type': 'application/json'}
                )
            else:
                response = requests.get(
                    url, 
                    params=data,
                    timeout=self.timeout
                )
            
            response.raise_for_status()
            
            try:
                return response.json()
            except:
                return {'raw': response.text}
                
        except requests.exceptions.Timeout:
            self.log.error(f"请求超时: {url}")
            return None
        except requests.exceptions.ConnectionError:
            self.log.error(f"连接失败: {url}")
            return None
        except requests.exceptions.HTTPError as e:
            self.log.error(f"HTTP错误: {e}")
            return None
        except Exception as e:
            self.log.error(f"请求失败: {e}")
            return None
    
    def activate_license(self, license_code: str) -> Dict:
        """激活授权"""
        self.log.info(f"正在激活授权码: {license_code[:8]}...")
        
        data = {
            'license_code': license_code,
            'device_fingerprint': self.device_fingerprint,
            'app_id': self.app_id,
            'app_version': '1.0.0',
            'system_info': self._get_system_info(),
        }
        
        result = self._make_request('/api/client/activate', 'POST', data)
        
        if result:
            self.log.success("授权激活成功")
            return result
        else:
            self.log.error("授权激活失败")
            return {'success': False, 'error': '激活失败'}
    
    def pull_accounts(self, session_token: Optional[str] = None) -> Dict:
        """获取账户列表"""
        self.log.info("正在获取账户列表...")
        
        data = {
            'device_fingerprint': self.device_fingerprint,
            'app_id': self.app_id,
        }
        
        if session_token:
            data['session_token'] = session_token
        
        result = self._make_request('/api/client/pull-accounts', 'POST', data)
        
        if result:
            self.log.success("获取账户列表成功")
            return result
        else:
            self.log.error("获取账户列表失败")
            return {'success': False, 'error': '获取失败'}
    
    def check_license_status(self) -> Dict:
        """检查授权状态"""
        self.log.info("正在检查授权状态...")
        
        data = {
            'device_fingerprint': self.device_fingerprint,
            'app_id': self.app_id,
        }
        
        result = self._make_request('/api/client/status', 'POST', data)
        
        if result:
            return result
        else:
            return {'success': False, 'error': '检查失败'}
    
    def deactivate_license(self) -> Dict:
        """注销授权"""
        self.log.info("正在注销授权...")
        
        data = {
            'device_fingerprint': self.device_fingerprint,
            'app_id': self.app_id,
        }
        
        result = self._make_request('/api/client/deactivate', 'POST', data)
        
        if result:
            self.log.success("授权注销成功")
            return result
        else:
            self.log.error("授权注销失败")
            return {'success': False, 'error': '注销失败'}
    
    def get_device_id(self) -> str:
        """获取设备ID"""
        return self.device_fingerprint
    
    def test_connection(self) -> bool:
        """测试连接"""
        if not HAS_REQUESTS:
            return False
        
        try:
            response = requests.get(
                self.base_url, 
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
