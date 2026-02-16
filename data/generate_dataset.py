import pandas as pd
import numpy as np

np.random.seed(42)

n_samples = 1000

hemoglobin = np.random.normal(14, 2.5, n_samples)
blood_sugar = np.random.normal(110, 30, n_samples)
cholesterol = np.random.normal(200, 40, n_samples)

def assign_risk(hb, bs, chol):
    risk_score = 0
    
    if hb < 12:
        risk_score += 2
    elif hb < 13.5:
        risk_score += 1
    
    if bs > 140:
        risk_score += 3
    elif bs > 110:
        risk_score += 1
    
    if chol > 240:
        risk_score += 3
    elif chol > 200:
        risk_score += 1
    
    if risk_score <= 2:
        return 'Low'
    elif risk_score <= 4:
        return 'Medium'
    else:
        return 'High'

risk_levels = [assign_risk(hb, bs, chol) for hb, bs, chol in zip(hemoglobin, blood_sugar, cholesterol)]

df = pd.DataFrame({
    'hemoglobin': np.round(hemoglobin, 1),
    'blood_sugar': np.round(blood_sugar, 1),
    'cholesterol': np.round(cholesterol, 1),
    'risk_level': risk_levels
})

df = df[(df['hemoglobin'] > 8) & (df['hemoglobin'] < 20)]
df = df[(df['blood_sugar'] > 50) & (df['blood_sugar'] < 250)]
df = df[(df['cholesterol'] > 120) & (df['cholesterol'] < 350)]

df.to_csv('/home/claude/medical-report-analyzer/data/medical_dataset.csv', index=False)
print(f"Dataset created with {len(df)} samples")
print(df['risk_level'].value_counts())
