import pandas as pd
import numpy as np
from faker import Faker
import random

# Force explicit Kenyan localization
fake = Faker(['en_KE'])
np.random.seed(42)
random.seed(42)

num_employees = 500

departments = ['Engineering', 'Sales', 'Marketing', 'Human Resources', 'Finance', 'Operations']
job_titles = {
    'Engineering': ['Software Engineer', 'Senior Engineer', 'Engineering Manager', 'QA Analyst'],
    'Sales': ['Account Executive', 'Sales Manager', 'Business Development Rep'],
    'Marketing': ['Marketing Specialist', 'Growth Manager', 'SEO Analyst'],
    'Human Resources': ['HR Specialist', 'HR Manager'],
    'Finance': ['Financial Analyst', 'Finance Manager'],
    'Operations': ['Operations Associate', 'Operations Manager']
}
locations = ['Nairobi', 'Mombasa', 'Kisumu', 'Nakuru']

data = []

for i in range(num_employees):
    emp_id = f"EMP{1000 + i}"
    
    # Generate explicit Kenyan first names and last names
    first_name = fake.first_name()
    last_name = fake.last_name()
    name = f"{first_name} {last_name}"
    
    gender = random.choice(['Male', 'Female', 'Non-binary'])
    age = random.randint(22, 60)
    
    max_tenure = max(1, age - 21)
    tenure_years = round(random.uniform(0.5, min(max_tenure, 15)), 1)
    
    dept = random.choice(departments)
    role = random.choice(job_titles[dept])
    location = random.choice(locations)
    
    base_salary_map = {
        'Engineering': 120000, 'Sales': 85000, 'Marketing': 80000,
        'Finance': 95000, 'Human Resources': 75000, 'Operations': 70000
    }
    salary = int(base_salary_map[dept] * random.uniform(0.8, 1.4) + (tenure_years * 2500))
    
    performance_rating = random.choice(['Needs Improvement', 'Meets Expectations', 'Exceeds Expectations', 'Outstanding'])
    
    flight_risk_score = 0
    if salary < base_salary_map[dept]: flight_risk_score += 35
    if performance_rating == 'Needs Improvement': flight_risk_score += 25
    if tenure_years > 4 and random.random() > 0.7: flight_risk_score += 20
    
    attrition = 'Yes' if random.randint(0, 100) < flight_risk_score else 'No'
    
    term_type = 'N/A'
    if attrition == 'Yes':
        term_type = 'Voluntary' if performance_rating != 'Needs Improvement' else 'Involuntary'

    data.append({
        'EmployeeID': emp_id,
        'FullName': name,
        'Gender': gender,
        'Age': age,
        'Department': dept,
        'JobTitle': role,
        'Location': location,
        'TenureYears': tenure_years,
        'Salary': salary,
        'PerformanceRating': performance_rating,
        'Attrition': attrition,
        'TerminationType': term_type,
        'TrainingHours': random.randint(4, 40)
    })

df = pd.DataFrame(data)
df.to_csv('hrm_mock_data.csv', index=False)

print(f"Successfully generated {num_employees} rows of localized Kenyan HR data!")
print("\n--- SAMPLE GENERATED NAMES ---")
print(df['FullName'].head(10).to_string(index=False))
print("------------------------------")