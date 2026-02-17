# Tech Stack Document
## hub - AI Development TUI

---

## Core Technology

### Language
**Python 3.11+**

**Rationale:**
- Fast development iteration
- Excellent TUI libraries available
- Great subprocess management for AI CLIs
- Rich ecosystem for git operations
- You're familiar with it and currently mobile

---

## TUI Framework

### Primary: Textual (v0.47+)
**Repository:** https://github.com/Textualize/textual

**Why Textual:**
- Modern, batteries-included TUI framework
- Built-in layout system (perfect for three panels)
- Rich widgets and styling
- Reactive programming model
- Excellent documentation
- Active development by Textualize (creators of Rich)
- CSS-like styling for theming
- Built-in widget library (containers, buttons, inputs, etc.)
- Keyboard handling out of the box
- Cross-platform terminal support

**Key Features We'll Use:**
- `Horizontal` / `Vertical` containers for layout
- `Static` widget for git status display
- `Input` widget for AI CLI commands
- Custom widgets for shell emulation
- `DirectoryTree` for folder browser
- CSS for panel sizing and themes
- Message passing between panels
- Keyboard bindings system

**Alternative Considered:**
- `rich` + `prompt_toolkit`: More manual work, we'd have to build everything
- **Decision:** Textual is better for complex layouts

---

## Git Integration

### GitPython (v3.1+)
**Repository:** https://github.com/gitpython-developers/GitPython

**Why GitPython:**
- Pythonic Git interface
- Don't need to parse raw git commands
- Get structured data (diffs, status, branches)
- Handle git operations safely
- Good error handling

**Usage:**
```python
from git import Repo

repo = Repo('/path/to/project')
# Get status
status = repo.git.status()
# Get changed files
changed = repo.index.diff(None)
# Commit
repo.index.commit("AI generated message")
# Push
origin = repo.remote('origin')
origin.push()
```

**Alternative:**
- Raw `subprocess` calls to git CLI
- **Decision:** GitPython is cleaner and safer

---

## Configuration Management

### tomli (Python 3.11+ built-in) + tomli_w
**tomli:** https://github.com/hukkin/tomli (built into Python 3.11+ as `tomllib`)  
**tomli_w:** https://github.com/hukkin/tomli-w (for writing TOML)

**Why TOML:**
- Human-readable
- Popular in modern dev tools (Rust, Python projects)
- Clean syntax for nested config
- Type-safe parsing
- Comments support

**Config Structure:**
```toml
[general]
default_ai = "claude"
theme = "default"

[panels]
left_width = 25
middle_width = 40
right_width = 35

[keybindings]
toggle_git_folder = "t"
commit = "c"
# ... etc
```

**Usage:**
```python
import tomllib  # Python 3.11+
import tomli_w

# Read config
with open('config.toml', 'rb') as f:
    config = tomllib.load(f)

# Write config
with open('config.toml', 'wb') as f:
    tomli_w.dump(config, f)
```

---

## Shell/Terminal Emulation

### Pyte (v0.8+)
**Repository:** https://github.com/selectel/pyte

**Why Pyte:**
- Terminal emulator in pure Python
- Handles ANSI escape sequences
- Virtual screen that we can render in Textual
- Perfect for embedding shell in our TUI

**Usage:**
```python
import pyte

screen = pyte.Screen(80, 24)
stream = pyte.Stream(screen)
stream.feed(terminal_output)
# Render screen.display in our TUI
```

**Alternative Approach:**
- Use `pty` module + subprocess
- Capture and render output directly
- **Decision:** Start simple with subprocess, add Pyte if needed for complex terminal features

---

## Process Management

### subprocess (Python stdlib)
**For launching AI CLIs and shell commands**

```python
import subprocess
import pty
import os

# Launch AI CLI
process = subprocess.Popen(
    ['claude'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# For interactive shell
master, slave = pty.openpty()
shell = subprocess.Popen(
    [os.environ.get('SHELL', '/bin/bash')],
    stdin=slave,
    stdout=slave,
    stderr=slave
)
```

---

## AI Integration

### Direct CLI Calls
**No additional libraries needed**

