def calculate_risk_score(values, risk_level, model_probabilities=None):
    """
    OPTIMIZATION TECHNIQUE 2: Custom Risk Score Formula
    
    Novel mathematical approach combining:
    1. ML Model Confidence (40% weight)
    2. Clinical Severity Index (30% weight)
    3. Abnormality Count (30% weight)
    
    Formula: Risk_Score = 0.4×ML_Conf + 0.3×Severity + 0.3×Abnormality
    
    Args:
        values: Dict with hemoglobin, blood_sugar, cholesterol
        risk_level: String ('Low', 'Medium', 'High')
        model_probabilities: Optional array of ML model probabilities
    
    Returns:
        int: Risk score from 0-100
    """
    
    # COMPONENT 1: ML Model Confidence (0-100)
    # Based on Random Forest prediction
    risk_base_scores = {
        'Low': 15,
        'Medium': 50,
        'High': 85
    }
    ml_confidence = risk_base_scores.get(risk_level, 50)
    
    # COMPONENT 2: Clinical Severity Index (0-100)
    # Weighted by feature importance from Random Forest
    # Feature weights: Blood Sugar (40.9%), Cholesterol (34.5%), Hemoglobin (24.6%)
    
    severity_scores = []
    feature_weights = []
    
    # Hemoglobin severity calculation
    if values.get('hemoglobin') is not None:
        hb = values['hemoglobin']
        # Normalize deviation from normal range (12-17 g/dL)
        if hb < 12:
            hb_severity = min((12 - hb) / 7 * 100, 100)  # Severe if < 5
        elif hb > 17:
            hb_severity = min((hb - 17) / 8 * 100, 100)  # Severe if > 25
        else:
            hb_severity = 0
        
        severity_scores.append(hb_severity)
        feature_weights.append(0.246)  # 24.6% importance
    
    # Blood sugar severity calculation
    if values.get('blood_sugar') is not None:
        bs = values['blood_sugar']
        # Normalize deviation from normal range (70-110 mg/dL)
        if bs < 70:
            bs_severity = min((70 - bs) / 30 * 100, 100)
        elif bs > 110:
            bs_severity = min((bs - 110) / 290 * 100, 100)  # Max at 400
        else:
            bs_severity = 0
        
        severity_scores.append(bs_severity)
        feature_weights.append(0.409)  # 40.9% importance (highest)
    
    # Cholesterol severity calculation
    if values.get('cholesterol') is not None:
        chol = values['cholesterol']
        # Normalize deviation from normal range (< 200 mg/dL)
        if chol > 200:
            chol_severity = min((chol - 200) / 200 * 100, 100)  # Max at 400
        else:
            chol_severity = 0
        
        severity_scores.append(chol_severity)
        feature_weights.append(0.345)  # 34.5% importance
    
    # Calculate weighted severity index
    if severity_scores:
        # Weighted average: Σ(wi × si) / Σ(wi)
        severity_index = sum(w * s for w, s in zip(feature_weights, severity_scores)) / sum(feature_weights)
    else:
        severity_index = 0
    
    # COMPONENT 3: Abnormality Count Score (0-100)
    abnormal_count = 0
    
    # Count abnormal values based on clinical thresholds
    if values.get('hemoglobin') is not None:
        hb = values['hemoglobin']
        if hb < 12 or hb > 17:
            abnormal_count += 1
    
    if values.get('blood_sugar') is not None:
        bs = values['blood_sugar']
        if bs < 70 or bs > 110:
            abnormal_count += 1
    
    if values.get('cholesterol') is not None:
        chol = values['cholesterol']
        if chol > 200:
            abnormal_count += 1
    
    # Normalize to 0-100 (3 abnormal = 100)
    abnormality_score = (abnormal_count / 3) * 100
    
    # FINAL FORMULA: Weighted combination
    # Risk_Score = 0.4 × ML_Confidence + 0.3 × Severity_Index + 0.3 × Abnormality_Count
    final_score = (
        0.4 * ml_confidence +
        0.3 * severity_index +
        0.3 * abnormality_score
    )
    
    # Ensure score is within 0-100
    final_score = max(0, min(100, int(round(final_score))))
    
    return final_score

def get_risk_score_message(score):
    """Get appropriate message based on risk score"""
    if score >= 80:
        return "🚨 CRITICAL - Immediate medical attention required"
    elif score >= 60:
        return "⚠️ HIGH RISK - Consult doctor urgently"
    elif score >= 40:
        return "⚡ MEDIUM RISK - Schedule checkup soon"
    elif score >= 20:
        return "⚠️ BORDERLINE - Monitor closely"
    else:
        return "✅ LOW RISK - Maintain healthy habits"

def get_risk_color(score):
    """Get color code based on risk score"""
    if score >= 80:
        return "#dc2626"  # Red
    elif score >= 60:
        return "#ea580c"  # Orange-red
    elif score >= 40:
        return "#f59e0b"  # Orange
    elif score >= 20:
        return "#eab308"  # Yellow
    else:
        return "#16a34a"  # Green
