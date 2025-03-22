import customtkinter as ctk
import asyncio
import threading
import queue
import os
from tkinter import filedialog, messagebox
from typing import Dict, Any, List, Optional
import json

from .settings_panel import SettingsPanel
from .game_panel import GamePanel
from .log_panel import LogPanel
from .theme import setup_theme, ThemeStyles
from .constants import COLORS

# 引入游戲組件
from game import GameManager
from game.game_manager import HumanPlayerHandler

class WerewolfApp(ctk.CTk):
    """狼人殺游戲應用主類"""
    
    def __init__(self):
        """初始化應用"""
        super().__init__()
        
        # 配置窗口
        self.title("🐺 狼人殺 LLM 游戲")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        
        # 設置主題
        setup_theme()
        
        # 游戲管理器實例
        self.game_manager = None
        
        # 消息隊列（從游戲線程到UI線程）
        self.message_queue = queue.Queue()
        
        # 創建主界面
        self._create_main_interface()
        
        # 啟動消息處理器
        self._start_message_processor()
    
    def _create_main_interface(self):
        """創建主界面布局"""
        # 創建主框架
        main_frame = ctk.CTkFrame(self, fg_color=COLORS["background"])
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 左側面板 (設置區)
        self.settings_panel = SettingsPanel(main_frame, width=300)
        self.settings_panel.pack(side="left", fill="y", padx=(0, 10))
        
        # 設置回調
        self.settings_panel.set_on_start_game(self._start_new_game)
        self.settings_panel.set_on_load_game(self._load_game)
        
        # 右側面板
        right_panel = ctk.CTkFrame(main_frame, fg_color=COLORS["background"])
        right_panel.pack(side="right", fill="both", expand=True)
        
        # 游戲狀態面板
        self.game_panel = GamePanel(right_panel)
        self.game_panel.pack(fill="x")
        
        # 日誌面板
        self.log_panel = LogPanel(right_panel)
        self.log_panel.pack(fill="both", expand=True)
    
    def _start_message_processor(self):
        """啟動消息處理器，用於處理從游戲線程到UI線程的消息"""
        def process_messages():
            """定期檢查並處理消息隊列中的消息"""
            try:
                # 處理所有現有消息
                while not self.message_queue.empty():
                    message = self.message_queue.get_nowait()
                    self._process_message(message)
            except queue.Empty:
                pass
            finally:
                # 計劃下一次檢查
                self.after(100, process_messages)
        
        # 啟動第一次檢查
        self.after(100, process_messages)
    
    def _process_message(self, message):
        """處理來自游戲線程的消息
        
        Args:
            message (tuple): 消息元組，格式為 (msg_type, content, ...)
        """
        msg_type = message[0]
        
        if msg_type == "LOG":
            # 日誌消息
            content = message[1]
            tag = message[2] if len(message) > 2 else "info"
            self.log_panel.log(content, tag)
        
        elif msg_type == "ERROR":
            # 錯誤消息
            content = message[1]
            messagebox.showerror("錯誤", content)
            self.log_panel.log(f"錯誤：{content}", "error")
        
        elif msg_type == "STATUS":
            # 狀態更新
            status = message[1]
            self.game_panel.update_status(status=status)
        
        elif msg_type == "UPDATE_STATUS":
            # 游戲狀態面板更新
            status_data = message[1]
            self.game_panel.update_status(
                day=status_data.get("day"),
                phase=status_data.get("phase"),
                alive=status_data.get("alive"),
                status=status_data.get("status")
            )
        
        elif msg_type == "HUMAN_PROMPT":
            # 人類玩家提示
            prompt = message[1]
            system_message = message[2] if len(message) > 2 else None
            
            # 顯示輸入提示
            self.log_panel.show_human_input(prompt, system_message)
    
    def _redirect_game_manager_output(self):
        """重定向GameManager中的print輸出到GUI"""
        import sys
        
        # 創建自定義的stdout類
        class GUIStdout:
            def __init__(self, message_queue):
                self.message_queue = message_queue
                self.original_stdout = sys.stdout
                
            def write(self, message):
                if message.strip():  # 忽略空白消息
                    self.message_queue.put(("LOG", message.rstrip()))
                
                # 同時也輸出到原始的stdout（可選）
                # self.original_stdout.write(message)
                
            def flush(self):
                # 必須實現此方法
                self.original_stdout.flush()
        
        # 替換 sys.stdout
        sys.stdout = GUIStdout(self.message_queue)
    
    def _start_new_game(self, player_count, werewolf_count, special_roles, 
                         human_players, api_type, model_name, max_days):
        """開始新游戲
        
        Args:
            player_count (int): 玩家數量
            werewolf_count (int): 狼人數量
            special_roles (List[str]): 特殊角色列表
            human_players (List[int]): 人類玩家ID列表
            api_type (str, optional): API類型
            model_name (str, optional): 模型名稱
            max_days (int): 最大游戲天數
        """
        # 清空日誌
        self.log_panel.log("創建新游戲...", "header")
        
        # 更新游戲狀態
        self.game_panel.update_status(
            day="Day 0",
            phase="準備中",
            alive=f"狼人: {werewolf_count} | 村民: {player_count - werewolf_count}",
            status="游戲狀態: 準備中"
        )
        
        # 創建游戲管理器
        self.game_manager = GameManager()
        
        # 修改GameManager中的print輸出，重定向到GUI
        self._redirect_game_manager_output()
        
        # 開始游戲
        self.log_panel.log(f"創建新游戲，玩家數量：{player_count}，狼人數量：{werewolf_count}", "header")
        self.log_panel.log(f"特殊角色：{', '.join(special_roles)}", "info")
        self.log_panel.log(f"最大天數：{max_days}", "info")
        
        if human_players:
            self.log_panel.log(f"人類玩家ID：{', '.join(map(str, human_players))}", "info")
        else:
            self.log_panel.log("全部為AI玩家", "info")
        
        if api_type:
            self.log_panel.log(f"使用API：{api_type}, 模型：{model_name}", "info")
        else:
            self.log_panel.log("使用混合API和模型", "info")
        
        # 更新游戲狀態
        self.message_queue.put(("STATUS", "游戲狀態: 準備中"))
        
        # 啟動游戲線程
        threading.Thread(target=self._run_game_thread, args=(
            player_count, werewolf_count, special_roles, 
            human_players, api_type, model_name, max_days
        ), daemon=True).start()
    
    def _load_game(self):
        """載入游戲狀態"""
        # 打開文件對話框
        file_path = filedialog.askopenfilename(
            title="選擇游戲狀態文件",
            filetypes=[("JSON 文件", "*.json"), ("所有文件", "*.*")],
            initialdir=os.path.join(os.getcwd(), "game_results")
        )
        
        if not file_path:
            return
            
        # 獲取設置面板中的配置
        config = self.settings_panel.get_game_config()
        human_players = config["human_players"]
        api_type = config["api_type"]
        model_name = config["model_name"]
        max_days = config["max_days"]
        
        # 清空日誌
        self.log_panel.log("載入游戲...", "header")
        
        # 更新游戲狀態
        self.game_panel.update_status(status="游戲狀態: 載入中")
        
        # 啟動游戲線程
        threading.Thread(target=self._run_load_game_thread, args=(
            file_path, human_players, api_type, model_name, max_days
        ), daemon=True).start()
    
    def _run_game_thread(self, player_count, werewolf_count, special_roles, 
                         human_players, api_type, model_name, max_days):
        """在單獨的線程中運行游戲
        
        Args:
            player_count (int): 玩家數量
            werewolf_count (int): 狼人數量
            special_roles (List[str]): 特殊角色列表
            human_players (List[int]): 人類玩家ID列表
            api_type (str, optional): API類型
            model_name (str, optional): 模型名稱
            max_days (int): 最大游戲天數
        """
        try:
            # 獲取事件循環
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 設置游戲
            self.game_manager.setup_game(
                player_count, werewolf_count, special_roles, 
                human_players, api_type, model_name
            )
            
            # 將HumanPlayerHandler的get_response方法指向我們的GUI處理方法
            for player_id, handler in self.game_manager.api_handlers.items():
                if isinstance(handler, HumanPlayerHandler):
                    handler.get_response = self._handle_human_input
            
            # 向UI發送游戲已設置消息
            self.message_queue.put(("STATUS", "游戲狀態: 進行中"))
            
            # 更新游戲狀態變數
            self.message_queue.put(("UPDATE_STATUS", {
                "day": "Day 1",
                "phase": "游戲開始",
                "alive": f"狼人: {werewolf_count} | 村民: {player_count - werewolf_count}"
            }))
            
            # 運行游戲
            loop.run_until_complete(self.game_manager.run_game(max_days))
            
            # 獲取並顯示游戲總結
            summary = self.game_manager.get_game_summary()
            
            # 向UI發送游戲結束消息
            self.message_queue.put(("STATUS", "游戲狀態: 游戲結束"))
            self.message_queue.put(("LOG", f"\n===== 游戲總結 =====", "header"))
            self.message_queue.put(("LOG", f"游戲天數：{summary['day']}", "info"))
            self.message_queue.put(("LOG", f"游戲狀態：{'已結束' if summary['game_over'] else '進行中'}", "info"))
            self.message_queue.put(("LOG", f"獲勝者：{summary['winner'] or '無'}", "success"))
            self.message_queue.put(("LOG", f"存活狼人：{summary['alive_werewolves']}，存活村民：{summary['alive_villagers']}", "info"))
            
            self.message_queue.put(("LOG", "\n玩家狀態：", "header"))
            for player in summary["players"]:
                status = "存活" if player["is_alive"] else "死亡"
                self.message_queue.put(("LOG", f"玩家{player['player_id']}（{player['name']}）- {player['role']} - {status} - 使用模型：{player['model']}", "player"))
            
            # 保存游戲結果
            self._save_game_results(summary)
        
        except Exception as e:
            import traceback
            error_msg = f"游戲運行錯誤：{str(e)}\n{traceback.format_exc()}"
            self.message_queue.put(("ERROR", error_msg))
            self.message_queue.put(("STATUS", "游戲狀態: 錯誤"))
    
    def _run_load_game_thread(self, file_path, human_players, api_type, model_name, max_days):
        """在單獨的線程中載入並運行游戲
        
        Args:
            file_path (str): 游戲狀態文件路徑
            human_players (List[int]): 人類玩家ID列表
            api_type (str, optional): API類型
            model_name (str, optional): 模型名稱
            max_days (int): 最大游戲天數
        """
        try:
            # 獲取事件循環
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # 向UI發送載入游戲消息
            self.message_queue.put(("LOG", f"從文件載入游戲：{file_path}", "header"))
            
            # 載入並運行游戲
            self.game_manager = loop.run_until_complete(GameManager.load_and_run(
                file_path, max_days, human_players, api_type, model_name
            ))
            
            # 將HumanPlayerHandler的get_response方法指向我們的GUI處理方法
            for player_id, handler in self.game_manager.api_handlers.items():
                if isinstance(handler, HumanPlayerHandler):
                    handler.get_response = self._handle_human_input
            
            # 向UI發送游戲已設置消息
            self.message_queue.put(("STATUS", "游戲狀態: 游戲載入完成"))
            
            # 獲取並顯示游戲總結
            summary = self.game_manager.get_game_summary()
            
            # 更新游戲狀態
            self.message_queue.put(("STATUS", "游戲狀態: 游戲結束"))
            self.message_queue.put(("LOG", f"\n===== 游戲總結 =====", "header"))
            self.message_queue.put(("LOG", f"游戲天數：{summary['day']}", "info"))
            self.message_queue.put(("LOG", f"游戲狀態：{'已結束' if summary['game_over'] else '進行中'}", "info"))
            self.message_queue.put(("LOG", f"獲勝者：{summary['winner'] or '無'}", "success"))
            self.message_queue.put(("LOG", f"存活狼人：{summary['alive_werewolves']}，存活村民：{summary['alive_villagers']}", "info"))
            
            self.message_queue.put(("LOG", "\n玩家狀態：", "header"))
            for player in summary["players"]:
                status = "存活" if player["is_alive"] else "死亡"
                self.message_queue.put(("LOG", f"玩家{player['player_id']}（{player['name']}）- {player['role']} - {status}", "player"))
        
        except Exception as e:
            import traceback
            error_msg = f"載入游戲錯誤：{str(e)}\n{traceback.format_exc()}"
            self.message_queue.put(("ERROR", error_msg))
            self.message_queue.put(("STATUS", "游戲狀態: 錯誤"))
    
    def _save_game_results(self, summary):
        """保存游戲結果到文件
        
        Args:
            summary (Dict[str, Any]): 游戲摘要
        """
        try:
            results_dir = os.path.join(os.getcwd(), "game_results")
            os.makedirs(results_dir, exist_ok=True)
            
            # 生成文件名
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(results_dir, f"game_summary_{timestamp}.json")
            
            # 保存摘要
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)
                
            self.message_queue.put(("LOG", f"\n游戲摘要已保存到：{filename}", "info"))
        
        except Exception as e:
            self.message_queue.put(("LOG", f"\n保存游戲摘要失敗：{str(e)}", "error"))
    
    async def _handle_human_input(self, prompt, system_message=None, temperature=0.7, max_tokens=500):
        """處理人類玩家輸入
        
        Args:
            prompt (str): 提示
            system_message (str, optional): 系統消息
            temperature (float, optional): 不適用於人類玩家
            max_tokens (int, optional): 不適用於人類玩家
            
        Returns:
            str: 玩家的回應
        """
        # 通過消息隊列向UI發送提示
        self.message_queue.put(("HUMAN_PROMPT", prompt, system_message))
        
        # 等待人類玩家的輸入
        response_event = asyncio.Event()
        self.log_panel.current_response_event = response_event
        self.log_panel.current_response = None
        
        # 等待事件
        await response_event.wait()
        
        # 返回獲取的輸入
        return self.log_panel.current_response
