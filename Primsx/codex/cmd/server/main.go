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
    "math/rand"
    "os/exec"
    "strconv"
    "strings"
    "time"
    "github.com/gofiber/fiber/v2"
    "github.com/mythicnode/superbrain-x/codex"
    "github.com/mythicnode/superbrain-x/codex_wheel"
    "github.com/mythicnode/superbrain-x/integrations/MYTHICNODE-Neuromorphic-Psychedelic-AI"
)
var app = fiber.New()
func main() {
    app.Get("/wheel/center", func(c *fiber.Ctx) error { return c.JSON(map[string]int{"center": 42}) })
    app.Get("/wheel/modules/:spoke", func(c *fiber.Ctx) error {
        spoke := c.Params("spoke")
        module, ok := codex.Modules[spoke]
        if !ok { return c.Status(404).SendString("Not found") }
        return c.JSON(module)
    })
    app.Get("/wheel/joke", func(c *fiber.Ctx) error {
        jokes := []string{"42: Ultimate answer!", "6*9=42 in base13!"}
        rand.Seed(time.Now().UnixNano())
        return c.SendString(jokes[rand.Intn(len(jokes))])
    })
    app.Get("/wheel/chaos", func(c *fiber.Ctx) error {
        nums := parseNums(c.Query("nums"))
        chaos := codex_wheel.ChaosSum(nums)
        entropy := codex_wheel.Entropy(nums)
        return c.JSON(map[string]interface{}{"chaos": chaos, "entropy": entropy})
    })
    app.Post("/wheel/mutate", func(c *fiber.Ctx) error {
        cmd := exec.Command("python3", "~/Desktop/superbrain-x/integrations/MYTHICNODE-Neuromorphic-Psychedelic-AI/psychedelic_snn.py")
        out, _ := cmd.Output()
        return c.SendString("SNN Mutated: " + string(out))
    })
    app.Get("/wheel/chaotic_neuro", func(c *fiber.Ctx) error {
        nums := parseNums(c.Query("nums"))
        trace := codex_wheel.ChaoticOscillator(nums)
        return c.JSON(trace)
    })
    app.Get("/wheel/transform", func(c *fiber.Ctx) error {
        input := c.Query("input")
        cmd := exec.Command("python3", "-c", fmt.Sprintf(`from transformers import pipeline; print(pipeline("sentiment-analysis")("%s"))`, input))
        out, _ := cmd.Output()
        return c.SendString(string(out))
    })
    app.Get("/wheel/entropy", func(c *fiber.Ctx) error {
        nums := parseNums(c.Query("nums"))
        entropy := codex_wheel.Entropy(nums)
        return c.JSON(map[string]float64{"entropy": entropy})
    })
    app.Listen(":8080")
}
func parseNums(s string) []int {
    var nums []int
    for _, p := range strings.Split(s, ",") {
        if n, err := strconv.Atoi(p); err == nil { nums = append(nums, n) }
    }
    return nums
}
