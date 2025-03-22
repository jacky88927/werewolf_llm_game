import customtkinter as ctk
from .constants import COLORS

def setup_theme():
    """配置 CustomTkinter 主題和外觀"""
    # 設置外觀模式 (系統, 亮色或暗色)
    ctk.set_appearance_mode("light")
    
    # 設置默認的顏色主題
    ctk.set_default_color_theme("blue")
    
    # 自定義顏色主題
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = COLORS["primary"]
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = COLORS["primary_light"]
    ctk.ThemeManager.theme["CTkButton"]["border_color"] = COLORS["primary"]
    
    # 成功按鈕主題
    ctk.ThemeManager.theme["SuccessButton"] = ctk.ThemeManager.theme["CTkButton"].copy()
    ctk.ThemeManager.theme["SuccessButton"]["fg_color"] = COLORS["success"]
    ctk.ThemeManager.theme["SuccessButton"]["hover_color"] = "#66bb6a"  # 較亮的綠色
    
    # 警告按鈕主題
    ctk.ThemeManager.theme["WarningButton"] = ctk.ThemeManager.theme["CTkButton"].copy()
    ctk.ThemeManager.theme["WarningButton"]["fg_color"] = COLORS["warning"]
    ctk.ThemeManager.theme["WarningButton"]["hover_color"] = "#ffb74d"  # 較亮的橙色
    
    # 標籤框主題
    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = COLORS["background"]
    ctk.ThemeManager.theme["CTkFrame"]["top_fg_color"] = COLORS["background"]
    
    # 為標籤設置顏色
    ctk.ThemeManager.theme["CTkLabel"]["text_color"] = COLORS["text"]
    ctk.ThemeManager.theme["CTkLabel"]["fg_color"] = "transparent"
    
    # 文本框主題
    ctk.ThemeManager.theme["CTkTextbox"]["fg_color"] = "#ffffff"
    ctk.ThemeManager.theme["CTkTextbox"]["border_color"] = COLORS["text_secondary"]

# 創建自定義的主題類別
class ThemeStyles:
    """提供自定義應用風格的靜態方法"""
    
    @staticmethod
    def card_frame():
        """卡片式框架風格"""
        return {
            "fg_color": COLORS["card"],
            "corner_radius": 10,
            "border_width": 1,
            "border_color": "#e0e0e0"
        }
    
    @staticmethod
    def header_label():
        """標題標籤風格"""
        return {
            "font": ("Arial", 14, "bold"),
            "text_color": COLORS["primary"]
        }
    
    @staticmethod
    def section_label():
        """區段標題標籤風格"""
        return {
            "font": ("Arial", 12, "bold"),
            "text_color": COLORS["text"]
        }
    
    @staticmethod
    def success_button():
        """綠色成功按鈕風格"""
        return {
            "fg_color": COLORS["success"],
            "hover_color": "#66bb6a",
            "text_color": "white",
            "corner_radius": 6,
            "font": ("Arial", 12, "bold")
        }
    
    @staticmethod
    def warning_button():
        """橙色警告按鈕風格"""
        return {
            "fg_color": COLORS["warning"],
            "hover_color": "#ffb74d",
            "text_color": "white",
            "corner_radius": 6
        }
    
    @staticmethod
    def normal_button():
        """標準藍色按鈕風格"""
        return {
            "fg_color": COLORS["primary"],
            "hover_color": COLORS["primary_light"],
            "text_color": "white",
            "corner_radius": 6
        }
    
    @staticmethod
    def small_button():
        """小型按鈕風格"""
        return {
            "fg_color": COLORS["primary"],
            "hover_color": COLORS["primary_light"],
            "text_color": "white",
            "corner_radius": 4,
            "font": ("Arial", 10)
        }
