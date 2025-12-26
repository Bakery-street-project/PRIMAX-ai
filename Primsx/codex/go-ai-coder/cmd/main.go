/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: main.go                                                               ║
║  Generated: 2025-12-26T10:00:42.487842                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - MAIN.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package main

import (
    "fmt"
    "github.com/BoozeLee/CloudyMcCodeFace/internal/ai"
)

func main() {
    if err := ai.NewCloudAIClient(); err != nil {
        fmt.Println("AI client error:", err)
        return
    }
    fmt.Println("AI client started.")
}
