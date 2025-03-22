import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Callable, Optional
import threading
import asyncio

from .constants import COLORS
from .theme import ThemeStyles

class LogPanel(ctk.CTkFrame):
    """日誌面板，顯示游戲日誌並處理人類玩家的輸入"""
    
    def __init__(self, master, **kwargs):
        """初始化日誌面板
        
        Args:
            master: 父窗口
            **kwargs: 額外參數傳給父類
        """
        super().__init__(master, fg_color=COLORS["background"], **kwargs)
        
        # 創建界面元素
        self._create_log_area()
        self._create_human_input_area()
        
        # 人類玩家輸入處理
        self.current_response = None
        self.current_response_event = None
    
    def _create_log_area(self):
        """創建日誌區域"""
        # 日誌框架
        log_frame = ctk.CTkFrame(self, **ThemeStyles.card_frame())
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 日誌標題與按鈕列
        header_frame = ctk.CTkFrame(log_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header_frame, 
            text="游戲日誌", 
            **ThemeStyles.header_label()
        ).pack(side="left")
        
        # 添加搜索過濾器
        self.search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            header_frame, 
            textvariable=self.search_var, 
            width=150,
            placeholder_text="搜尋..."
        )
        search_entry.pack(side="right", padx=5)
        search_entry.bind("<KeyRelease>", self._filter_log)
        
        ctk.CTkButton(
            header_frame, 
            text="清空日誌", 
            command=self._clear_log,
            width=100,
            height=30,
            **ThemeStyles.small_button()
        ).pack(side="right", padx=10)
        
        # 日誌文本區
        self.log_text = ctk.CTkTextbox(
            log_frame, 
            wrap="word", 
            fg_color="#fcfcfc", 
            border_width=1,
            border_color="#e0e0e0",
            corner_radius=6,
            font=("Consolas", 11)
        )
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 為不同日誌類型配置標籤
        # CustomTkinter的CTkTextbox不支持原生的tag_configure，我們需要使用自定義的方法
        # 這里我們使用文本插入時指定顏色的方法
        
        # 初始日誌消息
        self.log("歡迎使用狼人殺 LLM 游戲！", "header")
        self.log("請配置游戲參數，然後點擊「創建新游戲」開始。", "info")
    
    def _create_human_input_area(self):
        """創建人類玩家輸入區域"""
        self.human_input_frame = ctk.CTkFrame(
            self, 
            **ThemeStyles.card_frame()
        )
        
        # 標題
        ctk.CTkLabel(
            self.human_input_frame, 
            text="你的回應", 
            **ThemeStyles.header_label()
        ).pack(anchor="w", padx=10, pady=(10, 5))
        
        # 輸入文本區
        self.human_input_text = ctk.CTkTextbox(
            self.human_input_frame, 
            height=120,
            fg_color="#ffffff",
            border_width=1,
            border_color="#e0e0e0",
            corner_radius=6,
            font=("Consolas", 11)
        )
        self.human_input_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 按鈕放在右下角
        button_frame = ctk.CTkFrame(self.human_input_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.submit_button = ctk.CTkButton(
            button_frame, 
            text="提交回應", 
            command=self._submit_human_response,
            **ThemeStyles.success_button()
        )
        self.submit_button.pack(side="right")
        
        # 默認隱藏
        self.human_input_frame.pack_forget()
    
    def log(self, message: str, tag: str = "info"):
        """添加日誌消息
        
        Args:
            message (str): 日誌消息
            tag (str, optional): 消息類型標籤. 默認為 "info"
        """
        # 設置不同標籤對應的文本顏色
        tag_colors = {
            "header": COLORS["primary"],
            "info": COLORS["text"],
            "warning": COLORS["warning"],
            "error": COLORS["error"],
            "success": COLORS["success"],
            "player": "#663399",  # 紫色
            "werewolf": COLORS["werewolf"],
            "villager": COLORS["villager"],
            "night": COLORS["night"],
            "day": COLORS["day"]
        }
        
        # 設置不同標籤對應的文本字體
        tag_fonts = {
            "header": ("Arial", 12, "bold"),
            "night": ("Arial", 11, "bold"),
            "day": ("Arial", 11, "bold")
        }
        
        # 獲取顏色和字體
        color = tag_colors.get(tag, COLORS["text"])
        font = tag_fonts.get(tag, None)
        
        # 插入文本
        self.log_text.configure(state="normal")
        
        # 設置字體和顏色
        if font:
            current_font = self.log_text.cget("font")
            self.log_text.configure(font=font)
        
        self.log_text.insert("end", message + "\n", {"text_color": color})
        
        # 恢復默認字體
        if font:
            self.log_text.configure(font=current_font)
        
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def _clear_log(self):
        """清空日誌區"""
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
        self.log("日誌已清空", "info")
    
    def _filter_log(self, event=None):
        """根據搜索條件過濾日誌"""
        search_text = self.search_var.get().lower()
        if not search_text:
            # 如果沒有搜索文字，顯示所有內容
            # 這個功能在CTkTextbox中比較難實現，需要保存原始日誌
            # 簡化版本：僅清空並顯示已過濾的消息
            self._clear_log()
            self.log("搜索已清空，請重新開始游戲查看完整日誌", "info")
            return
            
        # 獲取所有文本
        self.log_text.configure(state="normal")
        all_text = self.log_text.get("1.0", "end")
        self.log_text.delete("1.0", "end")
        
        # 按行過濾並添加匹配的行
        for line in all_text.split('\n'):
            if search_text in line.lower():
                # 保持原來的標籤（這需要更複雜的實現）
                self.log_text.insert("end", line + '\n', {"text_color": COLORS["text"]})
                
        self.log_text.configure(state="disabled")
    
    def show_human_input(self, prompt: str, system_message: Optional[str] = None):
        """顯示人類玩家輸入區並等待回應
        
        Args:
            prompt (str): 提示信息
            system_message (Optional[str], optional): 系統消息
        """
        # 顯示提示
        self.log("\n=== 你的回合 ===", "header")
        if system_message:
            self.log(f"【角色指引】{system_message}", "info")
        self.log(f"\n{prompt}\n", "info")
        
        # 顯示輸入框
        self.human_input_frame.pack(fill="x", padx=10, pady=10)
        self.human_input_text.focus_set()
    
    def _submit_human_response(self):
        """提交人類玩家的回應"""
        response = self.human_input_text.get("1.0", "end").strip()
        
        if not response:
            messagebox.showwarning("提示", "請輸入回應")
            return
        
        # 記錄到日誌
        self.log("\n你的回應：", "header")
        self.log(response, "player")
        
        # 清空輸入區
        self.human_input_text.delete("1.0", "end")
        
        # 隱藏輸入框
        self.human_input_frame.pack_forget()
        
        # 設置回應並觸發事件
        if hasattr(self, 'current_response_event') and self.current_response_event:
            self.current_response = response
            # 在UI線程中調用asyncio的事件方法必須小心
            # 我們將其放入一個線程中執行
            threading.Thread(target=self._set_response_event).start()
    
    def _set_response_event(self):
        """設置回應事件（在單獨線程中執行）"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._set_event())
        loop.close()
    
    async def _set_event(self):
        """設置回應事件"""
        if hasattr(self, 'current_response_event') and self.current_response_event:
            self.current_response_event.set()
    
    def set_event_and_wait(self, event, response):
        """設置事件和響應
        
        Args:
            event (asyncio.Event): 事件對象
            response (str): 響應文本
        """
        self.current_response_event = event
        self.current_response = response
