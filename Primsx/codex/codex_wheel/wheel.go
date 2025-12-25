// ==============================================================================
// PRIMSX CODEX - WHEEL.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package codex_wheel
import (
    "math"
)
const Center = 42
func ChaosSum(nums []int) int {
    sum := 0
    for _, n := range nums { sum += n }
    return sum % Center
}
func Base13Chaos(nums []int) int {
    sum := 0
    for _, n := range nums { sum += n * 13 }
    return sum % Center
}
func ChaoticOscillator(nums []int) map[string][]float64 {
    sigma, rho, beta := 10.0, 28.0, 8.0/3.0
    x, y, z := float64(ChaosSum(nums)), 10.0, 28.0
    dt, steps := 0.01, 100
    xs, ys, zs := []float64{x}, []float64{y}, []float64{z}
    for i := 0; i < steps; i++ {
        dx := sigma * (y - x)
        dy := x * (rho - z) - y
        dz := x*y - beta*z
        x += dt * dx
        y += dt * dy
        z += dt * dz
        xs = append(xs, x)
        ys = append(ys, y)
        zs = append(zs, z)
    }
    return map[string][]float64{"x": xs, "y": ys, "z": zs}
}
func Entropy(nums []int) float64 {
    count := make(map[int]int)
    total := len(nums)
    for _, n := range nums {
        count[n]++
    }
    entropy := 0.0
    for _, c := range count {
        p := float64(c) / float64(total)
        entropy -= p * math.Log2(p)
    }
    return entropy
}
