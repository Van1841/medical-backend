import re

def parse_medical_values(text):
    values = {
        'hemoglobin': None,
        'blood_sugar': None,
        'cholesterol': None
    }
    
    text_lower = text.lower()
    
    hb_patterns = [
        r'hemoglobin[:\s]+(\d+\.?\d*)',
        r'hb[:\s]+(\d+\.?\d*)',
        r'haemoglobin[:\s]+(\d+\.?\d*)',
        r'hgb[:\s]+(\d+\.?\d*)'
    ]
    
    for pattern in hb_patterns:
        match = re.search(pattern, text_lower)
        if match:
            values['hemoglobin'] = float(match.group(1))
            break
    
    sugar_patterns = [
        r'blood\s*sugar[:\s]+(\d+\.?\d*)',
        r'glucose[:\s]+(\d+\.?\d*)',
        r'fasting\s*glucose[:\s]+(\d+\.?\d*)',
        r'fbs[:\s]+(\d+\.?\d*)',
        r'blood\s*glucose[:\s]+(\d+\.?\d*)'
    ]
    
    for pattern in sugar_patterns:
        match = re.search(pattern, text_lower)
        if match:
            values['blood_sugar'] = float(match.group(1))
            break
    
    cholesterol_patterns = [
        r'cholesterol[:\s]+(\d+\.?\d*)',
        r'total\s*cholesterol[:\s]+(\d+\.?\d*)',
        r'chol[:\s]+(\d+\.?\d*)'
    ]
    
    for pattern in cholesterol_patterns:
        match = re.search(pattern, text_lower)
        if match:
            values['cholesterol'] = float(match.group(1))
            break
    
    return values

def validate_values(values):
    errors = []
    found_count = 0
    
    # Check if at least ONE value was found
    if values['hemoglobin'] is not None:
        found_count += 1
        if values['hemoglobin'] < 5 or values['hemoglobin'] > 25:
            errors.append("Hemoglobin value out of valid range (5-25 g/dL)")
    
    if values['blood_sugar'] is not None:
        found_count += 1
        if values['blood_sugar'] < 40 or values['blood_sugar'] > 400:
            errors.append("Blood sugar value out of valid range (40-400 mg/dL)")
    
    if values['cholesterol'] is not None:
        found_count += 1
        if values['cholesterol'] < 100 or values['cholesterol'] > 400:
            errors.append("Cholesterol value out of valid range (100-400 mg/dL)")
    
    # Error only if NO values found at all
    if found_count == 0:
        errors.append("No medical values found in the report. Please ensure the report contains Hemoglobin, Blood Sugar, or Cholesterol values.")
    
    return errors
