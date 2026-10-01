# -*- coding: utf-8 -*-
"""Headless librime 部署：ctypes 调 rime.dll 维护接口（等价 WeaselDeployer /deploy）
前置：WeaselServer 已停止（避免词典文件内存映射锁）
"""
import ctypes, os, sys, time

RIME_DLL = r"C:\Program Files\Rime\weasel-0.17.4\rime.dll"
USER_DIR = r"C:\Users\Administrator\AppData\Roaming\Rime"
SHARED_DIR = r"C:\Program Files\Rime\weasel-0.17.4\data"
STAGING = os.path.join(USER_DIR, "build")
LOG_DIR = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "rime.weasel")

dll = ctypes.CDLL(RIME_DLL)

class RimeTraits(ctypes.Structure):
    _fields_ = [
        ("data_size", ctypes.c_int),
        ("shared_data_dir", ctypes.c_char_p),
        ("user_data_dir", ctypes.c_char_p),
        ("distribution_name", ctypes.c_char_p),
        ("distribution_code_name", ctypes.c_char_p),
        ("distribution_version", ctypes.c_char_p),
        ("app_name", ctypes.c_char_p),
        ("modules", ctypes.POINTER(ctypes.c_char_p)),
        ("min_log_level", ctypes.c_int),
        ("log_dir", ctypes.c_char_p),
        ("prebuilt_data_dir", ctypes.c_char_p),
        ("staging_dir", ctypes.c_char_p),
    ]

# RimeApi 前缀（rime_api.h 1.13.1 成员顺序，截到 join_maintenance_thread 为止）
class RimeApiPrefix(ctypes.Structure):
    _fields_ = [
        ("data_size", ctypes.c_int),
        ("setup", ctypes.CFUNCTYPE(None, ctypes.POINTER(RimeTraits))),
        ("set_notification_handler", ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p)),
        ("initialize", ctypes.CFUNCTYPE(None, ctypes.POINTER(RimeTraits))),
        ("finalize", ctypes.CFUNCTYPE(None)),
        ("start_maintenance", ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int)),
        ("is_maintenance_mode", ctypes.CFUNCTYPE(ctypes.c_int)),
        ("join_maintenance_thread", ctypes.CFUNCTYPE(None)),
    ]

dll.rime_get_api.restype = ctypes.POINTER(RimeApiPrefix)
api = dll.rime_get_api()
assert api and api.contents.setup, "rime_get_api failed"
api = api.contents
api.data_size = ctypes.sizeof(RimeApiPrefix)  # RIME_STRUCT_INIT 语义：覆盖到末成员即可用

t = RimeTraits()
t.data_size = ctypes.sizeof(RimeTraits)
t.shared_data_dir = SHARED_DIR.encode()
t.user_data_dir = USER_DIR.encode()
t.distribution_name = b"Weasel"
t.distribution_code_name = b"Weasel"
t.distribution_version = b"0.17.4"
t.app_name = b"rime.msxpdeploy"
t.modules = None
t.min_log_level = 0
t.log_dir = LOG_DIR.encode()
t.prebuilt_data_dir = None
t.staging_dir = STAGING.encode()

print("rime_setup ...")
api.setup(ctypes.byref(t))
print("start_maintenance(full_check=True) ...")
started = api.start_maintenance(1)
print("started =", started)
if started:
    api.join_maintenance_thread()
    print("maintenance joined (done)")
api.finalize()
print("FINALIZE OK")
