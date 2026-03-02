import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

st.title("🎓 Student Performance Clustering")
st.write("K-Means Clustering (K=3)")

# Upload file
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.write("### Raw Data")
    st.dataframe(df.head())

    # Select features
    X = df[['TEST 1', 'ASS1', 'TEST 2', 'ASS2']].dropna()

    # Scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # KMeans
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    df = df.loc[X.index]
    df['Cluster'] = clusters

    st.write("### Clustered Data")
    st.dataframe(df.head())

    # Show cluster means
    st.write("### Cluster Means")
    st.write(df.groupby('Cluster')[['TEST 1','ASS1','TEST 2','ASS2']].mean())

    # Plot
    fig, ax = plt.subplots()
    ax.scatter(df['TEST 1'], df['TEST 2'], c=df['Cluster'])
    ax.set_xlabel("TEST 1")
    ax.set_ylabel("TEST 2")
    ax.set_title("Student Clusters")
    st.pyplot(fig)