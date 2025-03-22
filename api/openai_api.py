import os
from openai import OpenAI

class OpenAIHandler:
    """處理與 OpenAI API 的交互"""
    
    def __init__(self, model="gpt-4"):
        """初始化 OpenAI API 處理器
        
        Args:
            model (str): 要使用的 OpenAI 模型名稱
        """
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("缺少 OPENAI_API_KEY 環境變數")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
    
    async def get_response(self, prompt, system_message=None, temperature=0.7, max_tokens=500):
        """從 OpenAI API 獲取回應
        
        Args:
            prompt (str): 要發送給模型的提示
            system_message (str, optional): 系統消息。默認為 None
            temperature (float, optional): 溫度參數。默認為 0.7
            max_tokens (int, optional): 最大生成標記數。默認為 500
            
        Returns:
            str: 模型的回應文本
        """
        messages = []
        
        if system_message:
            messages.append({"role": "system", "content": system_message})
        
        messages.append({"role": "user", "content": prompt})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
