import os
import sys
import json
import argparse
from rich.console import Console
from rich.table import Table

def analyze_game(game_file: str):
    """分析遊戲結果
    
    Args:
        game_file (str): 遊戲結果文件路徑
    """
    # 檢查文件是否存在
    if not os.path.exists(game_file):
        print(f"錯誤：文件 {game_file} 不存在")
        return 1
    
    # 讀取遊戲結果
    with open(game_file, 'r', encoding='utf-8') as f:
        game_data = json.load(f)
    
    # 創建控制台對象
    console = Console()
    
    # 打印遊戲基本信息
    console.print(f"[bold cyan]===== 遊戲分析 =====")
    console.print(f"[bold]遊戲天數：[/bold]{game_data.get('day', 0)}")
    console.print(f"[bold]遊戲階段：[/bold]{game_data.get('phase', 'unknown')}")
    console.print(f"[bold]遊戲結束：[/bold]{'是' if game_data.get('game_over', False) else '否'}")
    console.print(f"[bold]獲勝者：[/bold]{game_data.get('winner', '無')}")
    
    # 創建玩家信息表格
    player_table = Table(title="玩家信息")
    player_table.add_column("ID", justify="center")
    player_table.add_column("名稱", justify="left")
    player_table.add_column("角色", justify="center")
    player_table.add_column("陣營", justify="center")
    player_table.add_column("狀態", justify="center")
    
    # 添加玩家信息
    for player in game_data.get("players", []):
        player_id = player.get("player_id", "?")
        name = player.get("name", "未知")
        role = player.get("role", "未知")
        team = "狼人陣營" if role == "werewolf" else "村民陣營"
        status = "存活" if player.get("is_alive", False) else "死亡"
        
        # 設置顏色
        role_color = "[red]" if role == "werewolf" else "[green]"
        status_color = "[green]" if status == "存活" else "[red]"
        
        player_table.add_row(
            str(player_id),
            name,
            f"{role_color}{role}[/]",
            f"{role_color}{team}[/]",
            f"{status_color}{status}[/]"
        )
    
    console.print(player_table)
    
    # 打印遊戲日誌
    console.print("\n[bold cyan]遊戲日誌：")
    for i, log in enumerate(game_data.get("log", [])):
        console.print(f"{i+1:3d}. {log}")
    
    return 0

def main():
    """主程序入口"""
    # 解析命令行參數
    parser = argparse.ArgumentParser(description="狼人殺遊戲結果分析器")
    parser.add_argument("game_file", help="遊戲結果文件路徑")
    
    args = parser.parse_args()
    
    # 分析遊戲
    return analyze_game(args.game_file)

if __name__ == "__main__":
    # 運行主程序
    exit_code = main()
    sys.exit(exit_code)
