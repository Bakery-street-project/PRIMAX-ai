# ==============================================================================
# PRIMSX CODEX - BRAIN_PERPLEXITY_RESEARCH.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import numpy as np
from scipy.linalg import eigh
from brian2 import NeuronGroup, Synapses, SpikeMonitor, ms, mV, defaultclock, run
import nest
import time
import math

def compute_perplexity(matrix_size=10, codex_data=None):
    A = np.random.rand(matrix_size, matrix_size)
    if codex_data:
        chaos_vector = np.tile(np.array(codex_data) % 42, (matrix_size // len(codex_data) + 1))[:matrix_size]
        A += np.outer(chaos_vector, chaos_vector)
    eigenvalues, _ = eigh(A)
    print("Eigenvalues:", eigenvalues)
    shifted = np.abs(eigenvalues) + 1e-10
    perplexity = np.exp(-np.mean(np.log(shifted)))
    print("Perplexity:", perplexity)
    return perplexity

def compute_entropy(data):
    count = np.bincount(data)
    total = len(data)
    probs = count[count > 0] / total
    entropy = -np.sum(probs * np.log2(probs))
    return entropy

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
    spikes = np.histogram(spikemon.t / ms, bins=10)[0]
    entropy = compute_entropy(spikes)
    print("SNN Entropy:", entropy)
    return spikes

def run_nest_izhikevich():
    nest.ResetKernel()
    start = time.time()
    neuron = nest.Create('izhikevich', params={'a': 0.02, 'b': 0.2, 'c': -65.0, 'd': 8.0})
    mm = nest.Create('multimeter', params={'record_from': ['V_m']})
    nest.Connect(mm, neuron)
    nest.Simulate(1000.0)
    events = nest.GetStatus(mm)[0]['events']
    print("NEST Time:", time.time() - start)
    return events['V_m']

if __name__ == "__main__":
    codex_nums = [6, 9]
    compute_perplexity(codex_data=codex_nums)
    spikes = run_izhikevich_snn()
    compute_perplexity(codex_data=spikes)
    run_nest_izhikevich()
