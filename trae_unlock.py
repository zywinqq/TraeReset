#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""trae助手reset工具 - Trae IDE 设备限制重置工具
AI虎哥重置版 | https://3se.cc | v20260914
"""

import json, os, platform, shutil, subprocess, uuid, secrets, socket
import traceback, sys, ctypes, threading, time, re, base64, hashlib, hmac
from datetime import datetime, date
from typing import Dict, Optional, Tuple, List
from urllib import request as urlreq
from urllib.error import URLError, HTTPError
import json as _json

if platform.system() == "Windows":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

import customtkinter as ctk
from tkinter import messagebox, filedialog
try:
    from PIL import Image, ImageDraw, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ─── 常量 ─────────────────────────────────────────────────────

VERSION = "20260914"
APP_NAME = "trae助手reset工具"
APP_TITLE = f"trae助手reset工具 v{VERSION}"
APP_AUTHOR = "AI虎哥重置版"
APP_WEBSITE = "https://3se.cc"

# 卡密 API 服务地址
API_BASE = "https://trae.winvvv.com/api"
API_CHECK_CARD = API_BASE + "/check_card.php"
API_HEARTBEAT = API_BASE + "/check_heartbeat.php"

# 心跳间隔（秒）
HEARTBEAT_INTERVAL = 600  # 10 分钟
HEARTBEAT_FAIL_LIMIT = 3  # 连续失败上限（仅警告，不强制下线）
OFFLINE_GRACE_HOURS = 24  # 离线宽限期（小时）

# ─── 色彩系统（参考图片的渐变卡片配色） ───────────────────────

BG          = "#f3f4f6"   # 浅灰背景
BG_CARD     = "#ffffff"   # 白卡片
BG_HEAD     = "#1e293b"   # 深色顶部栏
BG_LOG      = "#f8fafc"
BG_INPUT    = "#f1f5f9"

FG          = "#1f2937"   # 主文字
FG_DIM      = "#6b7280"   # 次文字
FG_BODY     = "#475569"
FG_LINK     = "#2563eb"
FG_WHITE    = "#ffffff"

# 卡片配色（参考图片的蓝/紫/橙/绿）
CARD_BLUE_S, CARD_BLUE_E   = "#2563eb", "#3b82f6"
CARD_PURPLE_S, CARD_PURPLE_E = "#7c3aed", "#a855f7"
CARD_ORANGE_S, CARD_ORANGE_E = "#ea580c", "#f97316"
CARD_GREEN_S, CARD_GREEN_E  = "#059669", "#10b981"

# 主操作按钮紫色渐变
BTN_PRIMARY_S, BTN_PRIMARY_E = "#4f46e5", "#6366f1"

# 警示条
WARN_BG     = "#fef3c7"
WARN_BORDER = "#f59e0b"
WARN_TEXT   = "#92400e"

# 徽章
BADGE_OK_BG   = "#dcfce7"
BADGE_OK_FG   = "#166534"
BADGE_WARN_BG = "#fef3c7"
BADGE_WARN_FG = "#92400e"
BADGE_INFO_BG = "#dbeafe"
BADGE_INFO_FG = "#1e40af"
BADGE_ERR_BG  = "#fee2e2"
BADGE_ERR_FG  = "#991b1b"

# 通用
RED       = "#dc2626"
RED_H     = "#b91c1c"
AMBER     = "#d97706"
AMBER_H   = "#b45309"
GREEN     = "#16a34a"
GHOST     = "#e5e8f0"
GHOST_H   = "#cbd5e1"
BORDER    = "#e5e7eb"
BLUE      = "#2563eb"
BLUE_H    = "#1d4ed8"

# ─── 平台 & 路径 ──────────────────────────────────────────────

IS_WIN = platform.system() == "Windows"
IS_MAC = platform.system() == "Darwin"

if IS_WIN:
    DATA_DIR_DEFAULT = os.path.join(os.environ.get("APPDATA", ""), "Trae")
    DIR_HINT = "%APPDATA%\\Trae"
    FONT_UI = "Microsoft YaHei UI"
    FONT_MONO = "Consolas"
    REG_PATH = r"HKLM\SOFTWARE\Microsoft\Cryptography"
    REG_VAL = "MachineGuid"
elif IS_MAC:
    DATA_DIR_DEFAULT = os.path.join(
        os.path.expanduser("~"), "Library", "Application Support", "Trae")
    DIR_HINT = "~/Library/Application Support/Trae"
    FONT_UI = "PingFang SC"
    FONT_MONO = "Menlo"
else:
    DATA_DIR_DEFAULT = os.path.join(os.path.expanduser("~"), ".config", "Trae")
    DIR_HINT = "~/.config/Trae"
    FONT_UI = "Noto Sans CJK SC"
    FONT_MONO = "Noto Sans Mono"

STORAGE_REL = os.path.join("User", "globalStorage", "storage.json")
AUTH_KEY_PATTERNS = [
    "iCubeAuthInfo://", "iCubeServerData://", "-entitlement-notified"]
COOKIE_PATHS = [
    os.path.join("Network", "Cookies"),
    os.path.join("Network", "Cookies-journal"),
    os.path.join("Partitions", "icube-web-crawler-shared-session-v1.0",
                 "Network", "Cookies"),
    os.path.join("Partitions", "icube-web-crawler-shared-session-v1.0",
                 "Network", "Cookies-journal"),
    os.path.join("Partitions", "trae-webview", "Network", "Cookies"),
    os.path.join("Partitions", "trae-webview", "Network", "Cookies-journal"),
]

GUIDE_TIPS = [
    "使用前请先关闭 Trae，否则修改不生效或文件被锁定",
    "提示「设备数量已达上限」? 点「一键重置」即可",
    "重置后重新打开 Trae，用新账号登录即可",
    "所有操作会自动备份原文件（.bak），可手动恢复",
    "如检测不到目录，点「自定义目录」手动选择",
    "重置完成后建议禁用 Trae 自动更新，避免机器码被回写",
]

# ─── 设备指纹 ──────────────────────────────────────────────────

class DeviceFingerprint:
    """生成稳定设备指纹（基于 hostname + platform + mac 地址）"""

    _cached: Optional[str] = None

    @classmethod
    def generate(cls) -> str:
        if cls._cached:
            return cls._cached
        try:
            mac = uuid.getnode()
            components = [
                socket.gethostname(),
                platform.system(),
                platform.release(),
                str(mac),
            ]
            fp_str = "-".join(components)
            cls._cached = str(uuid.uuid5(uuid.NAMESPACE_DNS, fp_str))
        except Exception:
            cls._cached = str(uuid.uuid4())
        return cls._cached

    @classmethod
    def short(cls) -> str:
        return cls.generate()[:12]

# ─── 卡密 API 客户端 ──────────────────────────────────────────

class LicenseAPIError(Exception):
    pass


class LicenseClient:
    """卡密验证客户端 - POST form-urlencoded 到 PHP 后端"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.machine_id = DeviceFingerprint.generate()

    def _post(self, url: str, data: Dict) -> Dict:
        """使用 urllib 发送 POST 请求，返回 JSON 字典"""
        body = "&".join(
            f"{k}={urlreq.quote(str(v), safe='')}" for k, v in data.items()
        ).encode("utf-8")
        req = urlreq.Request(
            url, data=body, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded",
                     "User-Agent": f"TraeReset/{VERSION}"}
        )
        try:
            with urlreq.urlopen(req, timeout=self.timeout) as resp:
                raw = resp.read().decode("utf-8")
        except HTTPError as e:
            # 后端可能返回 JSON 或 HTML（PHP 错误页）
            body_bytes = b""
            try:
                body_bytes = e.read()
            except Exception:
                pass
            body_text = body_bytes.decode("utf-8", errors="ignore") if body_bytes else ""
            # 先尝试解析为 JSON
            try:
                return _json.loads(body_text)
            except Exception:
                pass
            # 提取 HTML 中的关键错误信息
            hint = self._extract_error_hint(body_text)
            if hint:
                raise LicenseAPIError(f"HTTP {e.code}: {hint}")
            raise LicenseAPIError(f"HTTP {e.code}: {e.reason}")
        except URLError as e:
            raise LicenseAPIError(f"网络错误: {e.reason}")
        except Exception as e:
            raise LicenseAPIError(f"请求失败: {e}")
        try:
            return _json.loads(raw)
        except Exception:
            # 提取 HTML 中的错误关键词
            hint = self._extract_error_hint(raw)
            if hint:
                raise LicenseAPIError(f"响应解析失败: {hint}")
            raise LicenseAPIError(f"响应解析失败: {raw[:200]}")

    @staticmethod
    def _extract_error_hint(html: str) -> str:
        """从 HTML 错误页面中提取关键错误信息"""
        if not html or len(html) > 5000:
            return ""
        import re as _re
        # PHP / Apache 常见错误关键词
        keywords = [
            "server error", "internal server error", "fatal error",
            "parse error", "syntax error", "mysql", "mysqli",
            "connection refused", "access denied", "no such file",
            "database", "sql", "pdo", "undefined", "warning",
        ]
        text_lower = html.lower()
        found = []
        for kw in keywords:
            if kw in text_lower and kw not in found:
                # 找到关键词上下文
                idx = text_lower.find(kw)
                start = max(0, idx - 30)
                end = min(len(html), idx + len(kw) + 50)
                snippet = html[start:end].replace("\n", " ").strip()
                # 去掉 HTML 标签
                snippet = _re.sub(r'<[^>]+>', '', snippet).strip()
                if snippet and len(snippet) > 3:
                    found.append(snippet[:100])
        return " | ".join(found[:2]) if found else ""

    def check_card(self, card_key: str) -> Dict:
        """卡密验证 + 设备绑定"""
        return self._post(API_CHECK_CARD, {
            "card_key": card_key,
            "machine_id": self.machine_id,
        })

    def heartbeat(self, card_key: str) -> Dict:
        """心跳保活"""
        return self._post(API_HEARTBEAT, {
            "card_key": card_key,
            "machine_id": self.machine_id,
        })


# ─── 本地缓存（Fernet 加密） ──────────────────────────────────

