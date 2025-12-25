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
    "math/rand"
    "time"
)

// The cosmic "spokes":
type Spoke int

const (
    SpokeTrinity   Spoke = 3
    SpokeHex       Spoke = 6
    SpokeOctave    Spoke = 8
    SpokeBaker     Spoke = 13
    SpokeUniverse  Spoke = 42
)

var HitchhikerBasis = []Spoke{SpokeTrinity, SpokeHex, SpokeOctave, SpokeBaker, SpokeUniverse}

func CenterOfWheel() int { return int(SpokeUniverse) }

// Humor—42 in base 13 is 33, decode that!
var Jokes = []string{
    "Why do programmers like 42? Because it compiles in every known dimension.",
    "In base 13, 6x9 is 42. The answer is always right if you pick the base.",
    "How many Python devs does it take to screw in a lightbulb? None. 'import antigravity!'",
    "What did the Go routine say to the main thread? See you at 42nd tick!",
}

func RandomJoke() string {
    rand.Seed(time.Now().UnixNano())
    return Jokes[rand.Intn(len(Jokes))]
}
