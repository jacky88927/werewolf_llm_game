# 🐺 Werewolf LLM Game

A technical implementation of the Werewolf (Mafia) party game using Large Language Models (LLMs). This project allows LLMs to play against each other by assuming different roles and communicating through API interactions.

## 🔍 Technical Overview

This project demonstrates the capabilities of LLMs in a complex social deduction game environment, requiring strategic thinking, deception, and logical reasoning.

## 🏗️ Project Architecture

- `/api` - 🔌 API connectors for different LLM providers
  - Handles authentication and request formatting
  - Implements rate limiting and error handling
  - Provides abstraction layers for different LLM providers
  
- `/game` - ⚙️ Core game logic and flow control
  - Game state management
  - Turn sequence handling
  - Event processing system
  - Game rule enforcement

- `/gui` - 🖥️ Graphical user interface
  - Built with CustomTkinter
  - Real-time game visualization
  - Interaction panels for human players
  - Game logging and status displays

- `/roles` - 👥 Role definitions and behaviors
  - Role-specific action handlers
  - Special ability implementations
  - Base classes for role inheritance
  - Role balance parameters

- `/utils` - 🛠️ Utility functions and helpers
  - Text processing utilities
  - Configuration management
  - Logging infrastructure
  - Random generation with controlled seed

## 💻 Technical Implementation

### 🔧 Environment Configuration

1. Requires Python 3.8+ runtime environment.

2. Dependencies installation:
   ```
   pip install -r requirements.txt
   ```

3. API key configuration in `.env` file based on the `.env.example` template.

### ✨ Technical Features

- **🧠 Multi-LLM Orchestration**: Manages multiple concurrent LLM instances with different system prompts
- **💾 Memory Management**: Implements conversation history handling with context window optimization
- **📝 Prompt Engineering**: Specialized prompts for different game phases and roles
- **👤 Hybrid Player Support**: Seamless integration of human and AI players in the same game
- **💾 State Persistence**: Game state serialization and save/load functionality
- **🎨 Custom GUI Framework**: Dedicated interface with real-time updates

### 🔬 Implementation Details

The core engine utilizes a turn-based state machine pattern, with event handlers for different game phases. The communication between players is managed through a centralized message broker that handles the formatting and delivery of information based on player roles and game state.

Special attention has been given to prompt design to ensure LLMs can:
- Understand the game state based on partial information
- Make strategic decisions within their role constraints
- Reason about other players' possible roles
- Communicate in natural language during discussions

## 🤖 Supported LLM Models

- **OpenAI**: GPT-4, GPT-4o, GPT-4-Turbo, GPT-3.5-Turbo
- **Anthropic**: Claude-3-Opus, Claude-3.5-Sonnet, Claude-3-Sonnet, Claude-3-Haiku

## 📋 Technical Notes

- 💰 API costs vary depending on token usage and model selection
- 📊 Game results and logs are stored in the `game_results` directory
- 📈 Performance metrics are available for analysis of model behavior
- ⚙️ Role-specific behaviors can be customized via configuration files
