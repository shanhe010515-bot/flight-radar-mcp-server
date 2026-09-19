# 航班雷达 MCP Server ✈️

一个基于 **FastMCP** 和 **OpenSky Network API** 构建的实时飞机雷达 MCP 服务器。

该服务器通过 MCP 协议向客户端提供实时航空数据查询能力，可以获取飞机位置、高度、速度、航向等信息，并提供基于实时数据的飞机分析功能。

---

# 项目功能

本 MCP Server 提供以下工具：

## 1. scan_airspace

扫描指定经纬度范围内的实时飞机。

可以获取：

- 飞机 ICAO24 标识
- 航班呼号（Callsign）
- 国家
- 经纬度位置
- 飞行高度
- 飞行速度
- 飞行方向


示例：

```
查询纬度 33-35，经度 -119 到 -117 区域内的飞机
```

---

## 2. get_aircraft_state

根据飞机 ICAO24 标识查询指定飞机的实时状态。

例如：

```
查询 ICAO24:
ad4454
```

返回：

- 飞机编号
- 呼号
- 当前国家
- 位置
- 高度
- 速度
- 航向

---

## 3. find_aircraft_by_callsign

根据航班呼号搜索飞机。

例如：

```
查询 VOI1813
```

返回对应飞机的实时状态信息。

---

## 4. get_nearest_aircraft

根据指定坐标查找距离最近的飞机。

输入：

- 纬度
- 经度

返回：

- 最近飞机信息
- 飞机距离目标位置的距离


---

## 5. get_highest_aircraft

查询指定空域内飞行高度最高的飞机。

返回：

- 飞机信息
- 当前高度


---

## 6. get_fastest_aircraft

查询指定空域内速度最快的飞机。

返回：

- 飞机信息
- 当前速度


---

# 系统架构

```
          MCP Client

              |

              |

     Flight Radar MCP Server

              |

              |

          FastMCP Tools

              |

              |

       OpenSky Network API

              |

              |

        实时飞机数据
```

---

# 技术栈

- Python
- FastMCP
- MCP Protocol
- OpenSky Network API
- Docker

---

# 安装方法

克隆项目：

```bash
git clone https://github.com/你的用户名/flight-radar-mcp-server.git

cd flight-radar-mcp-server
```

安装依赖：

```bash
pip install -r requirements.txt
```

---

# 环境变量配置

创建 `.env` 文件：

```env
OPENSKY_CLIENT_ID=你的OpenSky客户端ID
OPENSKY_CLIENT_SECRET=你的OpenSky客户端密钥
```

说明：

- `OPENSKY_CLIENT_ID`
- `OPENSKY_CLIENT_SECRET`

用于访问 OpenSky API。

注意：

`.env` 文件包含敏感信息，不应上传到 GitHub。

---

# 本地运行

启动 MCP Server：

```bash
python server.py
```

启动后，MCP Client 可以连接该服务器并调用提供的工具。

---

# Docker 部署

构建镜像：

```bash
docker build -t flight-radar-mcp-server .
```

运行：

```bash
docker run \
-p 8081:8081 \
-e OPENSKY_CLIENT_ID=你的ID \
-e OPENSKY_CLIENT_SECRET=你的密钥 \
flight-radar-mcp-server
```

---

# MCP 工具列表

| 工具名称 | 功能 |
|---|---|
| scan_airspace | 扫描指定区域飞机 |
| get_aircraft_state | 查询指定飞机状态 |
| find_aircraft_by_callsign | 根据呼号搜索飞机 |
| get_nearest_aircraft | 查询最近飞机 |
| get_highest_aircraft | 查询最高飞机 |
| get_fastest_aircraft | 查询最快飞机 |

---

# 项目目录

```
flight-radar-mcp-server/

├── server.py             # MCP服务器核心代码
├── requirements.txt      # Python依赖
├── pyproject.toml        # 项目配置
├── Dockerfile            # Docker部署配置
├── smithery.yaml         # Smithery发布配置
├── README.md             # 项目说明
├── LICENSE               # 开源许可证
└── .gitignore            # Git忽略配置
```

---

# 数据来源

本项目使用：

OpenSky Network API

提供实时飞机 ADS-B 数据。

---

# 开源协议

MIT License