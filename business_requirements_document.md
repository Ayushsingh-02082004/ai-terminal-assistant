# Business Requirements Document (BRD)
## Project: AI Command Line Agent (CrewAI Terminal Assistant)

**Document Version:** 1.0  
**Prepared For:** Technical Lead / Engineering Management  
**Author:** AI Development Team  
**Status:** Approved for Implementation  

---

## 1. Executive Summary

The **AI Command Line Agent** is an enterprise-grade terminal assistant that integrates Large Language Models (LLMs) directly into developer command-line interfaces. Built on **CrewAI**, **Textual**, and **Python**, the application bridges natural language intent with automated terminal, file system, code editing, and Git execution.

Unlike web-based AI assistants (e.g., ChatGPT) or simple single-script prototypes, this system utilizes a **multi-agent architecture** (Router & Executor), **safety guardrails** (file size limits, syntax validation, execution timeouts), and a **full-screen Terminal User Interface (TUI)** to streamline developer workflows without context switching.

---

## 2. Business Problem & Opportunity

### Problem Statement
1. **Context Switching**: Software engineers lose efficiency switching between the IDE, terminal commands, documentation, and web-based AI interfaces.
2. **Command Memory Burden**: Complex Git workflows, nested search commands, and build scripts require manual memorization or search engine lookup.
3. **Lack of Local Automation Safety**: Raw script-execution tools can lock up terminals, consume infinite tokens, or perform accidental destructive operations.

### Proposed Business Opportunity
Provide a lightweight, local/cloud-hybrid terminal assistant that:
- Runs directly inside developer terminal sessions.
- Automates repetitive shell, file, code, and version control tasks.
- Hides noisy background logs while presenting structured decision cards.
- Operates under strict safety bounds (timeout limits, size bounds, and syntax verification).

---

## 3. High-Level Architecture & Technical Stack

```
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                       User Input (Natural Language)                       │
 └─────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                   Textual TUI Layer (UI & Interception)                   │
 │   - Header & Status Info    - Conversation Cards    - Hidden Debug Log   │
 └─────────────────────────────────────┬─────────────────────────────────────┘
                                       │ Async Worker (@work)
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                       CrewAI Multi-Agent Pipeline                         │
 │                                                                           │
 │   [ Router Agent ]   ──(Intent & Plan)──►   [ Executor Agent ]            │
 │   Classifies prompt                         Executes via Services         │
 └─────────────────────────────────────┬─────────────────────────────────────┘
                                       │
                                       ▼
 ┌───────────────────────────────────────────────────────────────────────────┐
 │                       Service Layer (Safety Wrapped)                      │
 │   - shell_tool (60s Timeout)            - file_tool (<20MB Guard)         │
 │   - code_tool (py_compile Check)        - git_tool (Subprocess Git)       │
 └─────────────────────────────────────┴─────────────────────────────────────┘
```

### Core Technologies:
- **Orchestration Framework**: `CrewAI` (v1.x compatible)
- **Model Integration**: Ollama Cloud / LiteLLM (`qwen3.5:cloud`)
- **User Interface**: `Textual` (Full-screen TUI) + `Rich` (Markdown & Panel styling)
- **Execution Layer**: Python `subprocess`, `os`, `py_compile`

---

## 4. Key Functional Requirements

| ID | Module | Feature Description | Business Value |
|---|---|---|---|
| **FR-01** | **Router Agent** | Analyzes natural language prompts and classifies intent into `Shell`, `File`, `Code`, or `Git` categories. | Prevents model confusion by structuring execution plans before tool execution. |
| **FR-02** | **Executor Agent** | Receives structured tasks and executes actions using specialized toolsets. | Automates complex multi-step tasks reliably. |
| **FR-03** | **Shell Service** | Executes terminal commands (`pip`, `ipconfig`, build tasks) with a strict **60-second timeout**. | Prevents terminal locking and infinite background loops. |
| **FR-04** | **File Service** | Performs `read`, `write`, `append`, `list`, and recursive `find` operations with a **<20MB size guard**. | Prevents high API token consumption and memory crashes from large binary files. |
| **FR-05** | **Code Service** | Performs line-based `search`, exact block `edit`, and Python `check_syntax` (compilation validation). | Ensures code edits do not introduce syntax errors before committing. |
| **FR-06** | **Git Service** | Safely automates local Git operations (`status`, `diff`, `add`, `commit`, `log`, `branch`). | Streamlines developer version control workflows. |
| **FR-07** | **Textual TUI** | Renders full-screen interactive interface with chat history, status headers, and fixed command input. | Provides clean developer experience without web dependencies. |
| **FR-08** | **Debug Drawer** | Intercepts `stdout`, `stderr`, and OTel background logs into a collapsible drawer (`Ctrl+D`). | Eliminates console clutter while keeping trace logs accessible for debugging. |

---

## 5. Non-Functional & Security Requirements

### NFR-01: Performance & Responsiveness
- Agent execution runs asynchronously in background threads (`@work(thread=True)`) to ensure the TUI remaining smooth and responsive.
- Visual loading indicators provide immediate feedback during LLM inference.

### NFR-02: Safety & Reliability
- File operations strictly enforce a 20MB limit.
- Shell command execution is capped at 60 seconds.
- Python syntax checks occur automatically prior to finalizing code modifications.

### NFR-03: Console Compatibility
- Visual outputs use standard ASCII string fallbacks to prevent `UnicodeEncodeError` crashes on legacy Windows consoles.

---

## 6. Competitive Advantage: Prototype vs. Enterprise Solution

| Capability | Single-File Script Prototype (Tutorial) | Our Enterprise CLI Agent (Implementation) |
|---|---|---|
| **Orchestration** | Monolithic single loop with basic tool map | Multi-Agent CrewAI Architecture (Router & Executor separation) |
| **User Interface** | Basic `input()` and `print()` terminal statements | Full-screen Textual TUI with Rich Markdown panels & async workers |
| **Safety Guards** | Unrestricted `subprocess.run` (risk of hanging/deletions) | 60s timeouts, 20MB file bounds, and python syntax compilation checks |
| **Output Cleanliness** | Noisy trace logs and OTel warnings mix with user input | Background logs intercepted and hidden in a toggleable Debug Drawer (`Ctrl+D`) |
| **Extensibility** | Hardcoded Ollama schema dictionary | Modular `services/` package cleanly decoupled from LLM frameworks |

---

## 7. Future Production Roadmap

1. **Sandboxed Execution**: Wrap `shell_tool` execution inside isolated Docker containers (gVisor/WASM).
2. **User Confirmation Gate**: Require developer `[y/N]` confirmation prompts prior to executing destructive commands (e.g. `git push`, file deletions).
3. **Enterprise SSO & Proxying**: Support corporate OAuth logins and centralized LiteLLM API proxy gateways.
