# Coding Agent Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Coding Agent Workshop                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│   User      │───▶│   Go Agent   │───▶│      AIMLAPI            │
│   Input     │    │   (6 Versions)│    │   (Claude Models)       │
└─────────────┘    └──────────────┘    └─────────────────────────┘
                           │
                           ▼
                   ┌──────────────┐
                   │ Tool Registry│
                   │              │
                   │ • read_file  │
                   │ • list_files │
                   │ • run_command│
                   │ • write_file │
                   │ • search_code│
                   └──────────────┘
```

## Version Progression

```
Version 1: chat.go
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│   User      │───▶│   Basic      │───▶│      Claude             │
│   Input     │    │   Chat       │    │   (No Tools)            │
└─────────────┘    └──────────────┘    └─────────────────────────┘

Version 2: read.go
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│   User      │───▶│   Chat +     │───▶│      Claude             │
│   Input     │    │   File Read  │    │   + read_file tool      │
└─────────────┘    └──────────────┘    └─────────────────────────┘

Version 3: list_files.go
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│   User      │───▶│   Chat +     │───▶│      Claude             │
│   Input     │    │   File Tools │    │   + read_file           │
└─────────────┘    └──────────────┘    │   + list_files          │
                                       └─────────────────────────┘

Version 4: bash_tool.go
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│   User      │───▶│   Chat +     │───▶│      Claude             │
│   Input     │    │   File +     │    │   + read_file           │
└─────────────┘    │   Command    │    │   + list_files          │
                   │   Tools      │    │   + run_command         │
                   └──────────────┘    └─────────────────────────┘

Version 5: edit_tool.go
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│   User      │───▶│   Chat +     │───▶│      Claude             │
│   Input     │    │   File +     │    │   + read_file           │
└─────────────┘    │   Command +  │    │   + list_files          │
                   │   Edit Tools │    │   + run_command         │
                   └──────────────┘    │   + write_file          │
                                       └─────────────────────────┘

Version 6: code_search_tool.go
┌─────────────┐    ┌──────────────┐    ┌─────────────────────────┐
│   User      │───▶│   Full       │───▶│      Claude             │
│   Input     │    │   Coding     │    │   + read_file           │
└─────────────┘    │   Agent      │    │   + list_files          │
                   └──────────────┘    │   + run_command         │
                                       │   + write_file          │
                                       │   + search_code         │
                                       └─────────────────────────┘
```

## Tool Execution Flow

```
1. User Input
   ↓
2. Send to Claude with Tool Definitions
   ↓
3. Claude Response (with or without tool calls)
   ↓
4. If Tool Calls:
   a. Parse tool arguments
   b. Execute tool function
   c. Send results back to Claude
   d. Get final response
   ↓
5. Display response to user
```

## Tool Definitions

### read_file
- **Purpose**: Read file contents
- **Parameters**: file_path (string)
- **Returns**: File content as string

### list_files
- **Purpose**: List directory contents
- **Parameters**: dir_path (string)
- **Returns**: Formatted directory listing

### run_command
- **Purpose**: Execute shell commands safely
- **Parameters**: command (string)
- **Returns**: Command output
- **Safety**: Whitelist of allowed commands

### write_file
- **Purpose**: Create or modify files
- **Parameters**: file_path (string), content (string)
- **Returns**: Success message with file size

### search_code
- **Purpose**: Search code using ripgrep
- **Parameters**: pattern (string), search_path (string), file_type (optional string)
- **Returns**: Search results with line numbers

## Security Considerations

1. **Command Execution**: Whitelist of safe commands only
2. **File Operations**: No system file access restrictions
3. **API Key**: Stored in environment variables
4. **Input Validation**: Basic parameter validation for all tools

## Dependencies

- **Go 1.24+**: Core programming language
- **OpenAI Go SDK**: For AIMLAPI communication
- **godotenv**: Environment variable management
- **ripgrep**: Fast code search (external dependency)