class LicenseStore:
    """加密本地缓存 + 24h 离线宽限"""

    def __init__(self):
        self.base_dir = self._get_base_dir()
        os.makedirs(self.base_dir, exist_ok=True)
        self.license_file = os.path.join(self.base_dir, "license.dat")
        self.config_file = os.path.join(self.base_dir, "config.json")
        self._fernet = self._make_fernet()

    def _get_base_dir(self) -> str:
        if IS_WIN:
            base = os.path.join(
                os.environ.get("APPDATA", os.path.expanduser("~")), "TraeUnlock")
        elif IS_MAC:
            base = os.path.join(
                os.path.expanduser("~"), "Library",
                "Application Support", "TraeUnlock")
        else:
            base = os.path.join(os.path.expanduser("~"), ".config", "TraeUnlock")
        return base

    def _make_fernet(self):
        """从 hostname + mac 派生密钥（换机自动失效）"""
        from cryptography.fernet import Fernet
        seed = f"{socket.gethostname()}|{uuid.getnode()}|trae-reset-v1"
        key = base64.urlsafe_b64encode(
            hashlib.pbkdf2_hmac("sha256", seed.encode(), b"trae-salt-v1", 100_000)
        )
        return Fernet(key)

    def save_license(self, data: Dict) -> bool:
        try:
            payload = {
                "card_key": data.get("card_key", ""),
                "card_type": data.get("card_type", ""),
                "expire_date": data.get("expire_date", ""),
                "bound_devices": data.get("bound_devices", 0),
                "max_devices": data.get("max_devices", 0),
                "machine_id": DeviceFingerprint.generate(),
                "last_check": int(time.time()),
            }
            enc = self._fernet.encrypt(_json.dumps(payload).encode())
            with open(self.license_file, "wb") as f:
                f.write(enc)
            return True
        except Exception as e:
            print(f"[LicenseStore] save_license 失败: {e}")
            return False

    def load_license(self) -> Optional[Dict]:
        if not os.path.isfile(self.license_file):
            return None
        try:
            with open(self.license_file, "rb") as f:
                enc = f.read()
            data = _json.loads(self._fernet.decrypt(enc))
            # 设备指纹不匹配则拒绝
            if data.get("machine_id") != DeviceFingerprint.generate():
                return None
            return data
        except Exception as e:
            print(f"[LicenseStore] load_license 失败: {e}")
            return None

    def is_offline_grace_valid(self) -> bool:
        """检查是否在 24h 离线宽限期内"""
        data = self.load_license()
        if not data:
            return False
        last_check = data.get("last_check", 0)
        return (int(time.time()) - last_check) < OFFLINE_GRACE_HOURS * 3600

    def clear(self):
        try:
            if os.path.isfile(self.license_file):
                os.remove(self.license_file)
        except Exception:
            pass

    def get_config(self, key: str, default=None):
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                return _json.load(f).get(key, default)
        except Exception:
            return default

    def set_config(self, key: str, value):
        try:
            cfg = {}
            if os.path.isfile(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    cfg = _json.load(f)
            cfg[key] = value
            with open(self.config_file, "w", encoding="utf-8") as f:
                _json.dump(cfg, f, indent=2, ensure_ascii=False)
        except Exception:
            pass


# ─── 心跳线程 ──────────────────────────────────────────────────

class HeartbeatThread(threading.Thread):
    """后台心跳保活"""

    def __init__(self, app: "MainApp", card_key: str):
        super().__init__(daemon=True, name="heartbeat")
        self.app = app
        self.card_key = card_key
        self.client = LicenseClient()
        self.stop_flag = threading.Event()
        self.fail_count = 0

    def run(self):
        while not self.stop_flag.is_set():
            try:
                resp = self.client.heartbeat(self.card_key)
                if resp.get("success"):
                    self.fail_count = 0
                    self.app.after(0, lambda: self.app.on_heartbeat_ok(resp))
                else:
                    self.fail_count += 1
                    action = resp.get("action", "")
                    self.app.after(0, lambda: self.app.on_heartbeat_fail(resp, action))
                    if action == "exit":
                        self.app.after(0, self.app.force_logout)
                        return
            except LicenseAPIError as e:
                self.fail_count += 1
                if self.fail_count >= HEARTBEAT_FAIL_LIMIT:
                    self.app.after(0, lambda: self.app.on_heartbeat_network_error(str(e)))
            except Exception as e:
                print(f"[Heartbeat] {e}")
            self.stop_flag.wait(HEARTBEAT_INTERVAL)

    def stop(self):
        self.stop_flag.set()


# ─── 管理员权限 ────────────────────────────────────────────────

def is_admin() -> bool:
    if IS_WIN:
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    return os.geteuid() == 0 if hasattr(os, "geteuid") else True


def restart_as_admin() -> bool:
    if IS_WIN:
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable,
                " ".join([f'"{a}"' for a in sys.argv]), None, 1)
            return True
        except Exception:
            return False
    return False


# ─── 核心重置逻辑 ──────────────────────────────────────────────

def is_valid_trae_dir(path: str) -> bool:
    return (os.path.isfile(os.path.join(path, "machineid"))
            or os.path.isfile(os.path.join(path, STORAGE_REL)))


def auto_detect_trae_dirs() -> List[str]:
    """自动检测可能的 Trae 数据目录"""
    candidates = []
    if IS_WIN:
        env_keys = ["APPDATA", "LOCALAPPDATA", "USERPROFILE"]
        for key in env_keys:
            base = os.environ.get(key)
            if not base:
                continue
            for sub in ["Trae", os.path.join("Programs", "Trae"),
                        os.path.join("AppData", "Roaming", "Trae")]:
                p = os.path.join(base, sub)
                if os.path.isdir(p) and is_valid_trae_dir(p):
                    if p not in candidates:
                        candidates.append(p)
    elif IS_MAC:
        base = os.path.expanduser("~")
        for sub in [os.path.join("Library", "Application Support", "Trae")]:
            p = os.path.join(base, sub)
            if os.path.isdir(p) and is_valid_trae_dir(p):
                candidates.append(p)
    else:
        base = os.path.expanduser("~")
        for sub in [os.path.join(".config", "Trae")]:
            p = os.path.join(base, sub)
            if os.path.isdir(p) and is_valid_trae_dir(p):
                candidates.append(p)
    # 始终包含默认目录作为兜底
    if os.path.isdir(DATA_DIR_DEFAULT) and DATA_DIR_DEFAULT not in candidates:
        candidates.append(DATA_DIR_DEFAULT)
    return candidates


def is_trae_running() -> bool:
    try:
        if IS_WIN:
            out = subprocess.check_output(
                ["tasklist"], creationflags=0x08000000, text=True, timeout=10)
            return "trae.exe" in out.lower()
        else:
            out = subprocess.check_output(["ps", "aux"], text=True, timeout=10)
            return "/trae" in out.lower() or "/Trae" in out
    except Exception:
        return False


def kill_trae_process() -> Tuple[bool, str]:
    """结束 Trae 进程"""
    try:
        if IS_WIN:
            subprocess.run(["taskkill", "/F", "/IM", "trae.exe"],
                           capture_output=True, timeout=10)
            time.sleep(0.5)
            return (not is_trae_running(), "taskkill 完成")
        else:
            subprocess.run(["pkill", "-f", "[Tt]rae"],
                           capture_output=True, timeout=10)
            time.sleep(0.5)
            return (not is_trae_running(), "pkill 完成")
    except Exception as e:
        return False, f"结束失败: {e}"


def read_storage(data_dir: str) -> Optional[Dict]:
    path = os.path.join(data_dir, STORAGE_REL)
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _json.load(f)
    except (_json.JSONDecodeError, OSError):
        return None


def write_storage(data_dir: str, data: Dict) -> bool:
    path = os.path.join(data_dir, STORAGE_REL)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        if os.path.isfile(path):
            shutil.copy2(path, path + ".bak")
        with open(path, "w", encoding="utf-8") as f:
            _json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"write_storage 失败: {e}")
        return False


def read_machineid(data_dir: str) -> Optional[str]:
    path = os.path.join(data_dir, "machineid")
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def get_status(data_dir: str) -> Dict:
    info = {"machine_id": read_machineid(data_dir) or "未找到",
            "dev_device_id": "未找到", "accounts": []}
    storage = read_storage(data_dir)
    if not storage:
        return info
    info["dev_device_id"] = storage.get("telemetry.devDeviceId", "未找到")
    for key, val in storage.items():
        if not key.startswith("iCubeAuthInfo://icube.cloudide"):
            continue
        try:
            auth = _json.loads(val) if isinstance(val, str) else val
            acct = auth.get("account", {})
            name = acct.get("username", "未知")
            ct = acct.get("email", "") or acct.get("nonPlainTextMobile", "")
            info["accounts"].append(f"{name} ({ct})" if ct else name)
        except Exception:
            info["accounts"].append("(解析失败)")
    return info


def clear_accounts(data_dir: str) -> Tuple[List[str], int]:
    logs, removed = [], 0
    storage = read_storage(data_dir)
    if storage:
        keys = [k for k in list(storage.keys())
                if any(p in k for p in AUTH_KEY_PATTERNS)]
        for k in keys:
            del storage[k]
            logs.append(f"  删除: {k}")
            removed += 1
        if keys:
            if not write_storage(data_dir, storage):
                logs.append("  storage.json 写入失败")
        else:
            logs.append("  未找到 storage.json")
    for rel in COOKIE_PATHS:
        full = os.path.join(data_dir, rel)
        if os.path.isfile(full):
            try:
                os.remove(full)
                logs.append(f"  删除: {rel}")
                removed += 1
            except OSError as e:
                logs.append(f"  失败 {rel}: {e}")
    if removed == 0:
        logs.append("  没有需要清除的内容")
    return logs, removed


