from abc import ABC, abstractmethod

class BaseRole(ABC):
    """所有遊戲角色的基本類別"""
    
    def __init__(self, player_id, name=None):
        """初始化角色
        
        Args:
            player_id (int): 玩家 ID
            name (str, optional): 玩家名稱，默認為 None，將使用 "玩家{player_id}"
        """
        self.player_id = player_id
        self.name = name or f"玩家{player_id}"
        self.is_alive = True
        self.role_name = "未知"  # 將由子類覆蓋
        self.team = "未知"  # 將由子類覆蓋（村民陣營或狼人陣營）
        self.game_history = []  # 記錄游戲歷史
    
    def add_history(self, event):
        """添加事件到遊戲歷史記錄
        
        Args:
            event (str): 遊戲事件描述
        """
        self.game_history.append(event)
    
    def get_status(self):
        """獲取角色狀態
        
        Returns:
            dict: 包含角色狀態信息的字典
        """
        return {
            "player_id": self.player_id,
            "name": self.name,
            "role": self.role_name,
            "team": self.team,
            "is_alive": self.is_alive
        }
    
    @abstractmethod
    async def night_action(self, game_state, api_handler):
        """夜晚行動 - 每個角色子類必須實現
        
        Args:
            game_state (dict): 當前遊戲狀態
            api_handler: API 處理程序來獲取 LLM 決策
            
        Returns:
            dict: 行動結果
        """
        pass
    
    @abstractmethod
    async def day_discussion(self, game_state, api_handler):
        """白天討論 - 每個角色子類必須實現
        
        Args:
            game_state (dict): 當前遊戲狀態
            api_handler: API 處理程序來獲取 LLM 決策
            
        Returns:
            str: 討論發言
        """
        pass
    
    async def vote(self, game_state, api_handler):
        """白天投票
        
        Args:
            game_state (dict): 當前遊戲狀態
            api_handler: API 處理程序來獲取 LLM 決策
            
        Returns:
            int: 投票的玩家 ID
        """
        alive_players = [p for p in game_state["players"] if p["is_alive"] and p["player_id"] != self.player_id]
        
        if not alive_players:
            return None
        
        # 構建投票提示
        prompt = self._build_vote_prompt(game_state, alive_players)
        
        # 使用 API 獲取決策
        system_message = f"你是一名狼人殺遊戲中的{self.role_name}角色，名字是{self.name}。請根據遊戲情況做出投票決策。"
        response = await api_handler.get_response(prompt, system_message)
        
        # 解析響應以獲取投票的玩家 ID
        try:
            # 嘗試找到數字ID引用
            import re
            vote_ids = re.findall(r'玩家(\d+)', response)
            if vote_ids:
                vote_id = int(vote_ids[0])
                # 確保是有效的存活玩家
                if any(p["player_id"] == vote_id and p["is_alive"] for p in game_state["players"]):
                    return vote_id
            
            # 如果沒有找到有效的ID，隨機選擇一個
            import random
            return random.choice(alive_players)["player_id"]
        except Exception as e:
            # 出錯時返回第一個存活玩家
            return alive_players[0]["player_id"]
    
    def _build_vote_prompt(self, game_state, alive_players):
        """構建投票提示
        
        Args:
            game_state (dict): 當前遊戲狀態
            alive_players (list): 存活玩家列表
            
        Returns:
            str: 投票提示
        """
        prompt = f"現在是狼人殺遊戲的第{game_state['day']}天，需要進行投票。\n\n"
        
        # 添加遊戲歷史
        prompt += "遊戲歷史：\n"
        for event in self.game_history[-10:]:  # 只使用最近的10個事件
            prompt += f"- {event}\n"
        
        # 添加今天的討論
        prompt += "\n今天的討論：\n"
        for discussion in game_state["current_discussions"]:
            prompt += f"- {discussion['player_name']}（玩家{discussion['player_id']}）說：「{discussion['content']}」\n"
        
        # 添加投票指示
        prompt += "\n請投票選擇你認為最可能是狼人的玩家，僅回答玩家ID即可。可選的玩家：\n"
        for player in alive_players:
            prompt += f"- 玩家{player['player_id']}（{player['name']}）\n"
        
        prompt += "\n請分析並做出決策，回答格式：'我投票給玩家X'，其中X是玩家ID。"
        
        return prompt
