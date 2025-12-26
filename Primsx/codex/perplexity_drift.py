"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         PRIMAX-AI - PROPRIETARY CODE                          ║
║                                                                               ║
║  Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED         ║
║  PROPRIETARY & CONFIDENTIAL                                                   ║
║                                                                               ║
║  WATERMARK: PRIMAX-AI-BSP-2025                                            ║
║  Owner: Kiliaan Vanvoorden (@BoozeLee)                                      ║
║  File: perplexity_drift.py                                                   ║
║  Generated: 2025-12-26T10:00:42.116698                                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

# ==============================================================================
# PRIMSX CODEX - PERPLEXITY_DRIFT.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import numpy as np
import sys
sys.path.append("/home/boozelee/Desktop/bakery_neuromorphic_lab")
import sys
sys.path.append("/home/boozelee/Desktop/bakery_neuromorphic_lab")
from bakery_neuromorphic_lab.brain_perplexity_research import compute_perplexity
def monitor_drift(iterations=10):
    codex_nums = [6, 9]
    perplexities = []
    for i in range(iterations):
        p = compute_perplexity(codex_data=codex_nums)
        perplexities.append(p)
    print("Perplexities:", perplexities)
    print("Mean:", np.mean(perplexities), "Std:", np.std(perplexities))
monitor_drift()
