import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

st.set_page_config(page_title="Student Clustering App", layout="wide")

st.title("🎓 Student Performance Clustering")
st.markdown("K-Means Clustering on Coursework Data")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file is not None:

    try:
        df = pd.read_excel(uploaded_file)

        st.subheader("📄 Raw Data Preview")
        st.dataframe(df.head())

        required_columns = ['TEST 1', 'ASS1', 'TEST 2', 'ASS2']

        # Check if required columns exist
        if not all(col in df.columns for col in required_columns):
            st.error("❌ Required columns not found in file.")
            st.stop()

        # Select only required columns
        X = df[required_columns].copy()

        # Convert to numeric (force errors to NaN)
        X = X.apply(pd.to_numeric, errors='coerce')

        # Drop rows with missing values
        X = X.dropna()

        if X.shape[0] < 3:
            st.warning("⚠️ Not enough valid numeric data for clustering.")
            st.stop()

        # Scale data
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        # Choose number of clusters
        k = st.slider("Select Number of Clusters (K)", 2, 6, 3)

        # Apply KMeans
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)

        # Add clusters to dataframe
        clustered_df = df.loc[X.index].copy()
        clustered_df['Cluster'] = clusters

        st.subheader("📊 Clustered Data")
        st.dataframe(clustered_df.head())

        # Cluster Means
        st.subheader("📈 Cluster Means")
        cluster_means = clustered_df.groupby('Cluster')[required_columns].mean()
        st.dataframe(cluster_means)

        # Silhouette Score
        score = silhouette_score(X_scaled, clusters)
        st.success(f"Silhouette Score: {round(score, 3)}")

        # Visualization
        st.subheader("📍 Cluster Visualization")

        fig, ax = plt.subplots()
        scatter = ax.scatter(
            clustered_df['TEST 1'],
            clustered_df['TEST 2'],
            c=clustered_df['Cluster']
        )
        ax.set_xlabel("TEST 1")
        ax.set_ylabel("TEST 2")
        ax.set_title("Student Clusters")
        st.pyplot(fig)

        # Download button
        csv = clustered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="⬇ Download Clustered Data",
            data=csv,
            file_name='clustered_students.csv',
            mime='text/csv'
        )

    except Exception as e:
        st.error("Something went wrong while processing the file.")
        st.write(str(e))
