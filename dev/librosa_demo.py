"""
- https://chat.openai.com/c/8b21f613-b444-4d7f-93db-ccc670f1e468
"""

import os
import librosa
import numpy as np
from sklearn.cluster import KMeans
import shutil

# Define the directory containing your WAV files
input_dir = 'path_to_wav_files'
output_dir = 'output_clusters'

# Create a dictionary to store features for each file
feature_dict = {}

# Define the function to extract audio features
def extract_features(file_path):
    y, sr = librosa.load(file_path)
    # Extract features (you can use different features depending on your needs)
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    mfcc = librosa.feature.mfcc(y=y, sr=sr)
    return np.vstack((chroma, mfcc))

# Load and extract features from all WAV files in the input directory
for root, dirs, files in os.walk(input_dir):
    for file in files:
        if file.endswith('.wav'):
            file_path = os.path.join(root, file)
            features = extract_features(file_path)
            feature_dict[file] = features

# Convert the features into a matrix
X = np.array(list(feature_dict.values()))

# Determine the number of clusters (you can adjust this)
num_clusters = 5

# Apply KMeans clustering
kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(X)
cluster_labels = kmeans.labels_

# Create output directories for each cluster
for i in range(num_clusters):
    cluster_dir = os.path.join(output_dir, f'cluster_{i}')
    os.makedirs(cluster_dir, exist_ok=True)

# Move the files into their respective clusters based on labels
for i, file_name in enumerate(feature_dict.keys()):
    cluster_label = cluster_labels[i]
    source_path = os.path.join(input_dir, file_name)
    dest_dir = os.path.join(output_dir, f'cluster_{cluster_label}')
    dest_path = os.path.join(dest_dir, file_name)
    shutil.copy(source_path, dest_path)

print("Clustering complete.")
