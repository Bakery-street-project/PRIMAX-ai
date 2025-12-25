// ==============================================================================
// PRIMSX CODEX - MODULES.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package codex
type Spoke struct {
    Desc  string `json:"desc"`
    Value string `json:"value"`
}
var Modules = map[string]Spoke{
    "aspects": {Desc: "Aspects of the wheel", Value: "balanced"},
    "energy":  {Desc: "Energy flow", Value: "42 units"},
}
