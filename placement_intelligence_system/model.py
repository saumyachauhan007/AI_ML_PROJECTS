import numpy as np
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

np.random.seed(42)
N = 500

# generate data
cgpa = np.random.uniform(5, 10, N)
coding = np.random.uniform(1, 10, N)
dsa = np.random.uniform(1, 10, N)
comm = np.random.uniform(1, 10, N)
readiness = np.random.uniform(1, 10, N)

salary = (
    cgpa * 1.4 +
    coding * 1.1 +
    dsa * 1.0 +
    comm * 0.7 +
    readiness * 0.8 +
    np.random.normal(0, 1, N)
)

X = np.column_stack([cgpa, coding, dsa, comm, readiness])
y = salary

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

model = LinearRegression()
model.fit(X_scaled, y)

# save model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("Model trained and saved!")