import customtkinter as ctk
from PIL import Image, ImageTk
import os
from tkinter import messagebox
from typing import Dict, Callable, List, Any

from .constants import AVAILABLE_MODELS, AVAILABLE_ROLES, ROLE_ICONS, COLORS
from .theme import ThemeStyles

class SettingsPanel(ctk.CTkFrame):
    """設置面板，包含游戲配置，角色選擇和API設置"""
    
    def __init__(self, master, width=300, **kwargs):
        """初始化設置面板
        
        Args:
            master: 父窗口
            width: 面板寬度
            **kwargs: 額外參數傳給父類
        """
        super().__init__(master, width=width, fg_color=COLORS["background"], **kwargs)
        
        # 游戲設置變量
        self.player_count_var = ctk.IntVar(value=6)
        self.werewolf_count_var = ctk.IntVar(value=2)
        self.special_roles_vars = {}  # 特殊角色選擇變量
        self.max_days_var = ctk.IntVar(value=10)
        self.api_type_var = ctk.StringVar(value="mixed")
        self.model_name_var = ctk.StringVar(value="")
        self.human_players_var = ctk.StringVar(value="")
        
        # 保存角色選擇框引用的列表
        self.role_checkboxes = []
        
        # 嘗試載入角色圖標
        self.icons = self._load_icons()
        
        # 創建界面元素
        self._create_game_settings()
        self._create_role_selection()
        self._create_api_settings()
        self._create_action_buttons()
        
        # 回調函數
        self.on_start_game = None
        self.on_load_game = None
    
    def _load_icons(self) -> Dict[str, ImageTk.PhotoImage]:
        """載入角色圖標
        
        Returns:
            Dict[str, ImageTk.PhotoImage]: 角色圖標字典
        """
        icons = {}
        
        # 載入角色圖標 (假設圖標存在於指定路徑)
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "icons")
        if os.path.exists(icons_dir):
            for role, path in ROLE_ICONS.items():
                full_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), path)
                if os.path.exists(full_path):
                    img = Image.open(full_path)
                    img = img.resize((24, 24), Image.LANCZOS)  # 調整大小
                    icons[role] = ImageTk.PhotoImage(img)
        
        return icons
    
    def _create_game_settings(self):
        """創建游戲設置區域"""
        settings_frame = ctk.CTkFrame(self, **ThemeStyles.card_frame())
        settings_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # 標題
        ctk.CTkLabel(
            settings_frame, 
            text="游戲設置", 
            **ThemeStyles.header_label()
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # 玩家數量設置
        player_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        player_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            player_frame, 
            text="玩家數量:", 
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        player_count_spin = ctk.CTkEntry(
            player_frame, 
            width=60,
            textvariable=self.player_count_var
        )
        player_count_spin.pack(side="right")
        
        # 預設玩家數按鈕
        presets_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        presets_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        for count in [6, 8, 10, 12]:
            btn = ctk.CTkButton(
                presets_frame, 
                text=str(count), 
                command=lambda c=count: self.player_count_var.set(c),
                width=40,
                height=25,
                **ThemeStyles.small_button()
            )
            btn.pack(side="left", padx=2)
        
        # 狼人數量設置
        wolf_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        wolf_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            wolf_frame, 
            text="狼人數量:", 
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        wolf_count_spin = ctk.CTkEntry(
            wolf_frame, 
            width=60,
            textvariable=self.werewolf_count_var
        )
        wolf_count_spin.pack(side="right")
        
        # 預設狼人數按鈕
        wolf_presets_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        wolf_presets_frame.pack(fill="x", padx=10, pady=(0, 5))
        
        for count in [1, 2, 3, 4]:
            btn = ctk.CTkButton(
                wolf_presets_frame, 
                text=str(count), 
                command=lambda c=count: self.werewolf_count_var.set(c),
                width=40,
                height=25,
                **ThemeStyles.small_button()
            )
            btn.pack(side="left", padx=2)
        
        # 最大天數設置
        days_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        days_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            days_frame, 
            text="最大天數:", 
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        max_days_spin = ctk.CTkEntry(
            days_frame, 
            width=60,
            textvariable=self.max_days_var
        )
        max_days_spin.pack(side="right", pady=(0, 10))
    
    def _create_role_selection(self):
        """創建角色選擇區域"""
        roles_frame = ctk.CTkFrame(self, **ThemeStyles.card_frame())
        roles_frame.pack(fill="x", padx=10, pady=5)
        
        # 標題
        ctk.CTkLabel(
            roles_frame, 
            text="特殊角色選擇", 
            **ThemeStyles.header_label()
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # 角色選擇區域
        roles_grid = ctk.CTkFrame(roles_frame, fg_color="transparent")
        roles_grid.pack(fill="x", padx=10, pady=5)
        
        # 配置網格
        for i in range(3):
            roles_grid.grid_columnconfigure(i, weight=1)
        
        # 為每一個角色創建選擇框
        for i, role in enumerate(AVAILABLE_ROLES):
            # 為了使界面更美觀，每行放3個角色
            row, col = i // 3, i % 3
            
            self.special_roles_vars[role] = ctk.BooleanVar(value=role == "seer")
            
            role_frame = ctk.CTkFrame(roles_grid, fg_color="transparent")
            role_frame.grid(row=row, column=col, sticky="w", padx=5, pady=3)
            
            # 如果有圖標則使用
            if role in self.icons:
                # 在CustomTkinter中，我們需要使用CTkImage
                role_img = ctk.CTkLabel(role_frame, image=self.icons[role], text="")
                role_img.pack(side="left", padx=(0, 2))
            
            cb = ctk.CTkCheckBox(
                role_frame, 
                text=role, 
                variable=self.special_roles_vars[role],
                font=("Arial", 10)
            )
            cb.pack(side="left")
            self.role_checkboxes.append(cb)
        
        # 角色選擇按鈕
        buttons_frame = ctk.CTkFrame(roles_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        ctk.CTkButton(
            buttons_frame, 
            text="全選", 
            command=self._select_all_roles,
            width=70,
            height=28,
            **ThemeStyles.small_button()
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            buttons_frame, 
            text="取消全選", 
            command=self._deselect_all_roles,
            width=70,
            height=28,
            **ThemeStyles.small_button()
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame, 
            text="基本配置", 
            command=self._select_basic_roles,
            width=70,
            height=28,
            **ThemeStyles.small_button()
        ).pack(side="left", padx=5)
    
    def _create_api_settings(self):
        """創建API設置區域"""
        api_frame = ctk.CTkFrame(self, **ThemeStyles.card_frame())
        api_frame.pack(fill="x", padx=10, pady=5)
        
        # 標題
        ctk.CTkLabel(
            api_frame, 
            text="API 設置", 
            **ThemeStyles.header_label()
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # API類型
        api_type_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        api_type_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            api_type_frame, 
            text="API類型:",
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        api_values = ["mixed", "openai", "anthropic"]
        api_type_combo = ctk.CTkOptionMenu(
            api_type_frame, 
            variable=self.api_type_var, 
            values=api_values,
            width=150,
            command=self._update_model_list
        )
        api_type_combo.pack(side="right")
        
        # 模型名稱
        model_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        model_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            model_frame, 
            text="模型名稱:",
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        self.model_combo = ctk.CTkOptionMenu(
            model_frame, 
            variable=self.model_name_var,
            values=[],
            width=150,
            state="disabled"
        )
        self.model_combo.pack(side="right")
        
        # 人類玩家
        human_frame = ctk.CTkFrame(api_frame, fg_color="transparent")
        human_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            human_frame, 
            text="人類玩家:",
            font=("Arial", 12, "bold")
        ).pack(side="left")
        
        ctk.CTkEntry(
            human_frame, 
            textvariable=self.human_players_var,
            width=150
        ).pack(side="right")
        
        # 格式提示
        ctk.CTkLabel(
            api_frame, 
            text="(ID列表，逗號分隔: 1,3,5)",
            text_color=COLORS["text_secondary"],
            font=("Arial", 10)
        ).pack(anchor="e", padx=10, pady=(0, 10))
    
    def _create_action_buttons(self):
        """創建操作按鈕區域"""
        action_frame = ctk.CTkFrame(self, **ThemeStyles.card_frame())
        action_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        # 標題
        ctk.CTkLabel(
            action_frame, 
            text="操作", 
            **ThemeStyles.header_label()
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # 按鈕
        buttons_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        # 創建游戲按鈕
        start_button = ctk.CTkButton(
            buttons_frame, 
            text="創建新游戲", 
            command=self._start_game,
            **ThemeStyles.success_button()
        )
        start_button.pack(fill="x", pady=(0, 10))
        
        # 載入游戲按鈕
        load_button = ctk.CTkButton(
            buttons_frame, 
            text="載入游戲", 
            command=self._load_game,
            **ThemeStyles.normal_button()
        )
        load_button.pack(fill="x")
    
    def _update_model_list(self, event=None):
        """更新模型列表"""
        api_type = self.api_type_var.get()
        
        if api_type == "mixed":
            self.model_combo.configure(state="disabled", values=[])
            self.model_name_var.set("")
        else:
            models = AVAILABLE_MODELS.get(api_type, [])
            self.model_combo.configure(state="normal", values=models)
            if not self.model_name_var.get() and models:
                self.model_name_var.set(models[0])
    
    def _select_all_roles(self):
        """選擇所有特殊角色"""
        for role, var in self.special_roles_vars.items():
            var.set(True)
    
    def _deselect_all_roles(self):
        """取消選擇所有特殊角色"""
        for role, var in self.special_roles_vars.items():
            var.set(False)
    
    def _select_basic_roles(self):
        """選擇基本角色配置（預言家、女巫、獵人）"""
        self._deselect_all_roles()
        basic_roles = ["seer", "witch", "hunter"]
        for role in basic_roles:
            if role in self.special_roles_vars:
                self.special_roles_vars[role].set(True)
    
    def _start_game(self):
        """開始新游戲"""
        # 檢查參數
        player_count = self.player_count_var.get()
        werewolf_count = self.werewolf_count_var.get()
        
        if werewolf_count >= player_count / 2:
            messagebox.showerror("參數錯誤", "狼人數量不能超過或等於玩家總數的一半")
            return
        
        # 解析人類玩家ID
        human_players = []
        if self.human_players_var.get():
            try:
                human_players = [int(pid.strip()) for pid in self.human_players_var.get().split(",")]
                # 檢查ID是否有效
                for pid in human_players:
                    if pid < 1 or pid > player_count:
                        messagebox.showerror("參數錯誤", f"玩家ID {pid} 超出範圍（1-{player_count}）")
                        return
            except ValueError:
                messagebox.showerror("參數錯誤", "人類玩家ID格式無效")
                return
        
        # 解析API設置
        api_type = None
        model_name = None
        if self.api_type_var.get() != "mixed":
            api_type = self.api_type_var.get()
            model_name = self.model_name_var.get()
            if not model_name:
                if api_type == "openai":
                    model_name = "gpt-4-turbo"
                elif api_type == "anthropic":
                    model_name = "claude-3-opus-20240229"
        
        # 獲取選擇的特殊角色
        special_roles = [role for role, var in self.special_roles_vars.items() if var.get()]
        
        # 呼叫開始游戲回調
        if self.on_start_game:
            self.on_start_game(
                player_count=player_count,
                werewolf_count=werewolf_count,
                special_roles=special_roles,
                human_players=human_players,
                api_type=api_type,
                model_name=model_name,
                max_days=self.max_days_var.get()
            )
    
    def _load_game(self):
        """載入游戲"""
        if self.on_load_game:
            self.on_load_game()
    
    def set_on_start_game(self, callback: Callable):
        """設置開始游戲的回調函數
        
        Args:
            callback (Callable): 回調函數
        """
        self.on_start_game = callback
    
    def set_on_load_game(self, callback: Callable):
        """設置載入游戲的回調函數
        
        Args:
            callback (Callable): 回調函數
        """
        self.on_load_game = callback
    
    def get_game_config(self) -> Dict[str, Any]:
        """獲取當前游戲配置
        
        Returns:
            Dict[str, Any]: 游戲配置字典
        """
        special_roles = [role for role, var in self.special_roles_vars.items() if var.get()]
        
        # 解析人類玩家ID
        human_players = []
        if self.human_players_var.get():
            try:
                human_players = [int(pid.strip()) for pid in self.human_players_var.get().split(",")]
            except ValueError:
                pass
        
        # 解析API設置
        api_type = None
        model_name = None
        if self.api_type_var.get() != "mixed":
            api_type = self.api_type_var.get()
            model_name = self.model_name_var.get()
        
        return {
            "player_count": self.player_count_var.get(),
            "werewolf_count": self.werewolf_count_var.get(),
            "special_roles": special_roles,
            "human_players": human_players,
            "api_type": api_type,
            "model_name": model_name,
            "max_days": self.max_days_var.get()
        }
