import asyncio
from pathlib import Path

from fastmcp import Client


async def main():

    # 连接本地 MCP Server
    client = Client(
        Path("flight_radar_server.py")
    )

    async with client:

        print("✅ 已连接 Flight Radar MCP Server\n")

        # =========================
        # 1. 获取服务器所有工具
        # =========================

        tools = await client.list_tools()

        print(f"发现 {len(tools)} 个 MCP Tool：\n")

        for tool in tools:

            print("=" * 60)

            print("工具名称：")
            print(tool.name)

            print("\n工具描述：")
            print(tool.description)

            print("\n参数 Schema：")
            print(tool.inputSchema)

        print("=" * 60)


if __name__ == "__main__":

    asyncio.run(main())