import numpy as np
import pandas as pd

# Simulate 5 minutes of wrist shakes (1000 samples, 0.3s each)
t = np.arange(0, 300, 0.3)
ke = np.random.normal(2, 0.5, len(t))  # baseline low‑energy noise

# Add 20 random "shakes"
for _ in range(20):
    i = np.random.randint(0, len(t))
    ke[i:i+5] += np.random.uniform(3, 6, 5)   # spike

df = pd.DataFrame({"timestamp": t, "KE_value": ke})
df["label"] = (df["KE_value"] > 4).astype(int)   # 1 = harvest-worthy shake
df.to_csv("kinetic_data.csv", index=False)
print("✅ Fake data saved to kinetic_data.csv")