**Supported AI CLIs:**
1. **Claude Code:** `claude`
2. **Gemini CLI:** `gemini`
3. **OpenCode CLI:** `opencode`

**Integration Method:**
- Launch via subprocess
- Capture stdout/stderr
- Send commands via stdin
- Display output in middle panel

**For Commit Message Generation:**
```python
# Get git diff
diff = repo.git.diff()

# Send to AI CLI
prompt = f"Generate a commit message for these changes:\n{diff}"
result = subprocess.run(
    ['claude', '--prompt', prompt],
    capture_output=True,
    text=True
)
commit_message = result.stdout.strip()
```

---

## File System Operations

### pathlib (Python stdlib)
**For folder navigation and file operations**

```python
from pathlib import Path

project_root = Path.cwd()
files = list(project_root.rglob('*.py'))
```

---

## Development Tools

### Package Management
**uv (modern Python package manager)**
**Repository:** https://github.com/astral-sh/uv

**Why uv:**
- Blazing fast (written in Rust)
- Drop-in replacement for pip/pip-tools
- Better dependency resolution
- Lock file support
- Perfect for Arch Linux users who like modern tools

**Setup:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv
source .venv/bin/activate
uv pip install -e .
```

**Alternative:** Standard `pip` + `venv` (fallback for compatibility)

### Project Structure: pyproject.toml
```toml
[project]
name = "hub"
version = "0.1.0"
description = "AI-powered development TUI for Linux"
authors = [{name = "Your Name", email = "you@example.com"}]
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "textual>=0.47.0",
    "gitpython>=3.1.0",
    "tomli-w>=1.0.0",
    "pyte>=0.8.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-asyncio>=0.21.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]

[project.scripts]
hub = "hub.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.black]
line-length = 88
target-version = ['py311']

[tool.ruff]
line-length = 88
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true
```

### Testing Framework
**pytest + pytest-asyncio**

**Why pytest:**
- De facto standard for Python testing
- Great for async code (Textual is async)
- Excellent fixtures and parametrization
- Good coverage reporting

### Code Quality

**Black (Code Formatter):**
- Opinionated, no configuration needed
- Consistent code style

**Ruff (Linter):**
- Extremely fast (Rust-based)
- Replaces flake8, isort, pyupgrade
- Catches bugs and style issues

**mypy (Type Checker):**
- Static type checking
- Catch type errors before runtime
- Especially useful for larger codebase

---

## System Dependencies (Arch Linux)

### Required Packages:
```bash
# Core
sudo pacman -S python python-pip git

# Python development
sudo pacman -S python-virtualenv python-setuptools

# Terminal support (if needed)
sudo pacman -S ncurses

