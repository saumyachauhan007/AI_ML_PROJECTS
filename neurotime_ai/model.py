import numpy as np
import pickle
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

np.random.seed(42)
N = 500

# Generate synthetic data
study = np.random.uniform(1, 10, N)
phone = np.random.uniform(1, 10, N)
social = np.random.uniform(1, 10, N)
breaks = np.random.uniform(1, 10, N)
sleep = np.random.uniform(1, 10, N)

X = np.column_stack([study, phone, social, breaks, sleep])

# Scale data
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Clustering model
model = KMeans(n_clusters=3, random_state=42)
model.fit(X_scaled)

# Save model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("Model ready!")