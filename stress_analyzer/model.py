import numpy as np
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import MinMaxScaler

np.random.seed(42)
N = 600

sleep = np.random.uniform(1, 10, N)
screen = np.random.uniform(1, 10, N)
work = np.random.uniform(1, 10, N)
social = np.random.uniform(1, 10, N)
exercise = np.random.uniform(1, 10, N)

# stress logic
stress_score = (
    work * 1.5 +
    screen * 1.2 -
    sleep * 1.3 -
    exercise * 1.0 -
    social * 0.8 +
    np.random.normal(0, 1, N)
)

stress = np.where(stress_score > 5, 2,
         np.where(stress_score > 2, 1, 0))

X = np.column_stack([sleep, screen, work, social, exercise])
y = stress

scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

model = LogisticRegression()
model.fit(X_scaled, y)

pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(scaler, open("scaler.pkl", "wb"))

print("Model ready!")