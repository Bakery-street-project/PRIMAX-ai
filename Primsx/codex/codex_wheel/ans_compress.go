/*
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: ans_compress.go                                                       ║
║  Generated: 2025-12-26T10:00:42.254723                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
*/

// ==============================================================================
// PRIMSX CODEX - ANS_COMPRESS.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package codex_wheel
import (
    "math"
    "sort"
)
type ANSEncoder struct {
    state uint64
    probs map[float64]uint64
}
func NewANSEncoder(data []float64) *ANSEncoder {
    counts := make(map[float64]int)
    for _, v := range data {
        counts[v]++
    }
    probs := make(map[float64]uint64)
    total := len(data)
    for v, c := range counts {
        probs[v] = uint64((float64(c) / float64(total)) * 65536) // Scaled to 16-bit
    }
    return &ANSEncoder{state: 1, probs: probs}
}
func (ans *ANSEncoder) Encode(symbols []float64) uint64 {
    for _, s := range symbols {
        p := ans.probs[s]
        if p == 0 { p = 1 } // Avoid zero probability
        ans.state = (ans.state * 65536) / p + uint64(s)
    }
    return ans.state
}
func CompressChaosTrace(trace map[string][]float64) uint64 {
    x := trace["x"]
    sort.Float64s(x) // Ensure deterministic encoding
    ans := NewANSEncoder(x)
    return ans.Encode(x)
}
