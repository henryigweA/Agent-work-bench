from datetime import datetime, timezone
import ast
import operator
from urllib.parse import quote

import requests

TIMEOUT = 15
BINARY = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow,
}
UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}

def _number(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in BINARY:
        left, right = _number(node.left), _number(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > 8:
            raise ValueError("Exponent is too large.")
        result = BINARY[type(node.op)](left, right)
        if abs(result) > 1e15:
            raise ValueError("Result is outside the supported range.")
        return result
    if isinstance(node, ast.UnaryOp) and type(node.op) in UNARY:
        return UNARY[type(node.op)](_number(node.operand))
    raise ValueError("Only basic arithmetic is supported.")

def calculate(expression: str):
    if not isinstance(expression, str) or not expression.strip() or len(expression) > 100:
        raise ValueError("Expression must contain 1-100 characters.")
    return {"expression": expression, "result": _number(ast.parse(expression, mode="eval").body)}

def get_current_time():
    now = datetime.now(timezone.utc)
    return {"timezone": "UTC", "iso": now.isoformat(),
            "readable": now.strftime("%A, %d %B %Y at %H:%M:%S UTC")}

def get_weather(city: str):
    if not isinstance(city, str) or not city.strip() or len(city) > 100:
        raise ValueError("Provide a valid city name.")
    geo_url = "https://geocoding-api.open-meteo.com/v1/search?name=" + quote(city.strip()) + "&count=1&language=en&format=json"
    geo = requests.get(geo_url, timeout=TIMEOUT)
    geo.raise_for_status()
    places = geo.json().get("results") or []
    if not places:
        return {"found": False, "message": f"No location found for {city!r}."}
    place = places[0]
    url = ("https://api.open-meteo.com/v1/forecast"
           f"?latitude={place['latitude']}&longitude={place['longitude']}"
           "&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m")
    response = requests.get(url, timeout=TIMEOUT)
    response.raise_for_status()
    data = response.json()
    return {
        "found": True,
        "location": {"name": place.get("name"), "admin1": place.get("admin1"), "country": place.get("country")},
        "current": data.get("current", {}),
        "units": data.get("current_units", {}),
        "source": "Open-Meteo",
    }

def get_github_repository(owner: str, repo: str):
    for value in (owner, repo):
        if not isinstance(value, str) or not value.strip() or len(value) > 100:
            raise ValueError("Provide a valid GitHub owner and repository.")
    url = f"https://api.github.com/repos/{quote(owner)}/{quote(repo)}"
    response = requests.get(url, headers={"Accept": "application/vnd.github+json"}, timeout=TIMEOUT)
    if response.status_code == 404:
        return {"found": False, "message": "Repository not found or not public."}
    response.raise_for_status()
    data = response.json()
    return {key: data.get(source) for key, source in {
        "name": "full_name", "description": "description", "language": "language",
        "stars": "stargazers_count", "forks": "forks_count",
        "open_issues": "open_issues_count", "url": "html_url", "updated_at": "updated_at"
    }.items()} | {"found": True}

TOOL_DEFINITIONS = [
    {"name": "calculate", "description": "Calculate basic arithmetic. Supports +, -, *, /, //, %, ** and parentheses.",
     "parameters": {"type": "OBJECT", "properties": {"expression": {"type": "STRING", "description": "Arithmetic expression"}}, "required": ["expression"]}},
    {"name": "get_current_time", "description": "Get the current date and time in UTC.",
     "parameters": {"type": "OBJECT", "properties": {}}},
    {"name": "get_weather", "description": "Get current weather conditions for a city using Open-Meteo.",
     "parameters": {"type": "OBJECT", "properties": {"city": {"type": "STRING", "description": "City name"}}, "required": ["city"]}},
    {"name": "get_github_repository", "description": "Get public metadata about a GitHub repository.",
     "parameters": {"type": "OBJECT", "properties": {
         "owner": {"type": "STRING", "description": "GitHub username or organization"},
         "repo": {"type": "STRING", "description": "Repository name"}}, "required": ["owner", "repo"]}},
]

FUNCTIONS = {
    "calculate": calculate,
    "get_current_time": get_current_time,
    "get_weather": get_weather,
    "get_github_repository": get_github_repository,
}

def run_tool(name, arguments):
    function = FUNCTIONS.get(name)
    if function is None:
        return {"ok": False, "error": f"Tool {name!r} is not registered."}
    try:
        return {"ok": True, "result": function(**arguments)}
    except (TypeError, ValueError, requests.RequestException, ZeroDivisionError) as exc:
        return {"ok": False, "error": str(exc)}
