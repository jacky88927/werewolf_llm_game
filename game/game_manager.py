import os
import asyncio
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from .game_state import GameState
from api import OpenAIHandler, AnthropicHandler

class HumanPlayerHandler:
    """處理與人類玩家的交互"""
    
    def __init__(self, player_name):
        """初始化人類玩家處理器
        
        Args:
            player_name (str): 玩家名稱
        """
        self.player_name = player_name
    
    async def get_response(self, prompt, system_message=None, temperature=0.7, max_tokens=500):
        """從人類玩家獲取回應
        
        Args:
            prompt (str): 提示
            system_message (str, optional): 系統消息 (會顯示給玩家)
            temperature (float, optional): 不適用於人類玩家
            max_tokens (int, optional): 不適用於人類玩家
            
        Returns:
            str: 玩家的回應
        """
        print(f"\n=== {self.player_name} 的回合 ===")
        if system_message:
            print(f"【角色指引】{system_message}")
        print(f"\n{prompt}\n")
        
        return input("你的回應> ")

class GameManager:
    """狼人殺遊戲管理器"""
    
    def __init__(self):
        """初始化遊戲管理器"""
        # 載入環境變量
        load_dotenv()
        
        self.game_state = GameState()
        self.api_handlers = {}  # {player_id: api_handler}
        self.api_models = {}  # {player_id: model_name}
    
    def setup_game(self, player_count: int = None, werewolf_count: int = None, special_roles: List[str] = None,
                   human_players: List[int] = None, api_type: str = None, model_name: str = None):
        """設置遊戲
        
        Args:
            player_count (int, optional): 玩家數量。默認使用環境變量
            werewolf_count (int, optional): 狼人數量。默認使用環境變量
            special_roles (List[str], optional): 特殊角色列表。默認使用環境變量
            human_players (List[int], optional): 人類玩家的ID列表。默認為空
            api_type (str, optional): 使用的API類型('openai' 或 'anthropic')。默認根據環境變量混合
            model_name (str, optional): 使用的模型名稱。默認根據環境變量混合
        """
        # 如果沒有提供參數，使用環境變量
        if player_count is None:
            player_count = int(os.getenv("DEFAULT_PLAYER_COUNT", "6"))
        
        if werewolf_count is None:
            werewolf_count = int(os.getenv("DEFAULT_WEREWOLF_COUNT", "2"))
        
        if special_roles is None:
            special_roles_str = os.getenv("DEFAULT_SPECIAL_ROLES", "seer")
            special_roles = [role.strip() for role in special_roles_str.split(",")]
        
        # 設置人類玩家
        self.human_players = human_players or []
        
        # 設置API類型和模型
        self.use_single_api = api_type is not None and model_name is not None
        self.api_type = api_type
        self.model_name = model_name
        
        # 設置遊戲
        self.game_state.setup_game(player_count, werewolf_count, special_roles)
        
        # 為玩家分配處理程序
        self._setup_api_handlers()
    
    def _setup_api_handlers(self):
        """為玩家設置API處理程序"""
        # 清除之前的處理程序
        self.api_handlers = {}
        self.api_models = {}
        
        # 如果使用單一API
        if self.use_single_api:
            # 創建單一API處理程序
            if self.api_type == "openai":
                api_handler = OpenAIHandler(model=self.model_name)
                model_display = f"OpenAI - {self.model_name}"
            elif self.api_type == "anthropic":
                api_handler = AnthropicHandler(model=self.model_name)
                model_display = f"Anthropic - {self.model_name}"
            else:
                raise ValueError(f"不支持的API類型: {self.api_type}")
        else:
            # 獲取可用的API模型
            openai_models = ["gpt-4", "gpt-3.5-turbo"]
            anthropic_models = ["claude-3-opus-20240229", "claude-3-sonnet-20240229", "claude-3-haiku-20240307"]
            
            # 混合模型列表
            models = []
            models.extend([(api_type, model_name) for api_type, model_name in [("openai", m) for m in openai_models]])
            models.extend([(api_type, model_name) for api_type, model_name in [("anthropic", m) for m in anthropic_models]])
        
        # 為每個玩家分配處理程序
        for i, player in enumerate(self.game_state.players):
            player_id = player["player_id"]
            player_name = player["name"]
            
            # 檢查是否是人類玩家
            if player_id in self.human_players:
                self.api_handlers[player_id] = HumanPlayerHandler(player_name)
                self.api_models[player_id] = "Human Player"
                continue
            
            # AI玩家
            if self.use_single_api:
                self.api_handlers[player_id] = api_handler
                self.api_models[player_id] = model_display
            else:
                # 使用混合API
                api_type, model_name = models[i % len(models)]
                
                if api_type == "openai":
                    self.api_handlers[player_id] = OpenAIHandler(model=model_name)
                    self.api_models[player_id] = f"OpenAI - {model_name}"
                elif api_type == "anthropic":
                    self.api_handlers[player_id] = AnthropicHandler(model=model_name)
                    self.api_models[player_id] = f"Anthropic - {model_name}"
        
        # 打印分配結果
        print("玩家角色分配：")
        for player in self.game_state.players:
            player_id = player["player_id"]
            player_name = player["name"]
            player_role = player["role"]
            model = self.api_models.get(player_id, "未分配")
            print(f"玩家{player_id}（{player_name}）- {player_role}：使用 {model}")
    
    async def run_game(self, max_days: int = 10):
        """運行遊戲
        
        Args:
            max_days (int, optional): 最大遊戲天數。默認為 10
        """
        if self.game_state.phase == "setup":
            print("遊戲尚未設置，正在使用默認設置...")
            self.setup_game()
        
        # 運行遊戲直到結束或達到最大天數
        while not self.game_state.game_over and self.game_state.day <= max_days:
            await self._run_game_phase()
        
        # 打印遊戲結果
        if self.game_state.game_over:
            print(f"遊戲結束！獲勝者：{self.game_state.winner}")
        else:
            print(f"遊戲達到最大天數 {max_days}，強制結束")
            
            # 統計存活玩家
            alive_werewolves = sum(1 for p in self.game_state.players if p["is_alive"] and p["role"] == "werewolf")
            alive_villagers = sum(1 for p in self.game_state.players if p["is_alive"] and p["role"] != "werewolf")
            
            print(f"存活狼人：{alive_werewolves}，存活村民：{alive_villagers}")
            
            if alive_werewolves == 0:
                print("村民陣營獲勝！")
            elif alive_werewolves >= alive_villagers:
                print("狼人陣營獲勝！")
            else:
                print("平局！")
        
        # 將遊戲結果保存到文件
        self._save_game_result()
    
    async def _run_game_phase(self):
        """運行當前遊戲階段"""
        phase = self.game_state.phase
        day = self.game_state.day
        
        print(f"===== 第{day}天，{phase}階段 =====")
        
        if phase == "night":
            print("夜晚降臨，玩家們閉上眼睛...")
            await self.game_state.process_night_actions(self.api_handlers)
        
        elif phase == "day":
            # 打印夜間死亡信息
            if self.game_state.last_night_deaths:
                for death in self.game_state.last_night_deaths:
                    print(f"玩家{death['player_id']}（{death['name']}）在夜晚被殺，他的身份是{death['role']}")
            else:
                print("平安夜，昨晚無人死亡")
            
            print("\n天亮了，玩家們開始討論...")
            await self.game_state.process_day_discussions(self.api_handlers)
            
            # 打印討論內容
            for discussion in self.game_state.current_discussions:
                print(f"\n玩家{discussion['player_id']}（{discussion['player_name']}）：")
                print(f"「{discussion['content']}」")
        
        elif phase == "vote":
            print("\n投票開始，玩家們選擇要放逐的對象...")
            await self.game_state.process_votes(self.api_handlers)
        
        elif phase == "gameover":
            print("\n遊戲結束！")
            print(f"獲勝者：{self.game_state.winner}")
        
        # 緩沖顯示
        await asyncio.sleep(1)
    
    def _save_game_result(self):
        """保存遊戲結果到文件"""
        # 創建結果目錄（如果不存在）
        results_dir = os.path.join(os.getcwd(), "game_results")
        os.makedirs(results_dir, exist_ok=True)
        
        # 生成文件名
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(results_dir, f"game_{timestamp}.json")
        
        # 保存遊戲狀態
        self.game_state.save_game(filename)
        print(f"遊戲結果已保存到：{filename}")
    
    @classmethod
    async def load_and_run(cls, filename: str, max_days: int = 10, human_players: List[int] = None, 
                           api_type: str = None, model_name: str = None):
        """從文件加載遊戲狀態並繼續運行
        
        Args:
            filename (str): 遊戲狀態文件名
            max_days (int, optional): 最大遊戲天數。默認為 10
            human_players (List[int], optional): 人類玩家的ID列表。默認為空
            api_type (str, optional): 使用的API類型('openai' 或 'anthropic')
            model_name (str, optional): 使用的模型名稱
        """
        # 創建遊戲管理器
        manager = cls()
        
        # 加載遊戲狀態
        manager.game_state = GameState.load_game(filename)
        
        # 設置人類玩家和API選項
        manager.human_players = human_players or []
        manager.use_single_api = api_type is not None and model_name is not None
        manager.api_type = api_type
        manager.model_name = model_name
        
        # 設置處理程序
        manager._setup_api_handlers()
        
        # 運行遊戲
        await manager.run_game(max_days)
        
        return manager
    
    def get_game_summary(self) -> Dict[str, Any]:
        """獲取遊戲摘要
        
        Returns:
            Dict[str, Any]: 遊戲摘要
        """
        # 統計存活玩家
        alive_werewolves = sum(1 for p in self.game_state.players if p["is_alive"] and p["role"] == "werewolf")
        alive_villagers = sum(1 for p in self.game_state.players if p["is_alive"] and p["role"] != "werewolf")
        
        # 創建總覽信息
        summary = {
            "day": self.game_state.day,
            "phase": self.game_state.phase,
            "alive_werewolves": alive_werewolves,
            "alive_villagers": alive_villagers,
            "game_over": self.game_state.game_over,
            "winner": self.game_state.winner,
            "players": []
        }
        
        # 添加玩家信息
        for player in self.game_state.players:
            player_info = {
                "player_id": player["player_id"],
                "name": player["name"],
                "role": player["role"],
                "is_alive": player["is_alive"],
                "model": self.api_models.get(player["player_id"], "未知")
            }
            summary["players"].append(player_info)
        
        return summary
