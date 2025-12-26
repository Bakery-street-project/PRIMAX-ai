/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: mathutils.go                                                          ║
║  Generated: 2025-12-26T10:06:02.839990                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - MATHUTILS.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package math

import "gonum.org/v1/gonum/mat"
func ComputeEntropy(prob []float64) float64 {
    h := 0.0
    for _, p := range prob { if p > 0 { h -= p * math.Log2(p) } }
    return h
}
