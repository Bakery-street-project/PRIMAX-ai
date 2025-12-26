/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: fiber.go                                                              ║
║  Generated: 2025-12-26T10:06:02.847411                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - FIBER.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package api

import (
    "github.com/gofiber/fiber/v2"
)

func NewAPI() *fiber.App {
    app := fiber.New()
    app.Get("/status", func(c *fiber.Ctx) error {
        return c.JSON(fiber.Map{"status": "Neural net is live!"})
    })
    return app
}
