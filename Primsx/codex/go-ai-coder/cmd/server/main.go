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
║  Generated: 2025-12-26T10:00:42.504462                                    ║
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
    "github.com/gofiber/fiber/v2"
    "github.com/BoozeLee/CloudyMcCodeFace/internal/ai"
    "math/rand"
    "time"
    "fmt"
)

func main() {
    app := fiber.New()

    // Classic endpoint
    app.Get("/", func(c *fiber.Ctx) error {
        return c.SendString("Hello from Go-AI-Coder Superbrain!")
    })

    // Chat interface
    app.Post("/chat", func(c *fiber.Ctx) error {
        type ChatMsg struct{ Message string }
        var req ChatMsg
        if err := c.BodyParser(&req); err != nil {
            return c.Status(400).SendString("Invalid input")
        }
        reply := ai.RespondToMessage(req.Message)
        return c.JSON(fiber.Map{"reply": reply})
    })

    // Humor endpoint: next-level algorithmic humor
    app.Get("/humor", func(c *fiber.Ctx) error {
        j := ai.SuperHumor(time.Now().Nanosecond())
        return c.SendString(j)
    })

    app.Listen(":8080")
}
