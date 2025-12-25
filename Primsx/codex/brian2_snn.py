# ==============================================================================
# PRIMSX CODEX - BRIAN2_SNN.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import numpy as np
from brian2 import NeuronGroup, Synapses, SpikeMonitor, ms, mV, defaultclock, run

def run_izhikevich_snn():
    tfinal = 1000 * ms
    Ne, Ni = 800, 200
    re, ri = np.random.uniform(size=Ne), np.random.uniform(size=Ni)
    weights = np.hstack([0.5 * np.random.uniform(size=(Ne + Ni, Ne)), -np.random.uniform(size=(Ne + Ni, Ni))]).T
    defaultclock.dt = 1 * ms
    eqs = """dv/dt = (0.04*v**2 + 5*v + 140 - u + I + I_noise )/ms : 1
             du/dt = (a*(b*v - u))/ms : 1
             I : 1
             I_noise : 1
             a : 1
             b : 1
             c : 1
             d : 1"""
    N = NeuronGroup(Ne + Ni, eqs, threshold="v>=30", reset="v=c; u+=d", method="euler")
    N.v = -65
    N_exc = N[:Ne]
    N_inh = N[Ne:]
    spikemon = SpikeMonitor(N)
    N_exc.a = 0.02
    N_exc.b = 0.2
    N_exc.c = -65 + 15 * re**2
    N_exc.d = 8 - 6 * re**2
    N_inh.a = 0.02 + 0.08 * ri
    N_inh.b = 0.25 - 0.05 * ri
    N_inh.c = -65
    N_inh.d = 2
    N_exc.u = "b*v"
    N_inh.u = "b*v"
    S = Synapses(N, N, "w : 1", on_pre={"up": "I += w", "down": "I -= w"}, delay={"up": 0 * ms, "down": 1 * ms})
    S.connect()
    S.w[:] = weights.flatten()
    N_exc.run_regularly("I_noise = 5*randn()", dt=1 * ms)
    N_inh.run_regularly("I_noise = 2*randn()", dt=1 * ms)
    run(tfinal)
    return np.histogram(spikemon.t / ms, bins=10)[0]

if __name__ == "__main__":
    print("SNN Spikes:", run_izhikevich_snn())
