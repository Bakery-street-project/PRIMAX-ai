// ==============================================================================
// PRIMSX CODEX - ASPECTS.GO
// Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
// PROPRIETARY & CONFIDENTIAL
//
// WATERMARK: PRIMSX-CODEX-BSP-2025
// LICENSE: See LICENSE_PROPRIETARY.md
// ==============================================================================

package codex
type Aspect string
const Humor Aspect = "Humor"
func Run(as Aspect) string {
    if as == Humor { return "Knock knock. Who's there? A recursive bug. A recursive bug who?" }
    return "?"
}
