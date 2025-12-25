// ==============================================================================
// PRIMSX CODEX - VALIDATOR.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package main

import (
    "fmt"
    "github.com/go-playground/validator/v10"
    "github.com/gofiber/fiber/v2"
)

type ChaosMatrix [6][3]int

type Request struct {
    UserID  string      `json:"userId" validate:"required,uuid"`
    Action  string      `json:"action" validate:"required,oneof=spin mutate query"`
    Payload interface{} `json:"payload" validate:"required"`
}

func main() {
    app := fiber.New()
    validate := validator.New()

    app.Post("/validate", func(c *fiber.Ctx) error {
        var req Request
        if err := c.BodyParser(&req); err != nil {
            return c.Status(400).SendString("Invalid request")
        }
        if err := validate.Struct(req); err != nil {
            return c.Status(400).SendString(fmt.Sprintf("Validation error: %v", err))
        }
        return c.SendString("Valid request")
    })

    app.Listen(":8081")
}
