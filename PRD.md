# Product Requirements Document (PRD)
## hub - AI Development TUI

### Project Overview
A terminal-based unified workspace for AI-assisted development, combining git management, AI coding assistants, and shell access in a single, customizable interface.

**Target Platform:** Linux (Arch Linux first)  
**Target User:** Personal use first, then community release  
**Development Language:** Python

---

## Core Features

### 1. Three-Panel Layout

```
┌─────────────────────────────────────────────────────────────┐
│                     Project: ~/my-app                        │
├──────────────────┬──────────────────────┬───────────────────┤
│   Git/Folders    │    AI Assistant      │    Shell/Dev      │
│   (Permanent)    │    (Middle)          │    (Right)        │
│                  │                      │                   │
│ [Toggle: Git]    │ Type CLI name:       │ $ npm run dev     │
│                  │ > claude             │                   │
│ ● Changes (3)    │ > gemini             │ Server started    │
│   modified:      │ > opencode           │                   │
│   - main.py      │                      │                   │
│   - utils.js     │ [AI Output Area]     │ $                 │
│   + new.txt      │                      │                   │
│                  │                      │                   │
│ [Commit] [Push]  │                      │                   │
└──────────────────┴──────────────────────┴───────────────────┘
```

### 2. Left Panel (Git/Folders - Permanent)

**Toggle Modes:**
- Git Status (default)
- Folder Browser

**Git Status View:**
- Show current repository status
- Display modified files
- Display untracked files
- Display staged files (if any)
- Show current branch name
- Show remote status (ahead/behind)
- Show recent commits (last 5)

**Folder Browser View:**
- Tree view of current directory
- Navigate up/down directories from project root
- File/folder highlighting
- File type icons (optional enhancement)

**Actions:**
- Toggle between Git/Folder view (keybinding)
- Select files for commit
- Generate AI commit message
- Commit changes
- Push to remote
- Navigate files/folders

### 3. Middle Panel (AI Assistant)

**Functionality:**
- Text input field to type CLI command name
- Supported CLIs:
  - `claude` (Claude Code)
  - `gemini` (Google Gemini CLI)
  - `opencode` (OpenCode CLI)
- Launch selected AI CLI in this pane
- Display AI output inline
- Persist chat history per project (saved to `.hub/history/`)

**Behavior:**
- Remember last used AI CLI per project
- CLI process runs in this pane
- Support interactive AI sessions
- Scrollable output area

### 4. Right Panel (Shell/Dev)

