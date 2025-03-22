import customtkinter as ctk
from typing import Dict, Any, List

from .constants import COLORS
from .theme import ThemeStyles

class GamePanel(ctk.CTkFrame):
    """游戲狀態面板，顯示當前游戲狀態和玩家信息"""
    
    def __init__(self, master, **kwargs):
        """初始化游戲狀態面板
        
        Args:
            master: 父窗口
            **kwargs: 額外參數傳給父類
        """
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        
        # 創建狀態變量
        self.day_var = ctk.StringVar(value="Day 0")
        self.phase_var = ctk.StringVar(value="游戲未開始")
        self.alive_status_var = ctk.StringVar(value="狼人: 0 | 村民: 0")
        self.game_status_var = ctk.StringVar(value="游戲狀態: 未開始")
        
        # 創建界面元素
        self._create_status_panel()
    
    def _create_status_panel(self):
        """創建游戲狀態面板"""
        status_frame = ctk.CTkFrame(self, **ThemeStyles.card_frame())
        status_frame.pack(fill="x", padx=10, pady=10)
        
        # 使用网格布局来安排状态信息
        for i in range(3):
            status_frame.grid_columnconfigure(i, weight=1)
        
        # 游戏日/夜显示
        day_label = ctk.CTkLabel(
            status_frame, 
            textvariable=self.day_var, 
            font=("Arial", 16, "bold"),
            text_color=COLORS["primary"]
        )
        day_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        # 游戏阶段显示
        phase_label = ctk.CTkLabel(
            status_frame, 
            textvariable=self.phase_var,
            font=("Arial", 16)
        )
        phase_label.grid(row=0, column=1, padx=10, pady=10)
        
        # 存活状态显示
        alive_label = ctk.CTkLabel(
            status_frame, 
            textvariable=self.alive_status_var,
            font=("Arial", 14, "bold"),
            text_color=COLORS["primary"]
        )
        alive_label.grid(row=0, column=2, padx=10, pady=10, sticky="e")
        
        # 游戏状态文字
        status_text = ctk.CTkLabel(
            status_frame, 
            textvariable=self.game_status_var,
            font=("Arial", 12)
        )
        status_text.grid(row=1, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")
    
    def update_status(self, day: str = None, phase: str = None, 
                      alive: str = None, status: str = None):
        """更新游戲狀態
        
        Args:
            day (str, optional): 當前天數
            phase (str, optional): 當前階段
            alive (str, optional): 存活狀態
            status (str, optional): 游戲狀態
        """
        if day is not None:
            self.day_var.set(day)
        if phase is not None:
            self.phase_var.set(phase)
        if alive is not None:
            self.alive_status_var.set(alive)
        if status is not None:
            self.game_status_var.set(status)
    
    def reset_status(self):
        """重置游戲狀態為默認值"""
        self.day_var.set("Day 0")
        self.phase_var.set("游戲未開始")
        self.alive_status_var.set("狼人: 0 | 村民: 0")
        self.game_status_var.set("游戲狀態: 未開始")
    
    def update_from_summary(self, summary: Dict[str, Any]):
        """從游戲摘要更新狀態
        
        Args:
            summary (Dict[str, Any]): 游戲摘要
        """
        self.day_var.set(f"Day {summary.get('day', 0)}")
        self.phase_var.set(summary.get('phase', '未知'))
        
        # 更新存活狀態
        alive_werewolves = summary.get('alive_werewolves', 0)
        alive_villagers = summary.get('alive_villagers', 0)
        self.alive_status_var.set(f"狼人: {alive_werewolves} | 村民: {alive_villagers}")
        
        # 更新游戲狀態
        if summary.get('game_over', False):
            self.game_status_var.set(f"游戲狀態: 已結束 - {summary.get('winner', '無')}獲勝")
        else:
            self.game_status_var.set("游戲狀態: 進行中")