def reset_device_id(data_dir: str, backup_first: bool = True) -> Tuple[List[str], bool]:
    """重置设备 ID（machineid + storage.json 中所有相关字段 + .updaterId）
    返回 (logs, success)。失败时自动回滚备份。
    """
    logs = []
    backups = {}  # 记录已写过的文件，便于回滚

    try:
        # 1. machineid
        mid_path = os.path.join(data_dir, "machineid")
        os.makedirs(os.path.dirname(mid_path) or ".", exist_ok=True)
        new_mid = str(uuid.uuid4())
        if os.path.isfile(mid_path):
            shutil.copy2(mid_path, mid_path + ".bak")
            backups[mid_path] = mid_path + ".bak"
        with open(mid_path, "w", encoding="utf-8") as f:
            f.write(new_mid)
        logs.append(f"  machineid: {new_mid}")

        # 2. storage.json
        storage = read_storage(data_dir)
        if storage:
            # 先备份原 storage
            st_path = os.path.join(data_dir, STORAGE_REL)
            if os.path.isfile(st_path):
                shutil.copy2(st_path, st_path + ".bak")
                backups[st_path] = st_path + ".bak"
            nt = secrets.token_hex(32)
            ns = "{" + str(uuid.uuid4()).upper() + "}"
            nd = str(uuid.uuid4())
            storage["telemetry.machineId"] = nt
            storage["telemetry.sqmId"] = ns
            storage["telemetry.devDeviceId"] = nd
            storage["has_device_id_updated_to_aha"] = "false"
            if write_storage(data_dir, storage):
                logs.append(f"  telemetry.machineId: {nt[:20]}...")
                logs.append(f"  telemetry.devDeviceId: {nd}")
                logs.append(f"  telemetry.sqmId: {ns}")
            else:
                raise RuntimeError("storage.json 写入失败")
        else:
            logs.append("  未找到 storage.json，仅更新 machineid")

        # 3. .updaterId（若存在）
        upd_path = os.path.join(data_dir, ".updaterId")
        if os.path.isfile(upd_path):
            shutil.copy2(upd_path, upd_path + ".bak")
            backups[upd_path] = upd_path + ".bak"
            new_upd = str(uuid.uuid4())
            with open(upd_path, "w", encoding="utf-8") as f:
                f.write(new_upd)
            logs.append(f"  .updaterId: {new_upd}")

        # 4. Windows 注册表 MachineGuid（需管理员）
        if IS_WIN and is_admin():
            try:
                import winreg
                with winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography",
                    0, winreg.KEY_READ | winreg.KEY_WRITE
                ) as key:
                    try:
                        old_val, _ = winreg.QueryValueEx(key, REG_VAL)
                        # 备份到文件
                        bak_file = os.path.join(data_dir, "MachineGuid.bak")
                        with open(bak_file, "w", encoding="utf-8") as f:
                            f.write(str(old_val))
                        new_guid = str(uuid.uuid4())
                        winreg.SetValueEx(key, REG_VAL, 0, winreg.REG_SZ, new_guid)
                        logs.append(f"  注册表 MachineGuid: {new_guid}")
                    except FileNotFoundError:
                        logs.append("  注册表无 MachineGuid，跳过")
            except PermissionError:
                logs.append("  注册表需管理员权限，跳过")
            except Exception as e:
                logs.append(f"  注册表修改失败: {e}")
        elif IS_WIN and not is_admin():
            logs.append("  注册表需管理员权限，跳过（非管理员）")

        return logs, True

    except Exception as e:
        # 回滚已写文件
        for orig, bak in backups.items():
            try:
                if os.path.isfile(bak):
                    shutil.copy2(bak, orig)
                    logs.append(f"  已回滚: {os.path.basename(orig)}")
            except Exception:
                pass
        logs.append(f"  ❌ 重置失败，已回滚: {e}")
        return logs, False


def verify_write(data_dir: str, expected_mid: str) -> Tuple[bool, str]:
    """写入后验证"""
    actual = read_machineid(data_dir)
    if actual != expected_mid:
        return False, f"machineid 验证失败: 期望 {expected_mid[:12]}... 实际 {(actual or '空')[:12]}..."
    st = read_storage(data_dir)
    if st and st.get("telemetry.devDeviceId", "") == "":
        return False, "storage.json 中 devDeviceId 为空"
    return True, "文件验证通过"


def restore_backup(data_dir: str) -> Tuple[List[str], int]:
    logs, restored = [], 0
    targets = [
        ("machineid",     os.path.join(data_dir, "machineid")),
        ("storage.json",  os.path.join(data_dir, STORAGE_REL)),
        (".updaterId",    os.path.join(data_dir, ".updaterId")),
        ("MachineGuid",   os.path.join(data_dir, "MachineGuid.bak")),
    ]
    for name, dst in targets:
        bak = dst + ".bak"
        # MachineGuid 的备份文件就是 dst 本身（仅恢复到注册表）
        if name == "MachineGuid":
            if os.path.isfile(bak):
                try:
                    if IS_WIN and is_admin():
                        import winreg
                        with open(bak, "r", encoding="utf-8") as f:
                            old_guid = f.read().strip()
                        with winreg.OpenKey(
                            winreg.HKEY_LOCAL_MACHINE,
                            r"SOFTWARE\Microsoft\Cryptography",
                            0, winreg.KEY_WRITE
                        ) as key:
                            winreg.SetValueEx(key, REG_VAL, 0, winreg.REG_SZ, old_guid)
                        logs.append("  已恢复: 注册表 MachineGuid")
                        restored += 1
                    else:
                        logs.append("  MachineGuid 恢复需管理员权限")
                except Exception as e:
                    logs.append(f"  MachineGuid 恢复失败: {e}")
            continue
        if os.path.isfile(bak):
            try:
                shutil.copy2(bak, dst)
                logs.append(f"  已恢复: {name}")
                restored += 1
            except Exception as e:
                logs.append(f"  恢复 {name} 失败: {e}")
        else:
            logs.append(f"  未找到 {name}.bak")
    if restored == 0:
        logs.append("  没有找到任何备份文件")
    return logs, restored


def disable_trae_autoupdate() -> Tuple[bool, str]:
    """禁用 Trae 自动更新（Windows：删除 trae-updater 目录并替换为只读文件）"""
    if not IS_WIN:
        return False, "仅 Windows 支持自动禁用更新"
    try:
        updater_dir = os.path.join(
            os.environ.get("LOCALAPPDATA", ""), "trae-updater")
        if os.path.isdir(updater_dir):
            shutil.rmtree(updater_dir, ignore_errors=True)
        # 创建同名文件占位，使更新器无法重新安装
        with open(updater_dir, "wb") as f:
            f.write(b"")
        # 设只读
        os.chmod(updater_dir, 0o444)
        return True, f"已禁用: {updater_dir}"
    except Exception as e:
        return False, f"禁用失败: {e}"


def make_storage_readonly(data_dir: str) -> Tuple[bool, str]:
    """将 storage.json 和 machineid 设为只读，防 Trae 启动时覆盖"""
    try:
        files = [
            os.path.join(data_dir, STORAGE_REL),
            os.path.join(data_dir, "machineid"),
            os.path.join(data_dir, ".updaterId"),
        ]
        cnt = 0
        for f in files:
            if os.path.isfile(f):
                os.chmod(f, 0o444)
                cnt += 1
        return True, f"已设只读 {cnt} 个文件"
    except Exception as e:
        return False, f"设置只读失败: {e}"


def make_storage_writable(data_dir: str) -> Tuple[bool, str]:
    """恢复可写（重置前调用，避免上次只读影响）"""
    try:
        files = [
            os.path.join(data_dir, STORAGE_REL),
            os.path.join(data_dir, "machineid"),
            os.path.join(data_dir, ".updaterId"),
        ]
        cnt = 0
        for f in files:
            if os.path.isfile(f):
                os.chmod(f, 0o666)
                cnt += 1
        return True, f"已恢复可写 {cnt} 个文件"
    except Exception as e:
        return False, f"恢复可写失败: {e}"


# ─── 渐变背景生成（PIL） ──────────────────────────────────────

_gradient_cache: Dict = {}

