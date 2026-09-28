"""
Snap7 Server 示例：在 DB1 的 VD0/VD4/VD8/VD12 写入 float 温度，
                   在 VW50/VW52/VW54/VW56 写入 int
"""
import time
import struct
import random
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

# --- 3. 读写辅助函数 ---
def write_float(offset: int, value: float) -> None:
    """把 float 写入 DB 的指定偏移（大端序）"""
    db_data[offset:offset + 4] = struct.pack('>f', value)

def write_int(offset: int, value: int) -> None:
    """把 16 位有符号整数写入 DB 的指定偏移（大端序）"""
    value = max(-32768, min(32767, int(value)))
    db_data[offset:offset + 2] = struct.pack('>h', value)

def read_int(offset: int) -> int:
    """从 DB 指定偏移读取 16 位有符号整数"""
    return struct.unpack('>h', db_data[offset:offset + 2])[0]

def read_float(offset: int) -> float:
    """从 DB 指定偏移读取 float"""
    return struct.unpack('>f', db_data[offset:offset + 4])[0]

# 初始值
# write_float(0, 123.45)   # VD0
# write_float(4, 124.00)   # VD4
# write_float(8, 125.00)   # VD8
# write_float(12, 126.00)  # VD12
# write_int(50, 1000)      # VW50
# write_int(52, 1000)      # VW52
# write_int(54, 1000)      # VW54
# write_int(56, 1000)      # VW56

# --- 4. 启动服务器 ---
server.start(tcp_port=102)
print("S7 Server 已启动，监听 127.0.0.1:102")
# print(f"初始值: VD0={read_float(0):.2f}, VD4={read_float(4):.2f}, "
#       f"VD8={read_float(8):.2f}, VD12={read_float(12):.2f}")

# --- 5. 持续更新并打印 ---
try:
    t = 0.0
    while True:
        # 4 个温度通道，各自有不同的基线和波动
        base = 150.0 + 30.0 * (t % 10) / 10.0
        temp_et = base                      # VD0: ET
        temp_bt = base - 10.0               # VD4: BT（比 ET 低 10 度）
        temp_t3 = base + 5.0                # VD8: 第三个温度
        temp_t4 = base - 20.0               # VD12: 第四个温度

        write_float(0, temp_et)
        write_float(4, temp_bt)
        write_float(8, temp_t3)
        write_float(12, temp_t4)

        # # 每 5 秒更新一次 4 个 int
        # if int(t) % 5 == 0:
        #     write_int(50, round(temp_et / 3))
        #     write_int(52, round(temp_bt / 3 + random.randint(-5, 5)))
        #     write_int(54, round(temp_t3 / 3 + random.randint(-3, 3)))
        #     write_int(56, round(temp_t4 / 3 + random.randint(-2, 2)))

        print(f"VD0={read_float(0):7.2f}  VD4={read_float(4):7.2f}  "
              f"VD8={read_float(8):7.2f}  VD12={read_float(12):7.2f}  |  "
              f"VW50={read_int(50):5d}  VW52={read_int(52):5d}  "
              f"VW54={read_int(54):5d}  VW56={read_int(56):5d}")

        time.sleep(1.0)
        t += 1.0
except KeyboardInterrupt:
    print("\n停止服务器...")
    server.stop()
    server.destroy()