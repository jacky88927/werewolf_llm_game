import os
import anthropic

class AnthropicHandler:
    """處理與 Anthropic API (Claude) 的交互"""
    
    def __init__(self, model="claude-3-opus-20240229"):
        """初始化 Anthropic API 處理器
        
        Args:
            model (str): 要使用的 Anthropic 模型名稱
        """
        self.api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("缺少 ANTHROPIC_API_KEY 環境變數")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = model
    
    async def get_response(self, prompt, system_message=None, temperature=0.7, max_tokens=500):
        """從 Anthropic API 獲取回應
        
        Args:
            prompt (str): 要發送給模型的提示
            system_message (str, optional): 系統消息。默認為 None
            temperature (float, optional): 溫度參數。默認為 0.7
            max_tokens (int, optional): 最大生成標記數。默認為 500
            
        Returns:
            str: 模型的回應文本
        """
        system = system_message or ""
        
        response = self.client.messages.create(
            model=self.model,
            system=system,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.content[0].text