def make_gradient_image(width: int, height: int,
                       c1: str, c2: str, horizontal: bool = True):
    """生成渐变 PIL Image，缓存复用"""
    key = (width, height, c1, c2, horizontal)
    if key in _gradient_cache:
        return _gradient_cache[key]
    if not HAS_PIL:
        return None
    img = Image.new("RGB", (max(1, width), max(1, height)), c1)
    draw = ImageDraw.Draw(img)
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    if horizontal:
        for x in range(width):
            t = x / max(1, width - 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            draw.line([(x, 0), (x, height)], fill=(r, g, b))
    else:
        for y in range(height):
            t = y / max(1, height - 1)
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
    _gradient_cache[key] = img
    return img


# ─── T 字 Logo 生成（PIL 精致版） ─────────────────────────────

_logo_cache: Dict = {}

# Logo 渐变色（更明显的深→浅紫蓝）
LOGO_GRAD_DARK = "#3730a3"   # indigo-800
LOGO_GRAD_LIGHT = "#818cf8" # indigo-400

def make_logo_image(size: int = 96) -> Optional["Image.Image"]:
    """生成精致 T 字 logo：圆角方块 + 紫色斜向渐变 + 白色 T 字 + 阴影 + 高光"""
    if not HAS_PIL:
        return None
    key = ("logo_v3", size)
    if key in _logo_cache:
        return _logo_cache[key]

    # 4x 超采样抗锯齿
    scale = 4
    S = size * scale

    # 透明背景画布
    canvas = Image.new("RGBA", (S, S), (0, 0, 0, 0))

    # 圆角蒙版
    radius = int(S * 0.22)
    mask = Image.new("L", (S, S), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([(0, 0), (S - 1, S - 1)],
                          radius=radius, fill=255)

    # 斜向渐变（左上深紫 → 右下浅紫）
    grad = Image.new("RGB", (S, S), LOGO_GRAD_DARK)
    gd = ImageDraw.Draw(grad)
    c1 = LOGO_GRAD_DARK
    c2 = LOGO_GRAD_LIGHT
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    diag = (S ** 2 + S ** 2) ** 0.5
    # 用 numpy-like 但避免依赖：每行扫描
    for y in range(S):
        # 对角线参数：t = (x + y) / diag
        # 一次画 1 行，但用 4 像素分块提高速度
        for x in range(0, S, 2):
            t = (x + y) / diag
            if t > 1: t = 1
            r = int(r1 + (r2 - r1) * t)
            g = int(g1 + (g2 - g1) * t)
            b = int(b1 + (b2 - b1) * t)
            gd.rectangle([(x, y), (x + 2, y + 1)], fill=(r, g, b))

    grad_rgba = grad.convert("RGBA")
    grad_rgba.putalpha(mask)

    # 阴影层
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle(
        [(3, 5), (S - 2, S - 2)], radius=radius,
        fill=(15, 23, 42, 90))  # 深蓝灰阴影
    try:
        from PIL import ImageFilter
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=int(S * 0.05)))
    except Exception:
        pass

    # 合成：阴影 → 渐变主体
    canvas.paste(shadow, (0, 0), shadow)
    canvas.paste(grad_rgba, (0, 0), grad_rgba)

    # 绘制白色 T 字
    draw = ImageDraw.Draw(canvas)
    bar_h = int(S * 0.14)    # 横笔画高度
    bar_w = int(S * 0.62)    # 横笔画宽度
    stem_w = int(S * 0.16)   # 竖笔画宽度
    stem_h = int(S * 0.56)   # 竖笔画高度
    bar_x0 = (S - bar_w) // 2
    bar_y0 = int(S * 0.18)
    bar_x1 = bar_x0 + bar_w
    bar_y1 = bar_y0 + bar_h
    stem_x0 = (S - stem_w) // 2
    stem_y0 = bar_y1 - int(S * 0.02)  # 与横笔画相连
    stem_x1 = stem_x0 + stem_w
    stem_y1 = stem_y0 + stem_h

    # T 字阴影
    so = max(2, int(S * 0.02))
    draw.rounded_rectangle(
        [(bar_x0 + so, bar_y0 + so), (bar_x1 + so, bar_y1 + so)],
        radius=int(bar_h * 0.3), fill=(0, 0, 0, 80))
    draw.rounded_rectangle(
        [(stem_x0 + so, stem_y0 + so), (stem_x1 + so, stem_y1 + so)],
        radius=int(stem_w * 0.3), fill=(0, 0, 0, 80))
    # 白色 T 字主体
    draw.rounded_rectangle(
        [(bar_x0, bar_y0), (bar_x1, bar_y1)],
        radius=int(bar_h * 0.3), fill=(255, 255, 255, 255))
    draw.rounded_rectangle(
        [(stem_x0, stem_y0), (stem_x1, stem_y1)],
        radius=int(stem_w * 0.3), fill=(255, 255, 255, 255))

    # 顶部高光（半透明白色，营造立体感）
    try:
        highlight = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        hd = ImageDraw.Draw(highlight)
        hd.pieslice(
            [(0, -int(S * 0.3)), (S, int(S * 0.4))],
            180, 360, fill=(255, 255, 255, 70))
        # 用圆角蒙版裁切高光（保留椭圆区域 alpha，圆角外 alpha=0）
        hl_clip = Image.new("L", (S, S), 0)
        hcd = ImageDraw.Draw(hl_clip)
        hcd.rounded_rectangle([(0, 0), (S - 1, S - 1)],
                               radius=radius, fill=255)
        # 关键：用 ImageChops 或者手动合成 alpha，避免覆盖椭圆外的 RGB
        # 这里用 alpha_composite 实现
        from PIL import Image as PILImage
        # 创建一个临时画布：把 highlight 限制在圆角内
        tmp = PILImage.new("RGBA", (S, S), (0, 0, 0, 0))
        tmp.paste(highlight, (0, 0), hl_clip)
        # alpha 合成到 canvas（不是 paste 覆盖）
        canvas = PILImage.alpha_composite(canvas, tmp)
    except Exception as e:
        print(f"高光合成失败: {e}")

    # 缩小到目标尺寸（抗锯齿）
    final = canvas.resize((size, size), Image.LANCZOS)
    _logo_cache[key] = final
    return final


# ─── 登录页 ────────────────────────────────────────────────────

class LoginFrame(ctk.CTkFrame):
    """卡密登录页 - 卡片化设计"""

    def __init__(self, parent, on_success, on_exit):
        super().__init__(parent, fg_color=BG)
        self.on_success = on_success
        self.on_exit = on_exit
        self.client = LicenseClient()
        self.store = LicenseStore()
        self._logo_tk = None  # 保留引用防 GC
        self._build()

    def _build(self):
        # 居中容器（用 grid 居中，避免 pack_propagate 问题）
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.pack(fill="both", expand=True)
        outer.grid_rowconfigure(0, weight=1)
        outer.grid_columnconfigure(0, weight=1)
        wrap = ctk.CTkFrame(outer, fg_color="transparent")
        wrap.grid(row=0, column=0)

        # ── Logo 区 ──
        logo_frame = ctk.CTkFrame(wrap, fg_color="transparent", height=96)
        logo_frame.pack(pady=(0, 16), padx=0)
        logo_frame.pack_propagate(False)

        logo_pil = make_logo_image(88)
        if logo_pil is not None:
            # 用 CTkImage 支持 HighDPI 自适应缩放
            self._logo_ctk = ctk.CTkImage(
                light_image=logo_pil, dark_image=logo_pil,
                size=(88, 88))
            ctk.CTkLabel(logo_frame, image=self._logo_ctk, text="",
                         fg_color="transparent").place(relx=0.5, rely=0.5, anchor="center")
        else:
            # PIL 不可用时回退到纯色方块
            logo_box = ctk.CTkFrame(logo_frame, fg_color=BTN_PRIMARY_S,
                                    corner_radius=20, width=80, height=80)
            logo_box.place(relx=0.5, rely=0.5, anchor="center")
            ctk.CTkLabel(logo_box, text="T",
                         font=ctk.CTkFont(family=FONT_UI, size=36, weight="bold"),
                         text_color=FG_WHITE).place(relx=0.5, rely=0.5, anchor="center")

        # ── 标题 ──
        ctk.CTkLabel(wrap, text="trae助手reset工具",
                     font=ctk.CTkFont(family=FONT_UI, size=24, weight="bold"),
                     text_color=FG).pack(pady=(0, 2))
        ctk.CTkLabel(wrap,
                     text=f"Trae 身份重置 · {APP_AUTHOR}",
                     font=ctk.CTkFont(family=FONT_UI, size=12),
                     text_color=FG_DIM).pack(pady=(0, 2))
        ctk.CTkLabel(wrap, text=APP_WEBSITE,
                     font=ctk.CTkFont(family=FONT_UI, size=11),
                     text_color=FG_LINK).pack(pady=(0, 24))

        # ── 登录卡片 ──
        card = ctk.CTkFrame(wrap, fg_color=BG_CARD, corner_radius=14,
                            border_width=1, border_color=BORDER)
        card.pack(fill="both", expand=True, padx=0, pady=(0, 12))

        # 顶部紫色装饰条
        top_bar = ctk.CTkFrame(card, fg_color=BTN_PRIMARY_S, height=4,
                               corner_radius=14)
        top_bar.pack(fill="x")

        # 卡片内容容器（用 grid 严格布局，避免按钮被挤掉）
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=24, pady=(18, 18))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(99, weight=1)  # 弹性

        # 标题行
        ctk.CTkLabel(content, text="卡密登录",
                     font=ctk.CTkFont(family=FONT_UI, size=16, weight="bold"),
                     text_color=FG).grid(row=0, column=0, sticky="w", pady=(0, 4))

        # 提示
        ctk.CTkLabel(content,
                     text="请输入授权卡密以激活本工具",
                     font=ctk.CTkFont(family=FONT_UI, size=12),
                     text_color=FG_DIM).grid(row=1, column=0, sticky="w", pady=(0, 14))

        # 输入框（占满宽度）
        self.card_entry = ctk.CTkEntry(
            content, placeholder_text="TRAE-XXXX-XXXX-XXXX",
            font=ctk.CTkFont(family=FONT_MONO, size=14),
            fg_color=BG_INPUT, text_color=FG,
            corner_radius=10, height=46,
            border_width=1, border_color=BORDER)
        self.card_entry.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.card_entry.bind("<Return>", lambda e: self._do_login())

        # 记住卡密复选框
        self.remember_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(content, text="记住卡密（加密缓存，24小时离线宽限）",
                        variable=self.remember_var,
                        font=ctk.CTkFont(family=FONT_UI, size=12),
                        text_color=FG_BODY, fg_color=BTN_PRIMARY_S,
                        hover_color=BTN_PRIMARY_E).grid(
            row=3, column=0, sticky="w", pady=(0, 12))

        # 状态提示（多行 wraplength，确保错误完整显示）
        self.status_label = ctk.CTkLabel(
            content, text="",
            font=ctk.CTkFont(family=FONT_UI, size=12),
            text_color=FG_DIM, wraplength=420, justify="left",
            anchor="w", height=36)
        self.status_label.grid(row=4, column=0, sticky="ew", pady=(0, 12))

        # 主按钮：占满整行（紫色渐变，大按钮）
        self.login_btn = ctk.CTkButton(
            content, text="登录验证",
            height=48,
            font=ctk.CTkFont(family=FONT_UI, size=15, weight="bold"),
            fg_color=BTN_PRIMARY_S, hover_color=BTN_PRIMARY_E,
            text_color=FG_WHITE, corner_radius=12,
            command=self._do_login)
        self.login_btn.grid(row=5, column=0, sticky="ew", pady=(0, 8))

        # 退出按钮：右下角小按钮
        exit_btn = ctk.CTkButton(
            content, text="退出程序",
            height=36,
            font=ctk.CTkFont(family=FONT_UI, size=12),
            fg_color=GHOST, hover_color=GHOST_H,
            text_color=FG_BODY, corner_radius=8,
            command=self.on_exit)
        exit_btn.grid(row=6, column=0, sticky="e")

        # ── 底部版本信息 ──
        ctk.CTkLabel(wrap, text=f"v{VERSION}  ·  {APP_AUTHOR}",
                     font=ctk.CTkFont(family=FONT_UI, size=11),
                     text_color=FG_DIM).pack(pady=(8, 0))

        # 自动尝试离线缓存登录
        self.after(200, self._try_auto_login)

    def _try_auto_login(self):
        data = self.store.load_license()
        if not data:
            return
        if not self.store.is_offline_grace_valid():
            self.status_label.configure(
                text="⚠ 缓存已超过 24 小时离线宽限，请重新登录",
                text_color=BADGE_WARN_FG)
            return
        # 离线模式：直接放行
        self.on_success(data, offline=True)

    def _do_login(self):
        key = self.card_entry.get().strip()
        if not key:
            self.status_label.configure(text="❌ 请输入卡密", text_color=BADGE_ERR_FG)
            return
        self.login_btn.configure(state="disabled", text="正在验证...")
        self.status_label.configure(text="正在连接服务器验证...", text_color=FG_DIM)
        self.update_idletasks()

        def worker():
            try:
                resp = self.client.check_card(key)
                self.after(0, lambda: self._on_resp(resp, key))
            except LicenseAPIError as e:
                # 网络失败，尝试离线缓存
                cached = self.store.load_license()
                if cached and cached.get("card_key") == key and \
                        self.store.is_offline_grace_valid():
                    self.after(0, lambda: self.on_success(cached, offline=True))
                else:
                    err_msg = str(e)
                    # 截断超长错误信息但保留关键内容
                    if len(err_msg) > 200:
                        err_msg = err_msg[:200] + "..."
                    self.after(0, lambda: self.status_label.configure(
                        text=f"❌ 网络错误: {err_msg}",
                        text_color=BADGE_ERR_FG))
                    self.after(0, lambda: self.login_btn.configure(
                        state="normal", text="登录验证"))

        threading.Thread(target=worker, daemon=True).start()

    def _on_resp(self, resp: Dict, card_key: str):
        if not resp.get("success"):
            # 后端可能返回 'message' 字段，或原始响应文本
            msg = resp.get("message", "")
            if not msg:
                msg = resp.get("error", "验证失败")
            # 如果是 PHP 后端返回的 server error，提示更友好
            msg_lower = str(msg).lower()
            if "server error" in msg_lower or "服务器错误" in msg:
                msg = f"服务器错误: {msg}（请联系管理员检查后端数据库配置）"
            elif "network" in msg_lower or "请求失败" in msg:
                msg = f"网络异常: {msg}"
            self.status_label.configure(text=f"❌ {msg}", text_color=BADGE_ERR_FG)
            self.login_btn.configure(state="normal", text="登录验证")
            return
        data = {
            "card_key": card_key,
            "card_type": resp.get("card_type", "normal"),
            "expire_date": resp.get("expire_date", "永久"),
            "bound_devices": resp.get("bound_devices", 0),
            "max_devices": resp.get("max_devices", 1),
        }
        if self.remember_var.get():
            self.store.save_license(data)
        self.on_success(data, offline=False)


