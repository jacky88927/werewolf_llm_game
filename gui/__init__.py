# GUI 包初始化
from .constants import AVAILABLE_MODELS, AVAILABLE_ROLES, ROLE_ICONS, COLORS
from .theme import setup_theme, ThemeStyles

# 在導入其他模塊之前，先確保基礎模塊已經導入
try:
    from .settings_panel import SettingsPanel
    from .game_panel import GamePanel
    from .log_panel import LogPanel
    from .app import WerewolfApp
except ImportError as e:
    print(f"GUI 初始化錯誤: {e}")
