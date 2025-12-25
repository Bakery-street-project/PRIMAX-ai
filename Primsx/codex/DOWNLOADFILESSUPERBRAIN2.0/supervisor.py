# ==============================================================================
# PRIMSX CODEX - SUPERVISOR.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import os
     import faiss
     import numpy as np
     from sentence_transformers import SentenceTransformer
     import time
     from datetime import datetime

     model = SentenceTransformer('all-MiniLM-L6-v2')
     index = faiss.read_index('/home/boozelee/Desktop/superbrain-x/mu_index.faiss')
     mu_memory = {}  # Load from JSON if needed

     def supervise_analysis(folder_path='/home/boozelee/Desktop/superbrain-x'):
         start_time = time.time()
         total_files = sum(len(files) for _, _, files in os.walk(folder_path))
         processed_files = 0
         coverage = []
         for root, _, files in os.walk(folder_path):
             for file in files:
                 file_path = os.path.join(root, file)
                 try:
                     with open(file_path, 'r', errors='ignore') as f:
                         content = f.read()
                     embedding = model.encode(content[:10000])
                     D, I = index.search(np.array([embedding]), 1)
                     if D[0][0] < 0.1:  # Cosine similarity check
                         coverage.append(file_path)
                         processed_files += 1
                     else:
                         print(f"Warning: {file_path} not fully processed (similarity {D[0][0]})")
                 except Exception as e:
                     print(f"Error supervising {file_path}: {e}")
         completion_rate = (processed_files / total_files) * 100
         print(f"Supervision Report: {processed_files}/{total_files} files processed ({completion_rate:.2f}%)")
         print(f"Time taken: {time.time() - start_time:.2f}s")
         if completion_rate < 95:
             print("⚠️ Lazy AI detected: Incomplete coverage")
         # Bayesian laziness check
         p_lazy = 1 - (completion_rate / 100)
         print(f"P(Lazy|Output) ≈ {p_lazy:.2f}")
         with open('/home/boozelee/Desktop/superbrain-x/supervisor_log.txt', 'a') as f:
             f.write(f"{datetime.now()}: {completion_rate}% coverage, P(Lazy)={p_lazy}\n")

     if __name__ == "__main__":
         supervise_analysis()