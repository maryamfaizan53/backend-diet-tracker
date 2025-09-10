# py
def calculate_bmi(weight_kg: float, height_m: float) -> float:
    if weight_kg <= 0 or height_m <= 0:
        raise ValueError("Weight and height must be positive")
    bmi = weight_kg / (height_m ** 2)
    return round(bmi, 2)

def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if 18.5 <= bmi < 25:
        return "Normal weight"
    if 25 <= bmi < 30:
        return "Overweight"
    return "Obesity"
