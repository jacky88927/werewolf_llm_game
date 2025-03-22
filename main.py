"""狼人殺 LLM 游戲主程序"""
import os
import sys

# 配置日誌輸出
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    """主程序入口"""
    try:
        # 將當前目錄添加到 Python 路徑
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if current_dir not in sys.path:
            sys.path.insert(0, current_dir)
            logging.info(f"已將 {current_dir} 添加到 Python 路徑")
        
        # 導入必要模塊
        try:
            import customtkinter
            from PIL import Image, ImageTk
            logging.info("必要的模塊導入成功")
        except ImportError as e:
            print(f"錯誤: 缺少必要的依賴項。請執行 'pip install customtkinter pillow'\n詳細信息: {e}")
            return 1
        
        # 導入應用程序
        try:
            from gui.app import WerewolfApp
            logging.info("應用程序導入成功")
        except ImportError as e:
            print(f"錯誤: 無法導入應用程序。\n詳細信息: {e}")
            return 1
        
        # 創建應用
        app = WerewolfApp()
        
        # 運行應用
        app.mainloop()
        
        return 0
    except Exception as e:
        import traceback
        print(f"運行程序時發生錯誤:\n{traceback.format_exc()}")
        return 1

if __name__ == "__main__":
    sys.exit(main())