# AI CLIs (user installs these separately)
# - Claude Code: https://claude.ai/download
# - Gemini CLI: npm install -g @google/generative-ai-cli
# - OpenCode: pip install opencode-cli
```

### Optional (Development):
```bash
sudo pacman -S python-pytest python-black
```

---

## Deployment Strategy

### Phase 1: Development
**Local installation:**
```bash
git clone https://github.com/yourusername/chell.git
cd chell
uv venv
source .venv/bin/activate
uv pip install -e .
chell
```

### Phase 2: AUR Package
**Create AUR package for easy Arch installation**

**PKGBUILD structure:**
```bash
# Maintainer: Your Name <you@example.com>
pkgname=hub
pkgver=0.1.0
pkgrel=1
pkgdesc="AI-powered development TUI for Linux"
arch=('any')
url="https://github.com/yourusername/hub"
license=('MIT')
depends=('python>=3.11' 'git')
makedepends=('python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$pkgname-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$pkgname-$pkgver"
    python -m installer --destdir="$pkgdir" dist/*.whl
}
```

**Installation for users:**
```bash
yay -S hub
# or
paru -S hub
```

### Phase 3: PyPI Package
**For non-Arch users**
```bash
pip install hub-tui
```

---

## Development Workflow

### Local Development:
```bash
# Setup
git clone <repo>
cd hub
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Run
hub

# Test
pytest

# Format
black src/
ruff check src/ --fix

# Type check
mypy src/
```

### Git Workflow:
```bash
# Feature branch
git checkout -b feature/ai-commit-messages

# Commit (with your own tool later!)
git commit -m "feat: add AI commit message generation"

# Push
git push origin feature/ai-commit-messages
```

---

## Architecture Decisions

### Why Not Alternatives?

**Rich + prompt_toolkit instead of Textual:**
- ❌ More manual layout management
- ❌ No built-in widget system
- ❌ More boilerplate code
- ✅ Textual handles all this for us

**Rust + ratatui instead of Python + Textual:**
- ❌ Slower development iteration
- ❌ More complex subprocess handling
- ❌ Harder to modify while mobile
- ✅ Python is faster to develop, good enough performance

**Node.js + blessed/ink:**
- ❌ Another language to manage
- ❌ Less mature git libraries
- ❌ You're more comfortable with Python

**Direct ncurses:**
- ❌ Too low-level
- ❌ Would take weeks to build basic UI
- ✅ Textual abstracts this perfectly

---

## Performance Considerations

### Expected Performance:
- **Startup time:** <500ms
- **Git operations:** <100ms for status, <1s for large repos
- **UI responsiveness:** 60 FPS refresh rate
- **Memory usage:** <100MB typical

### Optimization Strategy:
1. **Lazy loading:** Don't load folder tree until requested
2. **Caching:** Cache git status for 1 second
3. **Async operations:** Use Textual's async features for long-running tasks
4. **Subprocess pooling:** Reuse shell processes

### Bottlenecks to Watch:
- Large git repositories (thousands of files)
- AI CLI response times (out of our control)
- Terminal rendering for massive shell output

---

## Security Considerations

### Git Operations:
- Never execute arbitrary shell commands
- Use GitPython's safe API
- Validate file paths before operations

### AI CLI Integration:
- Don't expose sensitive data in prompts
- Don't auto-commit without user review
- Clear AI history if it contains secrets

### Config Files:
- Don't store API keys in config
- Use environment variables for sensitive data
- Validate config before parsing

---

## Cross-Platform Future (Out of Scope for Now)

### When Adding macOS/Windows Support:
- **Terminal differences:** Windows Terminal vs ANSI terminals
- **Path handling:** Use `pathlib` consistently (already cross-platform)
- **Shell detection:** Detect PowerShell vs bash/zsh
- **Package managers:** Homebrew (macOS), winget (Windows)

**For now:** Focus on Arch Linux, make it amazing there first.

---

## Monitoring & Debugging

### Logging:
**Python's logging module**
```python
import logging

logging.basicConfig(
    filename='~/.config/hub/debug.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Debug Mode:
```bash
hub --debug  # Verbose logging
hub --log-file=/tmp/hub.log  # Custom log location
```

---

## Future Tech Considerations

### Potential Additions:

**Database (SQLite):**
- If we add persistent project history
- Store AI chat logs
- Cache git data

**HTTP Client (httpx):**
- If we add API integrations
- Remote repository features
- Update checks

**Rich (terminal formatting):**
- Already part of Textual
- Use for enhanced git diff display
- Syntax highlighting in file preview

---

## Summary: Core Stack

```
Language:        Python 3.11+
TUI Framework:   Textual v0.47+
Git:             GitPython v3.1+
Config:          tomllib (built-in) + tomli_w
Shell:           subprocess + pty (stdlib)
Process Mgmt:    subprocess (stdlib)
File System:     pathlib (stdlib)
Package Mgmt:    uv (or pip as fallback)
Testing:         pytest + pytest-asyncio
Code Quality:    black, ruff, mypy
Platform:        Arch Linux (first)
```

**Philosophy:** Use stdlib where possible, add dependencies only when they provide significant value.

---

## Getting Started Commands

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create project
mkdir hub && cd hub
git init

# Setup Python environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install textual gitpython tomli-w

# Create project structure
mkdir -p src/hub/{panels,git,ai,config,utils}
touch src/hub/__init__.py
touch src/hub/main.py
touch pyproject.toml

# Start coding!
```

Ready to build! 🚀
