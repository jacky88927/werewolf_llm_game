from .base_role import BaseRole

class Werewolf(BaseRole):
    """狼人角色"""
    
    def __init__(self, player_id, name=None):
        """初始化狼人角色
        
        Args:
            player_id (int): 玩家 ID
            name (str, optional): 玩家名稱
        """
        super().__init__(player_id, name)
        self.role_name = "狼人"
        self.team = "狼人陣營"
        self.teammates = []  # 其他狼人隊友的ID列表
    
    def set_teammates(self, teammate_ids):
        """設置狼人隊友
        
        Args:
            teammate_ids (list): 其他狼人的 ID 列表
        """
        self.teammates = teammate_ids
    
    async def night_action(self, game_state, api_handler):
        """夜晚行動 - 選擇一名玩家攻擊
        
        Args:
            game_state (dict): 當前遊戲狀態
            api_handler: API 處理程序
            
        Returns:
            dict: 行動結果，包含目標玩家 ID
        """
        # 只有當狼群中的首領狼人才能做出決定
        if not self._is_alpha_werewolf(game_state):
            return {"action": "wait", "target": None, "result": None}
        
        # 構建夜間行動提示
        prompt = self._build_night_action_prompt(game_state)
        
        # 使用 API 獲取決策
        system_message = f"""你是一名狼人殺遊戲中的狼人角色，名字是{self.name}。
現在是夜晚，你需要選擇一名玩家進行攻擊。
作為狼人首領，你要做出最有利於狼人陣營的決策。"""
        
        response = await api_handler.get_response(prompt, system_message)
        
        # 解析響應以獲取目標玩家 ID
        try:
            # 嘗試找到數字ID引用
            import re
            target_ids = re.findall(r'玩家(\d+)', response)
            if target_ids:
                target_id = int(target_ids[0])
                # 確保是有效的存活玩家且不是狼人
                valid_targets = [p for p in game_state["players"] 
                               if p["is_alive"] and p["player_id"] not in [self.player_id] + self.teammates]
                if any(p["player_id"] == target_id for p in valid_targets):
                    return {"action": "attack", "target": target_id, "result": None}
            
            # 如果沒有找到有效的ID，隨機選擇一個
            import random
            valid_targets = [p for p in game_state["players"] 
                           if p["is_alive"] and p["player_id"] not in [self.player_id] + self.teammates]
            if valid_targets:
                target = random.choice(valid_targets)
                return {"action": "attack", "target": target["player_id"], "result": None}
            return {"action": "wait", "target": None, "result": "無有效目標"}
        except Exception as e:
            # 出錯時返回等待
            return {"action": "wait", "target": None, "result": f"錯誤：{str(e)}"}
    
    async def day_discussion(self, game_state, api_handler):
        """白天討論
        
        Args:
            game_state (dict): 當前遊戲狀態
            api_handler: API 處理程序
            
        Returns:
            str: 討論發言
        """
        # 構建討論提示
        prompt = self._build_discussion_prompt(game_state)
        
        # 使用 API 獲取發言
        system_message = f"""你是一名狼人殺遊戲中的狼人角色，名字是{self.name}，正在偽裝成村民。
你的目標是生存並消滅所有村民。
記住，你必須偽裝成村民，不要暴露自己是狼人。
試著指控其他無辜的村民，保護自己和狼人同伴。"""
        
        response = await api_handler.get_response(prompt, system_message, temperature=0.9, max_tokens=300)
        return response
    
    def _is_alpha_werewolf(self, game_state):
        """判斷是否是首領狼人（狼群中ID最小的存活狼人）
        
        Args:
            game_state (dict): 當前遊戲狀態
            
        Returns:
            bool: 是否是首領狼人
        """
        alive_werewolves = [self.player_id] + [wid for wid in self.teammates 
                                            if any(p["player_id"] == wid and p["is_alive"] 
                                                 for p in game_state["players"])]
        return self.player_id == min(alive_werewolves) if alive_werewolves else False
    
    def _build_night_action_prompt(self, game_state):
        """構建夜間行動提示
        
        Args:
            game_state (dict): 當前遊戲狀態
            
        Returns:
            str: 夜間行動提示
        """
        prompt = f"現在是狼人殺遊戲的第{game_state['day']}天夜晚，狼人行動階段。\n\n"
        
        # 添加遊戲現狀
        prompt += "遊戲現狀：\n"
        prompt += f"- 你是狼人首領，需要决定今晚攻擊的目標\n"
        
        # 添加狼人同伴信息
        if self.teammates:
            alive_teammates = [tid for tid in self.teammates 
                              if any(p["player_id"] == tid and p["is_alive"] for p in game_state["players"])]
            if alive_teammates:
                prompt += "- 你的狼人同伴：\n"
                for tid in alive_teammates:
                    teammate = next((p for p in game_state["players"] if p["player_id"] == tid), None)
                    if teammate:
                        prompt += f"  - 玩家{tid}（{teammate['name']}）\n"
        
        # 添加可選目標
        prompt += "\n可選的攻擊目標：\n"
        for player in game_state["players"]:
            if (player["is_alive"] and player["player_id"] != self.player_id 
                and player["player_id"] not in self.teammates):
                prompt += f"- 玩家{player['player_id']}（{player['name']}）\n"
        
        # 添加遊戲歷史上下文
        prompt += "\n遊戲歷史：\n"
        for event in self.game_history[-10:]:  # 只使用最近的10個事件
            prompt += f"- {event}\n"
        
        prompt += "\n請選擇一名玩家作為今晚的攻擊目標。考慮誰可能是重要角色（如預言家、女巫），以及如何製造混亂。回答格式：'我選擇攻擊玩家X'，其中X是玩家ID。"
        
        return prompt
    
    def _build_discussion_prompt(self, game_state):
        """構建討論提示
        
        Args:
            game_state (dict): 當前遊戲狀態
            
        Returns:
            str: 討論提示
        """
        prompt = f"現在是狼人殺遊戲的第{game_state['day']}天，白天討論階段。\n\n"
        
        # 添加遊戲現狀
        prompt += "遊戲現狀：\n"
        prompt += f"- 存活玩家：{len([p for p in game_state['players'] if p['is_alive']])}人\n"
        prompt += f"- 昨晚死亡：{game_state['last_night_deaths'] or '無'}\n"
        
        # 添加狼人同伴信息
        if self.teammates:
            alive_teammates = [tid for tid in self.teammates 
                              if any(p["player_id"] == tid and p["is_alive"] for p in game_state["players"])]
            if alive_teammates:
                prompt += "- 你的狼人同伴：\n"
                for tid in alive_teammates:
                    teammate = next((p for p in game_state["players"] if p["player_id"] == tid), None)
                    if teammate:
                        prompt += f"  - 玩家{tid}（{teammate['name']}）\n"
        
        # 添加遊戲歷史
        prompt += "\n遊戲歷史：\n"
        for event in self.game_history[-15:]:  # 只使用最近的15個事件
            prompt += f"- {event}\n"
        
        # 添加今天已有的討論
        if game_state["current_discussions"]:
            prompt += "\n今天的討論：\n"
            for discussion in game_state["current_discussions"]:
                prompt += f"- {discussion['player_name']}（玩家{discussion['player_id']}）說：「{discussion['content']}」\n"
        
        prompt += "\n請以第一人稱發表你的看法和分析，偽裝成村民，試圖找出'狼人'（當然不是你自己）。你的發言應該看起來像是一個熱心的村民在分析局勢，但實際上你的目標是誤導其他玩家，保護自己和狼人同伴。"
        
        return prompt
