# ==============================================================================
# PRIMSX CODEX - FOLDER_ANALYZER.PY
# Copyright (c) 2024-2025 Bakery Street Project - ALL RIGHTS RESERVED
# PROPRIETARY & CONFIDENTIAL
#
# WATERMARK: PRIMSX-CODEX-BSP-2025
# LICENSE: See LICENSE_PROPRIETARY.md
# ==============================================================================

import os
     import hashlib
     import faiss
     import numpy as np
     from sentence_transformers import SentenceTransformer
     from sklearn.feature_extraction.text import TfidfVectorizer
     from googleapiclient.discovery import build
     from google.oauth2 import service_account
     from google.auth.transport.requests import Request
     from googleapiclient.http import MediaFileUpload

     # MU Memory Setup
     dimension = 384
     index = faiss.IndexFlatL2(dimension)
     mu_memory = {}
     model = SentenceTransformer('all-MiniLM-L6-v2')

     # Google Drive Backup (ADC Auth)
     creds = service_account.Credentials.from_service_account_file(
         '/home/boozelee/.config/gcloud/application_default_credentials.json',
         scopes=['https://www.googleapis.com/auth/drive']
     )
     creds.refresh(Request())
     drive_service = build('drive', 'v3', credentials=creds)

     def analyze_folder(folder_path='/home/boozelee/Desktop/superbrain-x'):
         if not os.path.exists(folder_path):
             raise FileNotFoundError(f"Folder {folder_path} missing—run: mkdir -p {folder_path}")
         file_count = 0
         for root, dirs, files in os.walk(folder_path):
             for file in files:
                 file_path = os.path.join(root, file)
                 try:
                     with open(file_path, 'r', errors='ignore') as f:
                         content = f.read()
                     file_hash = hashlib.sha256(content.encode()).hexdigest()
                     embedding = model.encode(content[:10000])
                     index.add(np.array([embedding]))
                     mu_memory[file_hash] = {
                         'path': file_path,
                         'content': content,
                         'embedding': embedding,
                         'metadata': {'subfolder': root, 'size': len(content), 'type': file.split('.')[-1], 'themes': extract_themes(content)}
                     }
                     file_count += 1
                     print(f"Analyzed: {file_path} | Hash: {file_hash[:8]} | Themes: {mu_memory[file_hash]['metadata']['themes']}")
                 except Exception as e:
                     print(f"Error analyzing {file_path}: {e}")
         print(f"Processed {file_count} files")
         # Backup to Drive
         with open('/tmp/mu_memory.json', 'w') as f:
             import json
             json.dump(mu_memory, f)
         drive_service.files().create(
             body={'name': 'superbrain_mu_memory.json'},
             media_body=MediaFileUpload('/tmp/mu_memory.json', mimetype='application/json')
         ).execute()
         faiss.write_index(index, '/home/boozelee/Desktop/superbrain-x/mu_index.faiss')

     def extract_themes(text):
         vectorizer = TfidfVectorizer(max_features=10)
         tfidf_matrix = vectorizer.fit_transform([text])
         return vectorizer.get_feature_names_out().tolist()

     if __name__ == "__main__":
         analyze_folder()