import asyncio
from concurrent.futures import ThreadPoolExecutor

from ping3 import ping

# 定义要测试的地址列表
addresses = [
    "114.114.114.114",
    "114.114.114.115",  # 备用
    "223.5.5.5",
    "233.6.6.6",  # 备用
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1",
    "1.0.0.1",
    "9.9.9.9",
    "149.112.112.112",
    "94.140.14.14",
    "94.140.15.15",
    "45.90.28.0",
    "45.90.30.0",
    "208.67.222.222",
    "208.67.220.220",
    "77.88.8.8",
    "77.88.8.1",
    "185.228.168.9",
    "185.228.169.9",
    "172.104.93.80",
    "8.26.56.26",
    "84.200.69.80",
    "46.250.226.242",
    "2407:3640:2205:1668::1",
    "185.228.168.9",
    "185.228.169.9",
    "76.76.2.1",
    "78.47.212.211",
]


# 定义 Ping 测试函数
def test_ping(address):
    try:
        latency = ping(address, timeout=2)  # 设置超时时间为 2 秒
        if latency is not None:
            return address, f"{round(latency * 1000, 2)}ms"  # 将秒转换为毫秒
        else:
            return address, "Failed"
    except Exception as e:
        return address, f"Error: {e}"


# 并发执行 Ping 测试
async def run_concurrent_ping():
    with ThreadPoolExecutor(max_workers=20) as executor:  # 设置最大并发数为 20
        loop = asyncio.get_event_loop()
        futures = [
            loop.run_in_executor(executor, test_ping, address) for address in addresses
        ]
        results = await asyncio.gather(*futures)
        return results


# 主函数
async def main():
    print("Starting Ping tests...")
    results = await run_concurrent_ping()
    print("\nPing results:")
    print("-" * 40)
    print(f"{'Address':<20} {'Latency (ms)':<10}")
    print("-" * 40)
    for address, latency in results:
        print(f"{address:<20} {latency:<10}")


# 运行主函数
if __name__ == "__main__":
    asyncio.run(main())
