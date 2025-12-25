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
    "strconv"
    "github.com/gofiber/fiber/v2"
    "codex_wheel"
)

func main() {
    app := fiber.New()

    app.Get("/wheel/center", func(c *fiber.Ctx) error {
        return c.SendString(fmt.Sprintf("Wheel Center is %d — the answer to life, universe, everything.", codex_wheel.CenterOfWheel()))
    })

    app.Get("/wheel/modules/:spoke", func(c *fiber.Ctx) error {
        n, _ := strconv.Atoi(c.Params("spoke"))
        return c.JSON(codex_wheel.ModulesForSpoke(codex_wheel.Spoke(n)))
    })

    app.Get("/wheel/joke", func(c *fiber.Ctx) error {
        return c.SendString("🚀 " + codex_wheel.RandomJoke())
    })

    app.Post("/wheel/chaos", func(c *fiber.Ctx) error {
        var matrix [6][3]int
        if err := c.BodyParser(&matrix); err != nil { return c.Status(400).SendString("Invalid") }
        out := codex_wheel.SumTripletsMod42(matrix)
        if out == 0 {
            return c.SendString("✨ Cosmic harmony: the sum modulo 42 is zero. VICTORY.")
        }
        return c.SendString(fmt.Sprintf("The Wheel is spinning, chaos residue is %d", out))
    })

    app.Post("/wheel/mutate", func(c *fiber.Ctx) error {
        var newModule string
        if err := c.BodyParser(&newModule); err != nil { 
            return c.Status(400).SendString("Send a JSON string for module name!") 
        }
        return c.SendString(fmt.Sprintf("Module '%s' would be appended! (Persistence requires file/db in real systems)", newModule))
    })

    app.Listen(":8080")
}
