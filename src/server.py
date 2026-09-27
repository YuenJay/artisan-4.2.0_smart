"""
Snap7 Server 示例：在 DB1.DBD0 (VD0) 写入 float，在 DB1.DBW50 (VW50) 写入 int
"""
import time
import struct
from ctypes import c_char
from snap7.server import Server
from snap7.type import SrvArea

# --- 1. 准备数据块 ---
DB_NUMBER = 1
DB_SIZE = 100

db_data = bytearray(DB_SIZE)
db_array = (c_char * DB_SIZE).from_buffer(db_data)

# --- 2. 创建并注册 DB1 ---
server = Server()
server.register_area(SrvArea.DB, DB_NUMBER, db_array)

# --- 3. 写入辅助函数 ---
def write_float(offset: int, value: float) -> None:
    """把 float 写入 DB 的指定偏移（大端序）"""
    db_data[offset:offset + 4] = struct.pack('>f', value)

def write_int(offset: int, value: int) -> None:
    """把 16 位有符号整数写入 DB 的指定偏移（大端序）"""
    db_data[offset:offset + 2] = struct.pack('>h', value)

def read_int(offset: int) -> int:
    """从 DB 指定偏移读取 16 位有符号整数"""
    return struct.unpack('>h', db_data[offset:offset + 2])[0]

def read_float(offset: int) -> float:
    """从 DB 指定偏移读取 float"""
    return struct.unpack('>f', db_data[offset:offset + 4])[0]

# 初始值
write_float(0, 123.45)   # VD0
write_int(50, 1000)      # VW50

# --- 4. 启动服务器 ---
server.start(tcp_port=1102)
print("S7 Server 已启动，监听 127.0.0.1:1102")
print(f"初始值: VD0={read_float(0):.2f}, VW50={read_int(50)}")

# --- 5. 持续更新并打印 ---
try:
    t = 0.0
    while True:
        # 模拟温度变化：150 附近波动
        value = 150.0 + 30.0 * (t % 10) / 10.0
        write_float(0, value)
        write_int(50, round(value/3))	

        print(f"VD0={read_float(0):7.2f}   VW50={read_int(50):5d}")

        time.sleep(1.0)
        t += 1.0
except KeyboardInterrupt:
    print("\n停止服务器...")
    server.stop()
    server.destroy()
