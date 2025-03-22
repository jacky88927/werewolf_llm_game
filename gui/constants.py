# 定義常數
AVAILABLE_MODELS = {
    "openai": [
        "gpt-4o-mini",
        "gpt-4o",
        "gpt-4-turbo",
        "gpt-4-32k",
        "gpt-3.5-turbo"
    ],
    "anthropic": [
        "claude-3-opus-20240229",
        "claude-3-sonnet-20240229",
        "claude-3-haiku-20240307",
        "claude-3.5-sonnet",
        "claude-3.7-sonnet"
    ]
}

AVAILABLE_ROLES = [
    "seer",       # 預言家
    "witch",      # 女巫
    "hunter",     # 獵人
    "guard",      # 守衛
    "fool",       # 白痴
    "elder",      # 長老
    "wolfkiller", # 狼殺手
    "medium",     # 通靈師
    "magician"    # 魔術師
]

# 角色圖示映射
ROLE_ICONS = {
    "villager": "icons/villager.png",
    "werewolf": "icons/werewolf.png",
    "seer": "icons/seer.png",
    "witch": "icons/witch.png",
    "hunter": "icons/hunter.png",
    "guard": "icons/guard.png",
    "fool": "icons/fool.png",
    "elder": "icons/elder.png",
    "wolfkiller": "icons/wolfkiller.png",
    "medium": "icons/medium.png",
    "magician": "icons/magician.png"
}

# 顏色主題
COLORS = {
    "primary": "#3f51b5",     # 主要深藍色
    "primary_light": "#757de8",
    "primary_dark": "#002984",
    "secondary": "#ff9800",   # 醒目的橙色
    "background": "#f5f5f5",  # 淺灰色背景
    "card": "#ffffff",        # 卡片白色
    "text": "#212121",        # 主要文字
    "text_secondary": "#757575", # 次要文字
    "error": "#f44336",       # 錯誤紅色
    "success": "#4caf50",     # 成功綠色
    "warning": "#ff9800",     # 警告橙色
    "info": "#2196f3",        # 信息藍色
    "werewolf": "#b71c1c",    # 狼人紅色
    "villager": "#1b5e20",    # Al村民綠色
    "night": "#303f9f",       # 夜晚藍色
    "day": "#ffb74d"          # 白天黃色
}