**Functionality:**
- Standard shell access (bash/zsh/fish based on user's default)
- Full terminal emulation
- Command history per project
- Scrollback buffer

**Future Enhancement:**
- Multiple shell tabs/splits
- Auto-run project-specific startup commands
- Save common commands per project

---

## Git Workflow (Simplified)

### Commit Process:
1. User selects files from left panel (or "commit all")
2. User triggers "generate commit message" action
3. AI analyzes git diff and generates commit message
4. User can:
   - Accept generated message
   - Edit message
   - Regenerate with different AI
5. Commit happens (no staging area)
6. Option to push immediately or separately

### AI Commit Message Generation:
- Use whichever AI CLI is currently active/configured
- Provide 2-3 commit message options
- Follow conventional commits format (feat/fix/docs/etc.)
- Analyze actual code changes from `git diff`

---

## Customization

### Configurable Settings (TOML format):

```toml
[general]
default_ai = "claude"
theme = "default"

[panels]
# Ratios: left:middle:right (must sum to 100)
left_width = 25
middle_width = 40
right_width = 35

[keybindings]
toggle_git_folder = "t"
commit = "c"
push = "p"
quit = "q"
focus_left = "h"
focus_middle = "l"
focus_right = ";"

[git]
auto_push_after_commit = false
show_recent_commits = 5

[ai]
commit_message_options = 3
default_ai = "claude"

[projects.my-app]
last_used_ai = "claude"
startup_commands = ["npm run dev"]
```

**Config Location:** `~/.config/hub/config.toml`

### What's Customizable:
- Panel size ratios (left:middle:right)
- Keybindings
- Default AI CLI
- Theme/colors
- Git behavior (auto-push, commits to show)
- Per-project settings

---

## Keybindings

**Navigation:**
- `h` / `Left Arrow` - Focus left panel
- `l` / `Right Arrow` - Focus middle panel  
- `;` / `Ctrl+Right` - Focus right panel
- `j/k` or `Up/Down` - Navigate items in focused panel
- `Tab` - Cycle through panels

**Actions:**
- `t` - Toggle Git/Folder view (in left panel)
- `c` - Commit with AI message
- `p` - Push to remote
- `Enter` - Select item / Execute
- `?` - Help menu
- `q` - Quit application
- `:` - Command mode (vim-style)

**Both vi-style and arrow keys supported**

---

## Technical Requirements

### Must Have (MVP):
- [x] Three-panel layout
- [x] Git status display
- [x] Folder browser
- [x] AI CLI integration (claude, gemini, opencode)
- [x] Shell panel with full terminal emulation
- [x] AI-generated commit messages
- [x] Simplified git workflow (no staging)
- [x] Panel resizing
- [x] TOML configuration
- [x] Keybindings

### Should Have (Phase 2):
- [ ] Themes/color schemes
- [ ] Multiple shell tabs
- [ ] Project switcher
- [ ] Auto-run startup commands per project
- [ ] Enhanced folder browser (file operations)
- [ ] Git branch management
- [ ] Commit history viewer

### Could Have (Future):
- [ ] Plugin system
- [ ] Remote repository browser
- [ ] Merge conflict resolver
- [ ] Built-in diff viewer
- [ ] AI code review integration
- [ ] Cross-platform support (after Arch Linux is solid)

---

## User Workflow Example

### Typical Development Session:

1. **Launch TUI:**
   ```bash
   cd ~/my-project
   hub
   ```

2. **Start Development:**
   - Right panel: Run dev server (`npm run dev`)
   - Left panel: Shows git status
   - Middle panel: Type `claude` to start Claude Code

3. **Code with AI:**
   - Ask Claude to implement feature in middle panel
   - Watch changes appear in left panel (git status updates)
   - See output in right panel (dev server logs)

4. **Commit Changes:**
   - Press `c` to commit
   - AI generates commit message from diff
   - Choose from 3 options or edit
   - Confirm commit

5. **Push:**
   - Press `p` to push to remote
   - See push status in left panel

6. **Continue Development:**
   - Toggle to folder view (`t`) to browse files
   - Switch AI tools as needed
   - Multiple commits throughout session

---

## Success Metrics

### For Personal Use (Phase 1):
- Daily active use for all development work
- Faster commit workflow than standard git CLI
- Reduced context switching between terminal windows
- Effective AI integration for commits and coding

### For Community Release (Phase 2):
- 100+ GitHub stars in first month
- 10+ community contributions
- 5+ feature requests from users
- Positive feedback on Arch Linux forums/AUR

---

## Out of Scope (For Now)

- GUI version
- Windows/macOS support (Linux first)
- Built-in text editor
- Database integration
- Cloud sync
- Team collaboration features
- CI/CD integration
- Package manager integration

---

## Release Plan

### Phase 1: Personal MVP (Arch Linux)
- Core three-panel layout
- Git + Folder views
- AI CLI integration
- Basic commit workflow
- TOML config
- Essential keybindings

### Phase 2: Polish & Features
- Themes
- Multiple shells
- Project switcher
- Enhanced git features
- Better error handling
- Documentation

### Phase 3: Community Release
- AUR package
- GitHub release
- Documentation site
- Installation scripts
- Community feedback integration

---

## Dependencies & Requirements

### System Requirements:
- Arch Linux (kernel 6.x+)
- Python 3.11+
- Git 2.40+
- At least one AI CLI installed:
  - Claude Code
  - Gemini CLI
  - OpenCode CLI

### Python Dependencies:
- See TECH_STACK.md for detailed list

---

## Project Structure

```
hub/
├── src/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── app.py               # Main TUI application
│   ├── panels/
│   │   ├── __init__.py
│   │   ├── git_panel.py     # Left panel
│   │   ├── ai_panel.py      # Middle panel
│   │   └── shell_panel.py   # Right panel
│   ├── git/
│   │   ├── __init__.py
│   │   ├── operations.py    # Git commands
│   │   └── status.py        # Git status parsing
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── cli_manager.py   # AI CLI launcher
│   │   └── commit_gen.py    # Commit message generation
│   ├── config/
│   │   ├── __init__.py
│   │   ├── loader.py        # TOML config loader
│   │   └── defaults.py      # Default config
│   └── utils/
│       ├── __init__.py
│       ├── keybindings.py   # Keyboard handling
│       └── file_tree.py     # Folder browser logic
├── config/
│   └── default.toml         # Default configuration
├── tests/
│   └── ...
├── README.md
├── LICENSE
├── pyproject.toml
├── PRD.md                   # This file
└── TECH_STACK.md
```

---

## Notes

- **Personal first:** Build for your workflow, optimize later for others
- **Arch Linux focus:** Don't worry about cross-platform until it works perfectly on Arch
- **Iterate quickly:** Get MVP working, then polish
- **Keep it simple:** No over-engineering, solve real problems
- **Customization is key:** Your workflow should be YOUR workflow
