import random
from typing import List, Dict, Any, Optional
import json
import os

class GameState:
    """管理狼人殺遊戲的狀態"""
    
    def __init__(self):
        """初始化遊戲狀態"""
        self.day = 0  # 遊戲天數
        self.phase = "setup"  # 遊戲階段：setup, night, day, vote, gameover
        self.players = []  # 玩家列表
        self.player_objects = {}  # 玩家對象 {player_id: player_object}
        self.current_discussions = []  # 當前討論 [{"player_id": id, "player_name": name, "content": content}]
        self.votes = {}  # 投票 {voter_id: target_id}
        self.night_actions = {}  # 夜間行動 {player_id: {"action": action, "target": target_id, "result": result}}
        self.last_night_deaths = []  # 上一晚死亡的玩家
        self.game_over = False  # 遊戲是否結束
        self.winner = None  # 獲勝陣營
        self.log = []  # 遊戲日誌
    
    def setup_game(self, player_count: int, werewolf_count: int, special_roles: List[str] = None):
        """設置遊戲
        
        Args:
            player_count (int): 玩家數量
            werewolf_count (int): 狼人數量
            special_roles (List[str], optional): 特殊角色列表。默認為 None
        """
        if special_roles is None:
            special_roles = []
        
        # 檢查參數有效性
        if player_count < 4:
            raise ValueError("玩家數量必須至少為4")
        if werewolf_count < 1 or werewolf_count >= player_count // 2:
            raise ValueError(f"狼人數量必須在1到{player_count // 2 - 1}之間")
        if len(special_roles) > player_count - werewolf_count - 1:
            raise ValueError("特殊角色數量過多")
        
        # 重置遊戲狀態
        self.day = 0
        self.phase = "setup"
        self.players = []
        self.player_objects = {}
        self.current_discussions = []
        self.votes = {}
        self.night_actions = {}
        self.last_night_deaths = []
        self.game_over = False
        self.winner = None
        self.log = []
        
        # 創建角色分配
        roles = ["werewolf"] * werewolf_count
        roles.extend(special_roles)
        remaining_count = player_count - len(roles)
        roles.extend(["villager"] * remaining_count)
        
        # 打亂角色
        random.shuffle(roles)
        
        # 生成玩家ID和名稱
        player_ids = list(range(1, player_count + 1))
        player_names = [f"玩家{i}" for i in player_ids]
        
        # 分配角色
        from roles import Villager, Werewolf, Seer
        
        werewolf_ids = []
        
        for i in range(player_count):
            player_id = player_ids[i]
            name = player_names[i]
            role = roles[i]
            
            player_info = {
                "player_id": player_id,
                "name": name,
                "role": role,
                "is_alive": True
            }
            
            self.players.append(player_info)
            
            # 創建相應的角色對象
            if role == "werewolf":
                player_obj = Werewolf(player_id, name)
                werewolf_ids.append(player_id)
                self.player_objects[player_id] = player_obj
            elif role == "seer":
                player_obj = Seer(player_id, name)
                self.player_objects[player_id] = player_obj
            else:  # 普通村民
                player_obj = Villager(player_id, name)
                self.player_objects[player_id] = player_obj
        
        # 設置狼人的隊友
        for werewolf_id in werewolf_ids:
            werewolf = self.player_objects[werewolf_id]
            werewolf.set_teammates([wid for wid in werewolf_ids if wid != werewolf_id])
        
        self.add_log("遊戲已設置")
        
        # 下一個階段
        self.next_phase()
    
    def next_phase(self):
        """進入下一個遊戲階段"""
        if self.phase == "setup":
            self.phase = "night"
            self.day += 1
            self.add_log(f"第{self.day}天夜晚開始")
        elif self.phase == "night":
            self.phase = "day"
            self.add_log(f"第{self.day}天白天開始")
            # 清除上一輪討論
            self.current_discussions = []
        elif self.phase == "day":
            self.phase = "vote"
            self.add_log(f"第{self.day}天投票階段開始")
            # 清除上一輪投票
            self.votes = {}
        elif self.phase == "vote":
            # 處理投票結果
            self._process_votes()
            # 檢查遊戲是否結束
            if self.check_game_over():
                self.phase = "gameover"
                self.add_log("遊戲結束")
            else:
                self.phase = "night"
                self.day += 1
                self.add_log(f"第{self.day}天夜晚開始")
    
    def check_game_over(self) -> bool:
        """檢查遊戲是否結束
        
        Returns:
            bool: 遊戲是否結束
        """
        # 統計存活的狼人和村民
        alive_werewolves = sum(1 for p in self.players if p["is_alive"] and p["role"] == "werewolf")
        alive_villagers = sum(1 for p in self.players if p["is_alive"] and p["role"] != "werewolf")
        
        if alive_werewolves == 0:
            # 所有狼人都死亡，村民陣營勝利
            self.game_over = True
            self.winner = "村民陣營"
            self.add_log("所有狼人都被殺死，村民陣營獲勝！")
            return True
        elif alive_werewolves >= alive_villagers:
            # 狼人數量大於或等於村民，狼人陣營勝利
            self.game_over = True
            self.winner = "狼人陣營"
            self.add_log("狼人數量已經超過村民，狼人陣營獲勝！")
            return True
        
        return False
    
    async def process_night_actions(self, api_handlers: Dict[int, Any]):
        """處理夜間行動
        
        Args:
            api_handlers (Dict[int, Any]): API 處理程序 {player_id: api_handler}
        """
        if self.phase != "night":
            self.add_log("錯誤：現在不是夜晚階段")
            return
        
        # 清除之前的夜間行動和死亡記錄
        self.night_actions = {}
        self.last_night_deaths = []
        
        # 獲取所有存活玩家的夜間行動
        for player_info in self.players:
            player_id = player_info["player_id"]
            
            if not player_info["is_alive"]:
                continue
            
            player_obj = self.player_objects[player_id]
            api_handler = api_handlers.get(player_id)
            
            if api_handler:
                action_result = await player_obj.night_action(self.get_state_for_player(player_id), api_handler)
                self.night_actions[player_id] = action_result
            else:
                self.add_log(f"警告：玩家{player_id}沒有API處理程序")
        
        # 處理狼人的攻擊行動
        self._process_werewolf_attacks()
        
        # 將結果添加到玩家歷史記錄
        self._update_player_history()
        
        # 進入下一個階段
        self.next_phase()
    
    def _process_werewolf_attacks(self):
        """處理狼人的攻擊行動"""
        # 找出所有狼人的攻擊目標
        attack_targets = []
        for player_id, action in self.night_actions.items():
            if action.get("action") == "attack" and action.get("target") is not None:
                attack_targets.append(action.get("target"))
        
        if not attack_targets:
            self.add_log("狼人沒有選擇攻擊目標")
            return
        
        # 如果有多個狼人，取第一個攻擊目標（首領狼人的選擇）
        target_id = attack_targets[0]
        target = next((p for p in self.players if p["player_id"] == target_id), None)
        
        if target and target["is_alive"]:
            # 處理玩家死亡
            target["is_alive"] = False
            target_name = target["name"]
            self.last_night_deaths.append({"player_id": target_id, "name": target_name, "role": target["role"]})
            self.add_log(f"玩家{target_id}（{target_name}）被狼人殺死了")
        else:
            self.add_log(f"狼人的攻擊目標無效或已經死亡")
    
    async def process_day_discussions(self, api_handlers: Dict[int, Any]):
        """處理白天討論
        
        Args:
            api_handlers (Dict[int, Any]): API 處理程序 {player_id: api_handler}
        """
        if self.phase != "day":
            self.add_log("錯誤：現在不是白天討論階段")
            return
        
        # 清除之前的討論
        self.current_discussions = []
        
        # 獲取所有存活玩家的討論
        for player_info in self.players:
            player_id = player_info["player_id"]
            
            if not player_info["is_alive"]:
                continue
            
            player_obj = self.player_objects[player_id]
            player_name = player_info["name"]
            api_handler = api_handlers.get(player_id)
            
            if api_handler:
                # 獲取玩家的討論內容
                discussion = await player_obj.day_discussion(self.get_state_for_player(player_id), api_handler)
                
                # 添加到當前討論
                self.current_discussions.append({
                    "player_id": player_id,
                    "player_name": player_name,
                    "content": discussion
                })
                
                # 添加到玩家歷史記錄
                player_obj.add_history(f"第{self.day}天白天：你說：「{discussion}」")
                
                # 添加到遊戲日誌
                self.add_log(f"玩家{player_id}（{player_name}）說：「{discussion}」")
            else:
                self.add_log(f"警告：玩家{player_id}沒有API處理程序")
        
        # 更新所有玩家的歷史記錄
        for player_info in self.players:
            player_id = player_info["player_id"]
            
            if not player_info["is_alive"]:
                continue
            
            player_obj = self.player_objects[player_id]
            
            # 將其他人的討論添加到自己的歷史記錄
            for discussion in self.current_discussions:
                if discussion["player_id"] != player_id:
                    player_obj.add_history(
                        f"第{self.day}天白天：{discussion['player_name']}（玩家{discussion['player_id']}）說：「{discussion['content']}」"
                    )
        
        # 進入下一個階段（修改：白天討論完畢后自動進入投票階段）
        self.next_phase()
    
    async def process_votes(self, api_handlers: Dict[int, Any]):
        """處理投票
        
        Args:
            api_handlers (Dict[int, Any]): API 處理程序 {player_id: api_handler}
        """
        if self.phase != "vote":
            self.add_log("錯誤：現在不是投票階段")
            return
        
        # 清除之前的投票
        self.votes = {}
        
        # 獲取所有存活玩家的投票
        for player_info in self.players:
            player_id = player_info["player_id"]
            
            if not player_info["is_alive"]:
                continue
            
            player_obj = self.player_objects[player_id]
            player_name = player_info["name"]
            api_handler = api_handlers.get(player_id)
            
            if api_handler:
                # 獲取玩家的投票
                vote_target_id = await player_obj.vote(self.get_state_for_player(player_id), api_handler)
                
                # 檢查投票目標是否有效
                target_player = next((p for p in self.players if p["player_id"] == vote_target_id and p["is_alive"]), None)
                
                if target_player:
                    self.votes[player_id] = vote_target_id
                    
                    # 添加到玩家歷史記錄
                    player_obj.add_history(f"第{self.day}天投票：你投票給了玩家{vote_target_id}（{target_player['name']}）")
                    
                    # 添加到遊戲日誌
                    self.add_log(f"玩家{player_id}（{player_name}）投票給了玩家{vote_target_id}（{target_player['name']}）")
                else:
                    self.add_log(f"玩家{player_id}（{player_name}）的投票目標無效")
            else:
                self.add_log(f"警告：玩家{player_id}沒有API處理程序")
        
        # 處理投票結果
        self._process_votes()
        
        # 進入下一個階段
        self.next_phase()
    
    def _process_votes(self):
        """處理投票結果，放逐得票最多的玩家"""
        if not self.votes:
            self.add_log("沒有有效投票，無人被放逐")
            return
        
        # 統計每個玩家獲得的票數
        vote_counts = {}
        for target_id in self.votes.values():
            vote_counts[target_id] = vote_counts.get(target_id, 0) + 1
        
        # 找出得票最多的玩家
        max_votes = max(vote_counts.values())
        most_voted = [pid for pid, count in vote_counts.items() if count == max_votes]
        
        # 處理平票情況
        if len(most_voted) > 1:
            self.add_log(f"平票！{', '.join([f'玩家{pid}' for pid in most_voted])}票數相同，無人被放逐")
            return
        
        # 放逐得票最多的玩家
        target_id = most_voted[0]
        target = next((p for p in self.players if p["player_id"] == target_id), None)
        
        if target and target["is_alive"]:
            target["is_alive"] = False
            target_name = target["name"]
            target_role = target["role"]
            self.add_log(f"玩家{target_id}（{target_name}）被放逐，他的身份是{target_role}")
            
            # 更新所有玩家的歷史記錄
            for player_obj in self.player_objects.values():
                player_obj.add_history(f"第{self.day}天投票：玩家{target_id}（{target_name}）被放逐，身份是{target_role}")
    
    def _update_player_history(self):
        """更新玩家歷史記錄"""
        # 更新夜間行動結果
        for player_id, action in self.night_actions.items():
            player_obj = self.player_objects.get(player_id)
            if player_obj:
                action_type = action.get("action", "無")
                target_id = action.get("target")
                result = action.get("result")
                
                if action_type == "attack" and target_id:
                    target = next((p for p in self.players if p["player_id"] == target_id), None)
                    if target:
                        player_obj.add_history(f"第{self.day}天夜晚：你選擇攻擊玩家{target_id}（{target['name']}）")
                
                elif action_type == "check" and target_id and result:
                    target = next((p for p in self.players if p["player_id"] == target_id), None)
                    if target:
                        player_obj.add_history(f"第{self.day}天夜晚：你查驗了玩家{target_id}（{target['name']}），結果是{result}")
        
        # 更新夜間死亡結果
        if self.last_night_deaths:
            for player in self.last_night_deaths:
                death_msg = f"第{self.day}天夜晚：玩家{player['player_id']}（{player['name']}）被殺死，身份是{player['role']}"
                for player_obj in self.player_objects.values():
                    player_obj.add_history(death_msg)
    
    def get_state_for_player(self, player_id: int) -> Dict[str, Any]:
        """獲取特定玩家可見的遊戲狀態
        
        Args:
            player_id (int): 玩家 ID
            
        Returns:
            Dict[str, Any]: 遊戲狀態
        """
        # 基本遊戲信息
        state = {
            "day": self.day,
            "phase": self.phase,
            "players": [],
            "current_discussions": self.current_discussions,
            "last_night_deaths": [],
            "game_over": self.game_over,
            "winner": self.winner
        }
        
        # 添加所有玩家的公開信息
        for player in self.players:
            player_info = {
                "player_id": player["player_id"],
                "name": player["name"],
                "is_alive": player["is_alive"]
            }
            
            # 只有自己能看到自己的角色
            if player["player_id"] == player_id:
                player_info["role"] = player["role"]
            
            # 狼人可以看到其他狼人的身份
            elif self._is_werewolf(player_id) and player["role"] == "werewolf":
                player_info["role"] = "werewolf"
            
            state["players"].append(player_info)
        
        # 死亡信息
        for death in self.last_night_deaths:
            death_info = {
                "player_id": death["player_id"],
                "name": death["name"],
                "role": death["role"]
            }
            state["last_night_deaths"].append(death_info)
        
        return state
    
    def _is_werewolf(self, player_id: int) -> bool:
        """檢查玩家是否是狼人
        
        Args:
            player_id (int): 玩家 ID
            
        Returns:
            bool: 是否是狼人
        """
        player = next((p for p in self.players if p["player_id"] == player_id), None)
        return player is not None and player["role"] == "werewolf"
    
    def add_log(self, message: str):
        """添加日誌
        
        Args:
            message (str): 日誌訊息
        """
        self.log.append(message)
        print(f"[遊戲日誌] {message}")
    
    def save_game(self, filename: str):
        """保存遊戲狀態到文件
        
        Args:
            filename (str): 文件名
        """
        # 創建可序列化的遊戲狀態
        state = {
            "day": self.day,
            "phase": self.phase,
            "players": self.players,
            "current_discussions": self.current_discussions,
            "votes": self.votes,
            "night_actions": self.night_actions,
            "last_night_deaths": self.last_night_deaths,
            "game_over": self.game_over,
            "winner": self.winner,
            "log": self.log
        }
        
        # 保存到文件
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
    
    @classmethod
    def load_game(cls, filename: str):
        """從文件加載遊戲狀態
        
        Args:
            filename (str): 文件名
            
        Returns:
            GameState: 加載的遊戲狀態
        """
        # 檢查文件是否存在
        if not os.path.exists(filename):
            raise FileNotFoundError(f"文件 {filename} 不存在")
        
        # 從文件加載
        with open(filename, 'r', encoding='utf-8') as f:
            state_data = json.load(f)
        
        # 創建新的遊戲狀態實例
        game_state = cls()
        
        # 設置基本狀態
        game_state.day = state_data.get("day", 0)
        game_state.phase = state_data.get("phase", "setup")
        game_state.players = state_data.get("players", [])
        game_state.current_discussions = state_data.get("current_discussions", [])
        game_state.votes = state_data.get("votes", {})
        game_state.night_actions = state_data.get("night_actions", {})
        game_state.last_night_deaths = state_data.get("last_night_deaths", [])
        game_state.game_over = state_data.get("game_over", False)
        game_state.winner = state_data.get("winner")
        game_state.log = state_data.get("log", [])
        
        # 重新創建玩家對象
        from roles import Villager, Werewolf, Seer
        
        werewolf_ids = []
        for player in game_state.players:
            player_id = player["player_id"]
            name = player["name"]
            role = player["role"]
            
            # 創建相應的角色對象
            if role == "werewolf":
                player_obj = Werewolf(player_id, name)
                werewolf_ids.append(player_id)
                game_state.player_objects[player_id] = player_obj
            elif role == "seer":
                player_obj = Seer(player_id, name)
                game_state.player_objects[player_id] = player_obj
            else:  # 普通村民
                player_obj = Villager(player_id, name)
                game_state.player_objects[player_id] = player_obj
            
            # 設置存活狀態
            if not player["is_alive"]:
                player_obj.is_alive = False
        
        # 設置狼人的隊友
        for werewolf_id in werewolf_ids:
            werewolf = game_state.player_objects[werewolf_id]
            werewolf.set_teammates([wid for wid in werewolf_ids if wid != werewolf_id])
        
        return game_state
