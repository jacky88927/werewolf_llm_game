# 使用指南

本文檔提供了狼人殺 LLM 遊戲的詳細使用說明。

## 命令行參數

遊戲支持以下命令行參數：

- `--players` 或 `-p`：設置玩家總數（包括狼人和村民），默認為 8
- `--werewolves` 或 `-w`：設置狼人數量，默認為 2
- `--max-days` 或 `-d`：設置最大遊戲天數，默認為 10
- `--special` 或 `-s`：設置特殊角色，用逗號分隔，例如 `seer,witch,hunter`
- `--human` 或 `-h`：設置由真人玩家控制的角色 ID，用逗號分隔，例如 `1,3,5`
- `--api` 或 `-a`：設置使用的 API 類型，可選 `openai`、`anthropic` 或 `mixed`（默認）
- `--model` 或 `-m`：設置使用的模型名稱
- `--load` 或 `-l`：載入保存的遊戲狀態

## 使用範例

### 基本用法

```bash
python main.py
```

這將啟動一個 8 玩家（包括 2 狼人）的遊戲，使用混合 API 模式。

### 自定義遊戲設置

```bash
python main.py --players 10 --werewolves 3 --special seer,witch,hunter,guard --max-days 15
```

這將啟動一個 10 玩家（包括 3 狼人）的遊戲，特殊角色有預言家、女巫、獵人和守衛，最大遊戲天數為 15。

### 使用特定 API 和模型

```bash
python main.py --api openai --model gpt-4
```

這將使用 OpenAI 的 GPT-4 模型運行遊戲。

### 真人玩家參與

```bash
python main.py --players 6 --human 1,3
```

這將啟動一個 6 玩家的遊戲，其中玩家 1 和玩家 3 由真人控制，其他由 LLM 控制。

### 載入保存的遊戲

```bash
python main.py --load game_results/game_state_20250322_123456.json
```

這將從保存的文件繼續遊戲。

## 控制台命令

在遊戲運行過程中，你可以在真人玩家回合使用以下命令：

- `/help` - 顯示幫助信息
- `/status` - 顯示當前遊戲狀態
- `/players` - 列出所有玩家
- `/quit` - 退出遊戲

## 角色能力說明

### 村民陣營

- **村民**：沒有特殊能力，但可以參與討論和投票。目標是找出並放逐狼人。

- **預言家**：每晚可以查看一名玩家的真實身份。預言家知道誰是狼人是村民陣營的重要優勢。

- **女巫**：擁有一瓶救藥和一瓶毒藥。救藥可以救活一名被狼人殺死的玩家，毒藥可以毒死一名玩家。每種藥只能使用一次。

- **獵人**：當獵人被狼人殺死或被投票放逐時，可以選擇開槍射殺一名玩家。

- **守衛**：每晚可以保護一名玩家不被狼人殺害。守衛不能連續兩晚保護同一名玩家。

- **白痴**：白天投票時，即使得票最高也不會被放逐（但身份會公開）。

- **長老**：可以承受狼人的第一次攻擊而不死亡。第二次被攻擊時將死亡。

- **狼殺手**：屬於村民陣營，但知道狼人身份並可與狼人一同行動。夜晚可以選擇殺死一名狼人。

- **通靈師**：每天早上可以得知被放逐玩家的真實身份。

- **魔術師**：每晚可以選擇交換兩名玩家的位置，使得狼人的攻擊目標改變。

### 狼人陣營

- **狼人**：每晚可以共同選擇一名玩家進行攻擊。狼人之間知道彼此的身份，並能在夜晚交流。

## 遊戲流程

1. **角色分配**：遊戲開始時，每個玩家被隨機分配角色。

2. **夜晚階段**：
   - 狼人選擇一名玩家攻擊
   - 預言家選擇一名玩家查看身份
   - 女巫決定是否使用藥水
   - 守衛選擇一名玩家保護
   - 其他特殊角色使用各自能力

3. **白天階段**：
   - 公布夜晚死亡情況
   - 所有存活玩家自由發言討論
   - 投票決定放逐誰

4. **特殊情況**：
   - 如果獵人或白痴被放逐，觸發其特殊能力
   - 如果預言家、女巫等關鍵角色死亡，對局面會產生重大影響

5. **遊戲結束**：
   - 當所有狼人被放逐時，村民陣營獲勝
   - 當狼人數量等於或超過村民數量時，狼人陣營獲勝
   - 當達到最大天數限制時，遊戲強制結束，根據當時狼人和村民的數量決定勝負

## 保存與載入

遊戲會在每天結束後自動將當前狀態保存到 `game_results` 目錄。你可以使用 `--load` 參數載入保存的遊戲狀態繼續遊戲。