# ─── 主应用 ────────────────────────────────────────────────────

class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BG)
        self.title(APP_TITLE)
        self.current_dir: Optional[str] = None
        self.license_data: Optional[Dict] = None
        self.offline_mode: bool = False
        self.client = LicenseClient()
        self.store = LicenseStore()
        self.heartbeat_thread: Optional[HeartbeatThread] = None
        self.action_btns: List = []
        self.countdown_job = None
        self.last_heartbeat_warn = 0
        self.tray_icon = None
        self._logo_ctk = None
        self._hdr_logo_ctk = None

        # ── Windows 任务栏图标修复 ──
        # ctypes.windll.shell32.ShellExecute 用的是 Python 解释器的图标，
        # 编译为 exe 后用 iconfrom-ico 设置；运行时通过 SetWindowPos 强制刷新任务栏
        self._set_taskbar_icon()

        # 窗口尺寸 & 居中（适配屏幕高度，留 60px 给任务栏）
        W = 1040
        H = 760
        self.update_idletasks()
        sx = self.winfo_screenwidth()
        sy = self.winfo_screenheight()
        # 最大高度 = 屏幕高度 - 任务栏(40) - 边距(20)
        max_h = sy - 60
        if H > max_h:
            H = max_h
        x = max(0, (sx - W) // 2)
        y = max(0, (sy - H) // 2 - 10)
        self.geometry(f"{W}x{H}+{x}+{y}")
        self.minsize(940, 640)

        # 登录页 & 主页
        self.login_frame: Optional[LoginFrame] = None
        self.main_frame = ctk.CTkFrame(self, fg_color=BG)
        self._build_main()

        # 默认显示登录页
        self._show_login()

        # 关闭窗口事件
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _set_taskbar_icon(self):
        """Windows 任务栏图标修复"""
        if not IS_WIN:
            return
        try:
            # 找 exe 同目录的 .ico
            exe_dir = os.path.dirname(sys.executable if getattr(sys, "frozen", False) else os.path.abspath(__file__))
            ico_path = os.path.join(exe_dir, "app_icon.ico")
            if not os.path.isfile(ico_path):
                ico_path = os.path.join(os.path.dirname(exe_dir), "app_icon.ico")
            if os.path.isfile(ico_path):
                import tkinter as tk
                self.iconbitmap(default=ico_path)
                self.iconbitmap(ico_path)
        except Exception as e:
            print(f"任务栏图标设置失败: {e}")

    # ─── 登录页 ──────────────────────────────────────────────

    def _show_login(self):
        if self.main_frame.winfo_ismapped():
            self.main_frame.pack_forget()
        if self.login_frame is None:
            self.login_frame = LoginFrame(
                self,
                on_success=self._on_login_success,
                on_exit=self._on_exit)
        self.login_frame.pack(fill="both", expand=True)

    def _on_login_success(self, data: Dict, offline: bool):
        self.license_data = data
        self.offline_mode = offline
        self.login_frame.pack_forget()
        self.main_frame.pack(fill="both", expand=True)
        self._update_license_card()
        self._on_startup()
        # 启动心跳线程（仅在线上模式时）
        if not offline:
            self.heartbeat_thread = HeartbeatThread(self, data.get("card_key", ""))
            self.heartbeat_thread.start()
        else:
            self._set_status_badge("offline", f"离线模式 · v{VERSION}")

    def _on_exit(self):
        self.destroy()
        sys.exit(0)

    def _on_close(self):
        """关闭窗口：最小化到托盘（如果有）或直接退出"""
        try:
            self._build_tray()
            if self.tray_icon:
                self.withdraw()
                return
        except Exception:
            pass
        self._cleanup_and_exit()

    def _cleanup_and_exit(self):
        if self.heartbeat_thread:
            self.heartbeat_thread.stop()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except Exception:
                pass
        self.destroy()

    # ─── 托盘 ─────────────────────────────────────────────────

    def _build_tray(self):
        if self.tray_icon or not HAS_PIL:
            return
        try:
            import pystray
            # 用精致 T 字 logo
            img = make_logo_image(64)
            if img is None:
                from PIL import Image as PILImage
                img = PILImage.new("RGB", (64, 64), BTN_PRIMARY_S)
            else:
                # pystray 需要 RGBA 或 RGB，转一下
                if img.mode == "RGBA":
                    # 在白底上合成避免透明区域看起来奇怪
                    from PIL import Image as PILImage
                    bg = PILImage.new("RGB", img.size, (255, 255, 255))
                    bg.paste(img, (0, 0), img)
                    img = bg
            menu = pystray.Menu(
                pystray.MenuItem("显示主界面", self._tray_show, default=True),
                pystray.MenuItem("退出", self._tray_exit),
            )
            self.tray_icon = pystray.Icon(
                "TraeReset", img, APP_TITLE, menu)
            threading.Thread(
                target=self.tray_icon.run, daemon=True).start()
        except ImportError:
            pass
        except Exception as e:
            print(f"托盘初始化失败: {e}")

    def _tray_show(self, *args):
        self.after(0, lambda: self.deiconify())

    def _tray_exit(self, *args):
        self.after(0, self._cleanup_and_exit)

    # ─── 主界面构建 ───────────────────────────────────────────

    def _build_main(self):
        m = self.main_frame
        # 主容器用 grid，自适应窗口大小
        m.grid_rowconfigure(1, weight=1)   # 中间内容区可伸缩
        m.grid_columnconfigure(0, weight=1)

        # ── 1. 顶部标题栏（固定 64px） ──
        hdr = ctk.CTkFrame(m, fg_color=BG_CARD, corner_radius=0, height=64)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.grid_propagate(False)
        hdr.grid_columnconfigure(1, weight=1)

        # 左侧 Logo（用 CTkImage）
        logo_pil = make_logo_image(40)
        if logo_pil is not None:
            self._hdr_logo_ctk = ctk.CTkImage(
                light_image=logo_pil, dark_image=logo_pil,
                size=(40, 40))
            ctk.CTkLabel(hdr, image=self._hdr_logo_ctk, text="",
                         fg_color="transparent").grid(
                row=0, column=0, padx=(16, 10), pady=12, sticky="w")
        else:
            logo_box = ctk.CTkFrame(hdr, fg_color=BTN_PRIMARY_S, corner_radius=8,
                                    width=40, height=40)
            logo_box.grid(row=0, column=0, padx=(16, 10), pady=12)
            logo_box.pack_propagate(False)
            ctk.CTkLabel(logo_box, text="T",
                         font=ctk.CTkFont(family=FONT_UI, size=18, weight="bold"),
                         text_color=FG_WHITE).place(relx=0.5, rely=0.5, anchor="center")

        # 标题文字（column=1，weight=1 拉伸）
        title_col = ctk.CTkFrame(hdr, fg_color="transparent")
        title_col.grid(row=0, column=1, sticky="ew", pady=12)
        title_col.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(title_col, text="trae助手reset工具",
                     font=ctk.CTkFont(family=FONT_UI, size=16, weight="bold"),
                     text_color=FG).grid(row=0, column=0, sticky="w", pady=(0, 0))
        ctk.CTkLabel(title_col,
                     text=f"{APP_AUTHOR} · {APP_WEBSITE}",
                     font=ctk.CTkFont(family=FONT_UI, size=11),
                     text_color=FG_DIM).grid(row=1, column=0, sticky="w")

        # 右侧徽章（column=2）
        badge_col = ctk.CTkFrame(hdr, fg_color="transparent")
        badge_col.grid(row=0, column=2, padx=(0, 16), pady=12, sticky="e")
        self.status_badge = ctk.CTkLabel(
            badge_col, text="● 未登录",
            font=ctk.CTkFont(family=FONT_UI, size=11, weight="bold"),
            fg_color=BADGE_ERR_BG, text_color=BADGE_ERR_FG,
            corner_radius=999, padx=10, pady=3)
        self.status_badge.pack(side="left", padx=(0, 6))
        # 只显示一个版本徽章，避免重复
        self.version_badge = ctk.CTkLabel(
            badge_col, text=f"v{VERSION}",
            font=ctk.CTkFont(family=FONT_UI, size=11, weight="bold"),
            fg_color=BADGE_INFO_BG, text_color=BADGE_INFO_FG,
            corner_radius=999, padx=10, pady=3)
        self.version_badge.pack(side="left")

        # ── 2. 中间内容区（grid 3 行布局：卡片 / 警示 / 两列 / 日志） ──
        content = ctk.CTkFrame(m, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=12, pady=(8, 8))
        content.grid_columnconfigure((0, 1), weight=1)
        # 行：0=卡片；1=警示条；2=两列功能区；3=操作日志
        content.grid_rowconfigure(0, weight=0)   # 卡片区固定
        content.grid_rowconfigure(1, weight=0)   # 警示条固定
        content.grid_rowconfigure(2, weight=2, minsize=320)  # 中部两列（较高）
        content.grid_rowconfigure(3, weight=1, minsize=100)   # 日志区

        # ── 2a. 4 张渐变卡片（横跨 2 列） ──
        top_wrap = ctk.CTkFrame(content, fg_color="transparent")
        top_wrap.grid(row=0, column=0, columnspan=2, sticky="ew")
        top_wrap.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="card")

        self.card_labels: Dict[str, ctk.CTkLabel] = {}
        self.card_imgs: Dict[str, ctk.CTkImage] = {}
        for i, (key, label_text, c1, c2, default_val) in enumerate([
            ("card_key",   "授权卡密",   CARD_BLUE_S,   CARD_BLUE_E,   "****"),
            ("card_type",  "卡密类型",   CARD_PURPLE_S, CARD_PURPLE_E, "普通"),
            ("bound",      "设备绑定",   CARD_ORANGE_S, CARD_ORANGE_E, "0 / 1"),
            ("expire",     "剩余有效期", CARD_GREEN_S,  CARD_GREEN_E,  "永久"),
        ]):
            card = self._make_gradient_card(
                top_wrap, label_text, default_val, c1, c2)
            card.grid(row=0, column=i, padx=(0 if i == 0 else 4, 4 if i == 3 else 0),
                      sticky="nsew")

        # 警示条（固定 50px 高度）
        warn = ctk.CTkFrame(content, fg_color=WARN_BG, corner_radius=6,
                            border_width=0, height=50)
        warn.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(4, 4))
        warn.grid_propagate(False)
        # 橙色左边框
        bar = ctk.CTkFrame(warn, fg_color=WARN_BORDER, width=3,
                          corner_radius=0)
        bar.pack(side="left", fill="y")
        ctk.CTkLabel(
            warn,
            text="  注意：本工具需要更换 IP 重置网络，使用工具后请重新申请登录新账户",
            font=ctk.CTkFont(family=FONT_UI, size=12),
            text_color=WARN_TEXT, anchor="w"
        ).pack(side="left", fill="both", expand=True, padx=6, pady=3)

        # ── 2b. 左列：数据目录 + 当前状态 ──
        left_col = ctk.CTkFrame(content, fg_color="transparent")
        left_col.grid(row=2, column=0, sticky="nsew", padx=(0, 6))
        left_col.grid_rowconfigure(1, weight=1)
        left_col.grid_columnconfigure(0, weight=1)

        # 左-1: 数据目录卡片
        dir_card = ctk.CTkFrame(left_col, fg_color=BG_CARD, corner_radius=8,
                                border_width=1, border_color=BORDER)
        dir_card.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        dir_inner = ctk.CTkFrame(dir_card, fg_color="transparent")
        dir_inner.pack(fill="x", padx=14, pady=10)

        dir_title_row = ctk.CTkFrame(dir_inner, fg_color="transparent")
        dir_title_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(dir_title_row, text="数据目录",
                     font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
                     text_color=FG).pack(side="left")

        dir_row = ctk.CTkFrame(dir_inner, fg_color="transparent")
        dir_row.pack(fill="x")
        self.dir_combobox = ctk.CTkComboBox(
            dir_row, values=["点击右侧刷新"], width=260,
            font=ctk.CTkFont(family=FONT_MONO, size=12),
            dropdown_font=ctk.CTkFont(family=FONT_MONO, size=12),
            fg_color=BG_INPUT, text_color=FG, border_color=BORDER,
            button_color=BTN_PRIMARY_S, button_hover_color=BTN_PRIMARY_E,
            command=self._on_combobox_select)
        self.dir_combobox.pack(side="left", padx=(0, 6))
        self.dir_combobox.set("点击「自动检测」")

        ctk.CTkButton(dir_row, text="自动检测", width=78, height=30,
                      font=ctk.CTkFont(family=FONT_UI, size=12),
                      fg_color=BTN_PRIMARY_S, hover_color=BTN_PRIMARY_E,
                      text_color=FG_WHITE, corner_radius=6,
                      command=self._on_auto_detect).pack(side="left", padx=(0, 6))
        ctk.CTkButton(dir_row, text="手动", width=54, height=30,
                      font=ctk.CTkFont(family=FONT_UI, size=12),
                      fg_color=BLUE, hover_color=BLUE_H,
                      text_color=FG_WHITE, corner_radius=6,
                      command=self._on_browse).pack(side="left", padx=(0, 6))
        ctk.CTkButton(dir_row, text="恢复", width=54, height=30,
                      font=ctk.CTkFont(family=FONT_UI, size=12),
                      fg_color=GHOST, hover_color=GHOST_H,
                      text_color=FG_BODY, corner_radius=5,
                      command=self._on_restore).pack(side="left")

        self.dir_label = ctk.CTkLabel(
            dir_inner, text="未选择 — 请点击「自动检测」",
            font=ctk.CTkFont(family=FONT_MONO, size=11), text_color=FG_DIM,
            anchor="w", wraplength=460)
        self.dir_label.pack(anchor="w", pady=(8, 0))

        # 左-2: 当前状态卡片
        sc = ctk.CTkFrame(left_col, fg_color=BG_CARD, corner_radius=8,
                         border_width=1, border_color=BORDER)
        sc.grid(row=1, column=0, sticky="nsew")
        si = ctk.CTkFrame(sc, fg_color="transparent")
        si.pack(fill="both", expand=True, padx=14, pady=10)

        st_top = ctk.CTkFrame(si, fg_color="transparent")
        st_top.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(st_top, text="当前状态",
                     font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
                     text_color=FG).pack(side="left")
        ctk.CTkButton(st_top, text="刷新", width=54, height=26,
                      font=ctk.CTkFont(family=FONT_UI, size=11),
                      fg_color=GHOST, hover_color=GHOST_H,
                      text_color=FG_BODY, corner_radius=4,
                      command=self._on_refresh).pack(side="right")

        self.info_labels = {}
        for key, txt in [("mid", "Machine ID"),
                         ("did", "Dev Device ID")]:
            row = ctk.CTkFrame(si, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=f"{txt}:", width=120, anchor="w",
                         font=ctk.CTkFont(family=FONT_UI, size=13),
                         text_color=FG_DIM).pack(side="left")
            v = ctk.CTkLabel(row, text="-", anchor="w",
                             font=ctk.CTkFont(family=FONT_MONO, size=13),
                             text_color=FG_LINK, wraplength=360)
            v.pack(side="left", fill="x", expand=True)
            self.info_labels[key] = v

        # ── 2c. 右列：操作 + 高级选项 ──
        right_col = ctk.CTkFrame(content, fg_color="transparent")
        right_col.grid(row=2, column=1, sticky="nsew", padx=(6, 0))
        # row 0 操作卡片固定，row 1 高级选项卡片拉伸填充
        right_col.grid_rowconfigure(0, weight=0)
        right_col.grid_rowconfigure(1, weight=1)
        right_col.grid_columnconfigure(0, weight=1)

        # 右-1: 操作卡片（不拉伸）
        ac = ctk.CTkFrame(right_col, fg_color=BG_CARD, corner_radius=8,
                         border_width=1, border_color=BORDER)
        ac.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        ai = ctk.CTkFrame(ac, fg_color="transparent")
        ai.pack(fill="x", padx=14, pady=10)

        ctk.CTkLabel(ai, text="操作",
                     font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
                     text_color=FG).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(ai,
                     text="遇到「设备数量已达上限」？点「一键重置」即可",
                     font=ctk.CTkFont(family=FONT_UI, size=12),
                     text_color=FG_DIM).pack(anchor="w", pady=(0, 10))

        self._btn_oneclick = ctk.CTkButton(
            ai, text="一键重置  —  清除账号 + 重置设备 ID",
            height=48,
            font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
            fg_color=BTN_PRIMARY_S, hover_color=BTN_PRIMARY_E,
            text_color=FG_WHITE, corner_radius=8,
            command=self._on_oneclick)
        self._btn_oneclick.pack(fill="x", pady=(0, 10))

        # 次要操作行
        sub_row = ctk.CTkFrame(ai, fg_color="transparent")
        sub_row.pack(fill="x")
        self.action_btns = [self._btn_oneclick]
        for txt, c, h, cmd in [
            ("清除所有账号", RED,   RED_H,   self._on_clear),
            ("重置设备 ID",  AMBER, AMBER_H, self._on_reset),
        ]:
            b = ctk.CTkButton(sub_row, text=txt, height=36,
                              font=ctk.CTkFont(family=FONT_UI, size=13),
                              fg_color=c, hover_color=h,
                              text_color=FG_WHITE, corner_radius=7,
                              command=cmd)
            b.pack(side="left", padx=(0, 6), expand=True, fill="x")
            self.action_btns.append(b)

        # 管理员提示（紧凑）
        if IS_WIN and not is_admin():
            admin_row = ctk.CTkFrame(ai, fg_color=BG_INPUT, corner_radius=6)
            admin_row.pack(fill="x", pady=(8, 0))
            admin_inner = ctk.CTkFrame(admin_row, fg_color="transparent")
            admin_inner.pack(fill="x", padx=10, pady=5)
            ctk.CTkLabel(admin_inner,
                         text="注册表重置需管理员权限",
                         font=ctk.CTkFont(family=FONT_UI, size=10),
                         text_color=FG_DIM).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(admin_inner, text="管理员重启", width=80, height=24,
                          font=ctk.CTkFont(family=FONT_UI, size=10),
                          fg_color=GHOST, hover_color=GHOST_H,
                          text_color=FG_BODY, corner_radius=5,
                          command=self._restart_admin).pack(side="right")

        # 右-2: 高级选项卡片
        adv = ctk.CTkFrame(right_col, fg_color=BG_CARD, corner_radius=8,
                          border_width=1, border_color=BORDER)
        adv.grid(row=1, column=0, sticky="nsew")
        adv_i = ctk.CTkFrame(adv, fg_color="transparent")
        adv_i.pack(fill="both", expand=True, padx=14, pady=10)
        ctk.CTkLabel(adv_i, text="高级选项",
                     font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
                     text_color=FG).pack(anchor="w", pady=(0, 8))

        self.opt_readonly = ctk.BooleanVar(value=self.store.get_config("opt_readonly", True))
        self.opt_kill = ctk.BooleanVar(value=self.store.get_config("opt_kill", True))
        self.opt_disable_update = ctk.BooleanVar(
            value=self.store.get_config("opt_disable_update", False))

        for text, var, desc in [
            ("重置后设只读", self.opt_readonly,
             "防 Trae 启动时覆盖"),
            ("自动结束 Trae", self.opt_kill,
             "检测到运行自动结束"),
            ("禁用自动更新", self.opt_disable_update,
             "删除 trae-updater 目录"),
        ]:
            row = ctk.CTkFrame(adv_i, fg_color="transparent")
            row.pack(fill="x", pady=4)
            ctk.CTkCheckBox(row, text=text, variable=var,
                            font=ctk.CTkFont(family=FONT_UI, size=12),
                            text_color=FG_BODY, fg_color=BTN_PRIMARY_S,
                            hover_color=BTN_PRIMARY_E).pack(side="left")
            ctk.CTkLabel(row, text=desc,
                        font=ctk.CTkFont(family=FONT_UI, size=10),
                        text_color=FG_DIM).pack(side="left", padx=(8, 0))

        # ── 2d. 底部日志区（横跨 2 列，高度自适应） ──
        lc = ctk.CTkFrame(content, fg_color=BG_CARD, corner_radius=8,
                          border_width=1, border_color=BORDER)
        lc.grid(row=3, column=0, columnspan=2, sticky="nsew", pady=(6, 0))
        li = ctk.CTkFrame(lc, fg_color="transparent")
        li.pack(fill="both", expand=True, padx=14, pady=10)

        log_top = ctk.CTkFrame(li, fg_color="transparent")
        log_top.pack(fill="x", pady=(0, 6))
        ctk.CTkLabel(log_top, text="操作日志",
                     font=ctk.CTkFont(family=FONT_UI, size=14, weight="bold"),
                     text_color=FG).pack(side="left")
        ctk.CTkButton(log_top, text="复制", width=54, height=26,
                      font=ctk.CTkFont(family=FONT_UI, size=11),
                      fg_color=GHOST, hover_color=GHOST_H,
                      text_color=FG_BODY, corner_radius=4,
                      command=self._copy_log).pack(side="right", padx=(4, 0))
        ctk.CTkButton(log_top, text="清空", width=54, height=26,
                      font=ctk.CTkFont(family=FONT_UI, size=11),
                      fg_color=GHOST, hover_color=GHOST_H,
                      text_color=FG_BODY, corner_radius=4,
                      command=self._clear_log).pack(side="right", padx=(4, 0))
        ctk.CTkButton(log_top, text="导出", width=54, height=26,
                      font=ctk.CTkFont(family=FONT_UI, size=11),
                      fg_color=GHOST, hover_color=GHOST_H,
                      text_color=FG_BODY, corner_radius=4,
                      command=self._export_log).pack(side="right", padx=(4, 0))

        self.log_box = ctk.CTkTextbox(
            li, font=ctk.CTkFont(family=FONT_MONO, size=12),
            fg_color=BG_INPUT, text_color=FG_BODY,
            corner_radius=6, wrap="word", state="disabled",
            border_width=1, border_color=BORDER)
        self.log_box.pack(fill="both", expand=True)
        self.log_box.tag_config("ok",   foreground=GREEN)
        self.log_box.tag_config("warn", foreground=AMBER)
        self.log_box.tag_config("err",  foreground=RED)
        self.log_box.tag_config("dim",  foreground=FG_DIM)

    def _make_gradient_card(self, parent, label_text, value_text, c1, c2):
        """创建渐变信息卡片"""
        if HAS_PIL:
            # 用 Canvas + PIL 渐变图实现真正渐变
            import tkinter as tk
            canv = tk.Canvas(parent, height=100, bg=BG, bd=0,
                              highlightthickness=0)
            canv.pack_propagate(False)
            # 先占位，绘制延后到 _redraw_gradient_card
            canv._card_label = label_text
            canv._card_value = value_text
            canv._c1 = c1
            canv._c2 = c2
            canv._grad_img = None
            canv._tk_img = None
            # 绘制
            self.after(50, lambda: self._redraw_gradient_card(canv))
            canv.bind("<Configure>",
                      lambda e: self._redraw_gradient_card(canv))
            return canv
        else:
            # 回退：单色 CTkFrame
            card = ctk.CTkFrame(parent, fg_color=c1, corner_radius=12)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=label_text,
                         font=ctk.CTkFont(family=FONT_UI, size=11, weight="bold"),
                         text_color=FG_WHITE).pack(anchor="w", padx=14, pady=(12, 0))
            v_lbl = ctk.CTkLabel(card, text=value_text,
                                 font=ctk.CTkFont(family=FONT_UI, size=18, weight="bold"),
                                 text_color=FG_WHITE)
            v_lbl.pack(anchor="w", padx=14, pady=(4, 12))
            self.card_labels[label_text] = v_lbl
            return card

    def _redraw_gradient_card(self, canv):
        """重绘渐变卡片"""
        try:
            w = canv.winfo_width()
            h = canv.winfo_height()
            if w < 10 or h < 10:
                self.after(50, lambda: self._redraw_gradient_card(canv))
                return
            img = make_gradient_image(w, h, canv._c1, canv._c2, horizontal=True)
            if img is None:
                return
            canv._tk_img = ImageTk.PhotoImage(img)
            canv.delete("all")
            canv.create_image(0, 0, image=canv._tk_img, anchor="nw")
            # 圆角矩形 mask 不做（简化），直接铺满
            canv.create_text(14, 14, text=canv._card_label,
                             fill=FG_WHITE,
                             font=(FONT_UI, 11, "bold"), anchor="nw")
            canv.create_text(14, h - 12, text=canv._card_value,
                             fill=FG_WHITE,
                             font=(FONT_UI, 18, "bold"), anchor="sw")
            # 缓存引用
            if not hasattr(self, "card_labels"):
                self.card_labels = {}
            self.card_labels[canv._card_label] = canv
        except Exception as e:
            print(f"渐变卡片重绘失败: {e}")

    # ─── 启动 ────────────────────────────────────────────────

    def _on_startup(self):
        self._log("=" * 44)
        self._log(f"  {APP_TITLE}")
        self._log(f"  {APP_AUTHOR} · {APP_WEBSITE}")
        self._log("=" * 44)
        self._log("")

        # 自动检测
        self._on_auto_detect(silent=True)

        if self.current_dir:
            self._do_refresh(silent=True)

        self._log("")
        for i, t in enumerate(GUIDE_TIPS, 1):
            self._log(f"  {i}. {t}", "dim")
        self._log("")

    # ─── 工具方法 ─────────────────────────────────────────────

    def _log(self, msg, tag=None):
        self.log_box.configure(state="normal")
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        self.log_box.insert("end", line, tag if tag else ())
        lc = int(self.log_box.index("end-1c").split(".")[0])
        if lc > 500:
            self.log_box.delete("1.0", f"{lc - 400}.0")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _copy_log(self):
        try:
            self.clipboard_clear()
            self.clipboard_append(self.log_box.get("1.0", "end"))
            self._log("日志已复制到剪贴板", "dim")
        except Exception as e:
            self._log(f"复制失败: {e}", "err")

    def _clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _export_log(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
            initialfile=f"trae_reset_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.log_box.get("1.0", "end"))
            self._log(f"已导出: {path}", "ok")
        except Exception as e:
            self._log(f"导出失败: {e}", "err")

    def _set_btns(self, on: bool):
        st = "normal" if on else "disabled"
        for b in self.action_btns:
            try:
                b.configure(state=st)
            except Exception:
                pass

    def _update_license_card(self):
        """更新 4 张信息卡片的值"""
        if not self.license_data:
            return
        d = self.license_data
        # 卡密脱敏
        full = d.get("card_key", "")
        if len(full) > 8:
            masked = full[:4] + "****" + full[-4:]
        else:
            masked = "****"
        # 剩余有效期
        exp = d.get("expire_date", "永久")
        days_left = "永久"
        if exp and exp != "永久":
            try:
                exp_date = datetime.strptime(exp, "%Y-%m-%d").date()
                delta = (exp_date - date.today()).days
                days_left = f"{delta} 天" if delta > 0 else "已过期"
            except Exception:
                days_left = str(exp)

        bound = d.get("bound_devices", 0)
        max_d = d.get("max_devices", 1)
        card_type = d.get("card_type", "普通")

        values = {
            "授权卡密": masked,
            "卡密类型": card_type.upper() if card_type else "普通",
            "设备绑定": f"{bound} / {max_d}",
            "剩余有效期": days_left,
        }
        for label, val in values.items():
            canv = self.card_labels.get(label)
            if canv and hasattr(canv, "_card_value"):
                canv._card_value = val
                self._redraw_gradient_card(canv)

    def _set_status_badge(self, status: str, text: str = None):
        colors = {
            "ok":     (BADGE_OK_BG,   BADGE_OK_FG),
            "offline":(BADGE_WARN_BG, BADGE_WARN_FG),
            "warn":   (BADGE_WARN_BG, BADGE_WARN_FG),
            "err":    (BADGE_ERR_BG,  BADGE_ERR_FG),
            "info":   (BADGE_INFO_BG, BADGE_INFO_FG),
        }
        bg, fg = colors.get(status, (BADGE_INFO_BG, BADGE_INFO_FG))
        prefix = {"ok": "✓ ", "offline": "● ", "warn": "⚠ ",
                  "err": "✗ ", "info": "● "}.get(status, "● ")
        if text is None:
            text = {"ok": "已授权", "offline": "离线模式",
                    "warn": "警告", "err": "未授权"}.get(status, "")
        self.status_badge.configure(text=prefix + text,
                                     fg_color=bg, text_color=fg)

    def _do_refresh(self, silent=False):
        if not self.current_dir:
            if not silent:
                self._log("请先选择数据目录", "warn")
            return
        s = get_status(self.current_dir)
        self.info_labels["mid"].configure(text=s["machine_id"])
        self.info_labels["did"].configure(text=s["dev_device_id"])
        if not silent:
            self._log(f"状态已刷新 · 账号数: {len(s['accounts'])}", "dim")

    def _check(self) -> bool:
        if not self.current_dir:
            messagebox.showwarning("提示", "请先选择数据目录")
            return False
        if is_trae_running():
            if self.opt_kill.get():
                if messagebox.askyesno(
                        "Trae 正在运行",
                        "检测到 Trae 进程在运行，是否自动结束？"):
                    ok, msg = kill_trae_process()
                    self._log(msg, "ok" if ok else "err")
                    if not ok:
                        return False
                    time.sleep(0.5)
                    if is_trae_running():
                        messagebox.showwarning("仍运行中", "无法结束 Trae 进程")
                        return False
                else:
                    return False
            else:
                h = ("右键任务栏 Trae 图标 → 退出\n或在任务管理器中结束进程"
                     if IS_WIN else "菜单栏 Trae → Quit\n或终端 killall Trae")
                messagebox.showwarning("Trae 正在运行",
                                       f"请先关闭 Trae 再操作。\n\n{h}")
                return False
        return True

    # ─── 心跳回调 ─────────────────────────────────────────────

    def on_heartbeat_ok(self, resp: Dict):
        self.offline_mode = False
        self._set_status_badge("ok", f"已授权 · v{VERSION}")
        # 更新本地缓存的 last_check
        if self.license_data:
            self.store.save_license(self.license_data)

    def on_heartbeat_fail(self, resp: Dict, action: str):
        msg = resp.get("message", "心跳失败")
        self._log(f"心跳: {msg}", "warn")
        if action != "exit":
            self._set_status_badge("warn", f"心跳异常 · v{VERSION}")

    def on_heartbeat_network_error(self, err: str):
        # 网络错误不强制下线，进入离线宽限
        now = time.time()
        if now - self.last_heartbeat_warn > 300:
            self._log(f"心跳网络异常: {err}（已进入离线宽限）", "warn")
            self.last_heartbeat_warn = now
            self.offline_mode = True
            self._set_status_badge("offline", f"离线模式 · v{VERSION}")

    def force_logout(self):
        self._log("卡密已失效，强制下线", "err")
        self.store.clear()
        if self.heartbeat_thread:
            self.heartbeat_thread.stop()
            self.heartbeat_thread = None
        self.license_data = None
        self.offline_mode = False
        self.main_frame.pack_forget()
        self._show_login()
        messagebox.showerror("已下线", "卡密已失效或被禁用，请重新登录")

    # ─── 按钮回调 ─────────────────────────────────────────────

    def _on_auto_detect(self, silent=False):
        candidates = auto_detect_trae_dirs()
        if not candidates:
            if not silent:
                self._log("未检测到任何 Trae 目录", "warn")
                self._log(f"请点击「手动选择」指定目录（通常位于 {DIR_HINT}）", "warn")
            self.dir_combobox.configure(values=["（未检测到）"])
            self.dir_combobox.set("（未检测到，请手动选择）")
            return
        display = [p for p in candidates]
        self.dir_combobox.configure(values=display)
        # 自动选第一个
        first = candidates[0]
        self.dir_combobox.set(first)
        self.current_dir = first
        self.dir_label.configure(text=first, text_color=FG)
        if not silent:
            self._log(f"检测到 {len(candidates)} 个候选目录，已自动选中：")
            for i, p in enumerate(candidates, 1):
                self._log(f"  {i}. {p}", "dim")
            self._log(f"已选择: {first}", "ok")
        else:
            self._log(f"已自动检测: {first}", "ok")
        self._do_refresh(silent=True)

    def _on_combobox_select(self, value: str):
        if not value or value.startswith("（"):
            return
        if not is_valid_trae_dir(value):
            messagebox.showwarning("目录无效", f"未找到 machineid 或 storage.json")
            return
        self.current_dir = value
        self.dir_label.configure(text=value, text_color=FG)
        self._log(f"切换目录: {value}")
        self._do_refresh()

    def _on_browse(self):
        p = filedialog.askdirectory(title="选择 Trae 数据目录")
        if not p:
            return
        if not is_valid_trae_dir(p):
            messagebox.showwarning("目录无效",
                f"未找到 machineid 或 storage.json\n\n通常位于:\n{DIR_HINT}")
            return
        self.current_dir = p
        self.dir_label.configure(text=p, text_color=FG)
        self._log(f"手动选择: {p}")
        self._do_refresh()

    def _on_refresh(self):
        self._do_refresh()

    def _on_clear(self):
        if not self._check():
            return
        if not messagebox.askyesno("确认清除",
                "确定清除所有已登录账号？\n\n将删除 Token、Cookies 等登录信息。"):
            return
        self._set_btns(False)
        self._log("清除账号...")
        try:
            logs, cnt = clear_accounts(self.current_dir)
            for l in logs:
                self._log(l)
            self._log("清除完成" if cnt > 0 else "没有需要清除的内容",
                       "ok" if cnt > 0 else "warn")
            self._do_refresh(silent=True)
        except PermissionError:
            self._log("权限不足", "err")
        except Exception as e:
            self._log(f"错误: {e}", "err")
        finally:
            self._set_btns(True)

    def _on_reset(self):
        if not self._check():
            return
        if not messagebox.askyesno("确认重置",
                "确定重置设备 ID？\n\n将生成全新的设备标识。"):
            return
        self._set_btns(False)
        self._log("重置设备 ID...")
        # 先恢复可写（避免上次设了只读）
        make_storage_writable(self.current_dir)
        try:
            logs, ok = reset_device_id(self.current_dir)
            for l in logs:
                self._log(l)
            if ok:
                mid = read_machineid(self.current_dir)
                vok, vmsg = verify_write(self.current_dir, mid)
                if vok:
                    self._log("写入验证通过", "ok")
                else:
                    self._log(f"写入验证失败: {vmsg}", "err")
                # 只读
                if self.opt_readonly.get():
                    rok, rmsg = make_storage_readonly(self.current_dir)
                    self._log(rmsg, "ok" if rok else "warn")
                # 禁用更新
                if self.opt_disable_update.get():
                    dok, dmsg = disable_trae_autoupdate()
                    self._log(dmsg, "ok" if dok else "warn")
                self._do_refresh(silent=True)
            else:
                self._log("重置失败，已回滚", "err")
        except PermissionError:
            self._log("权限不足", "err")
        except Exception as e:
            self._log(f"错误: {e}", "err")
        finally:
            self._set_btns(True)

    def _on_oneclick(self):
        if not self._check():
            return
        # 5 秒倒计时确认
        if not messagebox.askyesno(
                "确认一键重置",
                "将执行:\n  1. 清除所有已登录账号\n  2. 重置设备 ID（含 .updaterId / 注册表）\n\n"
                + ("  3. 自动结束 Trae 进程\n" if self.opt_kill.get() else "")
                + ("  4. 重置后设为只读\n" if self.opt_readonly.get() else "")
                + ("  5. 禁用 Trae 自动更新\n" if self.opt_disable_update.get() else "")
                + "\n适用于「设备数量已达上限」，确定继续？"):
            return
        self._set_btns(False)
        # 倒计时按钮显示
        self._start_countdown(5)

    def _start_countdown(self, n: int):
        """重置按钮 5 秒倒计时"""
        if n <= 0:
            self._btn_oneclick.configure(text="正在重置...")
            self._do_oneclick()
            return
        self._btn_oneclick.configure(text=f"请稍候 {n} 秒后开始重置...")
        self.countdown_job = self.after(1000, lambda: self._start_countdown(n - 1))

    def _do_oneclick(self):
        self._log("━" * 36)
        self._log("  一键重置开始")
        self._log("━" * 36)
        try:
            # 恢复可写
            make_storage_writable(self.current_dir)
            self._log("[1/2] 清除账号...")
            logs, _ = clear_accounts(self.current_dir)
            for l in logs:
                self._log(l)
            self._log("[2/2] 重置设备 ID...")
            logs, ok = reset_device_id(self.current_dir)
            for l in logs:
                self._log(l)
            if ok:
                mid = read_machineid(self.current_dir)
                vok, vmsg = verify_write(self.current_dir, mid)
                self._log("━" * 36)
                if vok:
                    self._log("  一键重置完成，文件验证通过", "ok")
                    self._log("  现在可以打开 Trae 登录新账号了", "ok")
                else:
                    self._log(f"  重置完成但验证异常: {vmsg}", "warn")
                # 只读
                if self.opt_readonly.get():
                    rok, rmsg = make_storage_readonly(self.current_dir)
                    self._log(rmsg, "ok" if rok else "warn")
                # 禁用更新
                if self.opt_disable_update.get():
                    dok, dmsg = disable_trae_autoupdate()
                    self._log(dmsg, "ok" if dok else "warn")
                self._log("━" * 36)
                self._do_refresh(silent=True)
            else:
                self._log("━" * 36)
                self._log("  重置失败，已回滚", "err")
                self._log("━" * 36)
        except PermissionError:
            self._log("权限不足，请以管理员身份运行", "err")
        except Exception as e:
            self._log(f"错误: {e}", "err")
        finally:
            self._set_btns(True)
            self._btn_oneclick.configure(
                text="一键重置  —  清除账号 + 重置设备 ID")

    def _on_restore(self):
        if not self.current_dir:
            messagebox.showwarning("提示", "请先选择数据目录")
            return
        if is_trae_running():
            messagebox.showwarning("Trae 正在运行", "请先关闭 Trae。")
            return
        if not messagebox.askyesno("确认恢复",
                "从 .bak 备份恢复到操作前的状态？\n仅能恢复最近一次。"):
            return
        self._set_btns(False)
        self._log("恢复备份...")
        # 恢复可写
        make_storage_writable(self.current_dir)
        try:
            logs, cnt = restore_backup(self.current_dir)
            for l in logs:
                self._log(l)
            self._log("恢复完成" if cnt > 0 else "没有可恢复的备份",
                       "ok" if cnt > 0 else "warn")
            self._do_refresh(silent=True)
        except Exception as e:
            self._log(f"恢复失败: {e}", "err")
        finally:
            self._set_btns(True)

    def _restart_admin(self):
        if restart_as_admin():
            self.destroy()
            sys.exit(0)
        else:
            messagebox.showerror("失败", "无法以管理员身份重启")


# ─── 启动 ──────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        app = MainApp()
        app.mainloop()
    except Exception:
        err = traceback.format_exc()
        try:
            messagebox.showerror("启动失败", f"程序异常:\n{err}")
        except Exception:
            pass
        sys.exit(1)
