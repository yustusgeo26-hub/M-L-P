import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# -------------------------
# Step 1: Load and Clean Data
# -------------------------
df = pd.read_excel("MACHINE LEARNING CWORK-2026.xlsx")

# Select performance features (do NOT use TOTAL)
features = ['ASS1', 'ASS2', 'TEST 1', 'TEST 2']

# Convert to numeric and drop invalid rows
df[features] = df[features].apply(pd.to_numeric, errors='coerce')
df = df.dropna(subset=features)

# -------------------------
# Step 2: Scale Features
# -------------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df[features])

# -------------------------
# Step 3: Apply K-Means
# -------------------------
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
df['Cluster'] = kmeans.fit_predict(X_scaled)

# -------------------------
# Step 4: Interpret Clusters
# -------------------------
# Compute cluster averages
cluster_means = df.groupby('Cluster')[features].mean()

# Rank clusters by overall mean score
cluster_means['Overall'] = cluster_means.mean(axis=1)
ranking = cluster_means['Overall'].sort_values()

# Map cluster numbers to performance labels
labels = {
    ranking.index[0]: "At-Risk",
    ranking.index[1]: "Average",
    ranking.index[2]: "High Performer"
}

df['Performance_Level'] = df['Cluster'].map(labels)
print(df[['Cluster', 'Performance_Level']].head())

# -------------------------
# Step 5: PCA for Visualization
# -------------------------
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(8,6))
scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=df['Cluster'], cmap='Set1', s=60)
plt.title("Student Performance Clusters (PCA Visualization)")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.grid(True)

# Optional: Add legend for clusters
handles, _ = scatter.legend_elements()
plt.legend(handles, ["At-Risk", "Average", "High Performer"], title="Clusters")
plt.show()
