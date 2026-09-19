import os
import time
import math
import requests

from dotenv import load_dotenv
from fastmcp import FastMCP


# =========================
# 1. 读取 OpenSky 凭据
# =========================

load_dotenv()

CLIENT_ID = os.getenv("OPENSKY_CLIENT_ID")
CLIENT_SECRET = os.getenv("OPENSKY_CLIENT_SECRET")

TOKEN_URL = (
    "https://auth.opensky-network.org/"
    "auth/realms/opensky-network/"
    "protocol/openid-connect/token"
)

STATES_URL = "https://opensky-network.org/api/states/all"


# =========================
# 2. 创建 MCP Server
# =========================

mcp = FastMCP("Flight Radar MCP")


# =========================
# 3. Token 缓存
# =========================

_access_token = None
_token_expire_time = 0


def get_token():
    """获取 OpenSky Token，并进行简单缓存"""

    global _access_token
    global _token_expire_time

    # Token 还没过期，直接继续用
    if _access_token and time.time() < _token_expire_time:
        return _access_token

    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    _access_token = data["access_token"]

    # 提前60秒当作过期
    _token_expire_time = (
        time.time()
        + data.get("expires_in", 1800)
        - 60
    )

    return _access_token


# =========================
# 4. OpenSky 通用请求函数
# =========================

def fetch_states(params=None):

    token = get_token()

    response = requests.get(
        STATES_URL,
        headers={
            "Authorization": f"Bearer {token}"
        },
        params=params or {},
        timeout=20
    )

    response.raise_for_status()

    return response.json().get("states", []) or []


# =========================
# 5. 把 OpenSky 原始数组整理成人能看懂的字典
# =========================

def parse_plane(plane):

    velocity = plane[9]

    return {
        "icao24": plane[0],

        "callsign": (
            plane[1].strip()
            if plane[1]
            else "未知"
        ),

        "country": plane[2],

        "longitude": plane[5],
        "latitude": plane[6],

        "altitude_m": plane[7],

        "on_ground": plane[8],

        "velocity_m_s": velocity,

        "velocity_km_h": (
            round(velocity * 3.6, 1)
            if velocity is not None
            else None
        ),

        "heading_deg": plane[10],

        "vertical_rate_m_s": plane[11]
    }


# =========================
# Tool 1：扫描一片空域
# =========================

@mcp.tool
def scan_airspace(
    lamin: float,
    lomin: float,
    lamax: float,
    lomax: float,
    limit: int = 50
) -> list:
    """
    扫描指定经纬度矩形区域中的实时飞机。

    lamin: 最小纬度
    lomin: 最小经度
    lamax: 最大纬度
    lomax: 最大经度
    limit: 最多返回多少架飞机
    """

    states = fetch_states({
        "lamin": lamin,
        "lomin": lomin,
        "lamax": lamax,
        "lomax": lomax
    })

    return [
        parse_plane(plane)
        for plane in states[:limit]
    ]


# =========================
# Tool 2：根据 ICAO24 查飞机
# =========================

@mcp.tool
def get_aircraft_state(icao24: str) -> dict:
    """
    根据飞机的 ICAO24 唯一标识查询实时状态。
    例如：ad4454
    """

    states = fetch_states({
        "icao24": icao24.lower()
    })

    if not states:
        return {
            "error": "没有找到这架飞机",
            "icao24": icao24
        }

    return parse_plane(states[0])


# =========================
# Tool 3：根据呼号找飞机
# =========================

@mcp.tool
def find_aircraft_by_callsign(
    callsign: str,
    lamin: float,
    lomin: float,
    lamax: float,
    lomax: float
) -> list:
    """
    在指定空域中根据呼号搜索飞机。
    例如：VOI1813、AMX057。
    """

    callsign = callsign.strip().upper()

    states = fetch_states({
        "lamin": lamin,
        "lomin": lomin,
        "lamax": lamax,
        "lomax": lomax
    })

    matches = []

    for plane in states:

        plane_callsign = (
            plane[1].strip().upper()
            if plane[1]
            else ""
        )

        if callsign in plane_callsign:
            matches.append(parse_plane(plane))

    if not matches:
        return [{
            "error": f"没有找到呼号 {callsign}"
        }]

    return matches


# =========================
# 距离计算函数
# =========================

def calculate_distance(
    lat1,
    lon1,
    lat2,
    lon2
):
    """Haversine公式，返回公里"""

    earth_radius = 6371

    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return earth_radius * c


# =========================
# Tool 4：找最近的飞机
# =========================

@mcp.tool
def get_nearest_aircraft(
    latitude: float,
    longitude: float,
    search_range: float = 1.0
) -> dict:
    """
    查询距离指定坐标最近的飞机。

    search_range:
    经纬度搜索范围，默认上下左右各1度。
    """

    states = fetch_states({
        "lamin": latitude - search_range,
        "lamax": latitude + search_range,
        "lomin": longitude - search_range,
        "lomax": longitude + search_range
    })

    candidates = []

    for plane in states:

        plane_lon = plane[5]
        plane_lat = plane[6]

        if plane_lon is None or plane_lat is None:
            continue

        distance = calculate_distance(
            latitude,
            longitude,
            plane_lat,
            plane_lon
        )

        info = parse_plane(plane)

        info["distance_km"] = round(
            distance,
            2
        )

        candidates.append(info)

    if not candidates:
        return {
            "error": "附近没有发现飞机"
        }

    return min(
        candidates,
        key=lambda x: x["distance_km"]
    )


# =========================
# Tool 5：找飞得最高的飞机
# =========================

@mcp.tool
def get_highest_aircraft(
    lamin: float,
    lomin: float,
    lamax: float,
    lomax: float
) -> dict:
    """
    查询指定空域中飞行高度最高的飞机。
    """

    states = fetch_states({
        "lamin": lamin,
        "lomin": lomin,
        "lamax": lamax,
        "lomax": lomax
    })

    planes = [
        parse_plane(plane)
        for plane in states
        if plane[7] is not None
    ]

    if not planes:
        return {
            "error": "该区域没有有效高度数据"
        }

    return max(
        planes,
        key=lambda x: x["altitude_m"]
    )


# =========================
# Tool 6：找飞得最快的飞机
# =========================

@mcp.tool
def get_fastest_aircraft(
    lamin: float,
    lomin: float,
    lamax: float,
    lomax: float
) -> dict:
    """
    查询指定空域中速度最快的飞机。
    """

    states = fetch_states({
        "lamin": lamin,
        "lomin": lomin,
        "lamax": lamax,
        "lomax": lomax
    })

    planes = [
        parse_plane(plane)
        for plane in states
        if plane[9] is not None
    ]

    if not planes:
        return {
            "error": "该区域没有有效速度数据"
        }

    return max(
        planes,
        key=lambda x: x["velocity_m_s"]
    )


# =========================
# 启动 MCP Server
# =========================

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8081"))

    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=port
    )