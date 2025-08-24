# hotwork_paycheck_calculator.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Define per diem meal rates (Meals + Incendiary)
PER_DIEM_OPTIONS = {
    "None": 0,
    "Breakfast Only": 11 + 4,       # 15
    "Breakfast + Lunch": 12 + 8,    # 20
    "Breakfast + Lunch + Dinner": 41 + 13, # 54
    "Lunch + Dinner": 30 + 9,       # 39
    "Dinner Only": 18 + 5           # 23
}

def calc_weekly_pay(hours, per_diem_choices, days, base_weekly, site_bonus_day, tax_rate=0.15):
    base_pay = base_weekly
    site_bonus = site_bonus_day * days
    
    # Overtime calculation (fluctuating hours method)
    ot_pay = 0
    if hours > 40:
        regular_rate = (base_pay + site_bonus) / hours
        ot_hours = hours - 40
        ot_pay = ot_hours * (0.5 * regular_rate)
    
    taxable_gross = base_pay + site_bonus + ot_pay
    per_diem = sum(PER_DIEM_OPTIONS[choice] for choice in per_diem_choices)
    
    taxes = taxable_gross * tax_rate
    after_tax = taxable_gross - taxes + per_diem
    
    return taxable_gross, per_diem, after_tax

# --- UI START ---
st.title("Hotwork Technician Paycheck Calculator")

# Sidebar settings
st.sidebar.header("Settings")
base_weekly = st.sidebar.number_input("Base Weekly Salary ($)", value=700)
site_bonus_day = st.sidebar.number_input("Site Bonus per Day ($)", value=45)
tax_rate = st.sidebar.slider("Tax Rate (%)", 10, 25, 15) / 100

# Week 1 inputs
st.header("Week 1")
w1_hours = st.number_input("Hours worked (Week 1)", min_value=0, max_value=100, value=84)
w1_days = st.number_input("Days worked (Week 1)", min_value=0, max_value=7, value=7)
w1_per_diem_choices = []
for i in range(w1_days):
    choice = st.selectbox(f"Per diem (Day {i+1}) - Week 1", list(PER_DIEM_OPTIONS.keys()), index=0, key=f"w1_{i}")
    w1_per_diem_choices.append(choice)

# Week 2 inputs
st.header("Week 2")
w2_hours = st.number_input("Hours worked (Week 2)", min_value=0, max_value=100, value=0)
w2_days = st.number_input("Days worked (Week 2)", min_value=0, max_value=7, value=0)
w2_per_diem_choices = []
for i in range(w2_days):
    choice = st.selectbox(f"Per diem (Day {i+1}) - Week 2", list(PER_DIEM_OPTIONS.keys()), index=2, key=f"w2_{i}")
    w2_per_diem_choices.append(choice)

# Calculate for both weeks
w1_taxable, w1_perdiem, w1_after = calc_weekly_pay(w1_hours, w1_per_diem_choices, w1_days, base_weekly, site_bonus_day, tax_rate)
w2_taxable, w2_perdiem, w2_after = calc_weekly_pay(w2_hours, w2_per_diem_choices, w2_days, base_weekly, site_bonus_day, tax_rate)

taxable_total = w1_taxable + w2_taxable
perdiem_total = w1_perdiem + w2_perdiem
after_tax_total = w1_after + w2_after

# Output summary
st.subheader("Pay Period Summary")
st.write(f"**Taxable Gross Wages:** ${taxable_total:,.2f}")
st.write(f"**Per Diem (tax-free):** ${perdiem_total:,.2f}")
st.write(f"**Estimated Take-Home:** ${after_tax_total:,.2f}")

# --- Monthly Projection ---
st.subheader("Monthly Projection")

# Define month scenarios (4 weeks explicitly)
scenarios = {
    "Light Month (5 Days)": [
        {"hours": 60, "days": 5, "per_diem": "Breakfast + Lunch + Dinner"},
        {"hours": 0, "days": 0, "per_diem": "None"},
        {"hours": 0, "days": 0, "per_diem": "None"},
        {"hours": 0, "days": 0, "per_diem": "None"},
    ],
    "Medium Month (14 Days)": [
        {"hours": 84, "days": 7, "per_diem": "Breakfast + Lunch + Dinner"},
        {"hours": 0, "days": 0, "per_diem": "None"},
        {"hours": 84, "days": 7, "per_diem": "Breakfast + Lunch + Dinner"},
        {"hours": 0, "days": 0, "per_diem": "None"},
    ],
    "Heavy Month (28 Days)": [
        {"hours": 84, "days": 7, "per_diem": "Breakfast + Lunch + Dinner"},
        {"hours": 84, "days": 7, "per_diem": "Breakfast + Lunch + Dinner"},
        {"hours": 84, "days": 7, "per_diem": "Breakfast + Lunch + Dinner"},
        {"hours": 84, "days": 7, "per_diem": "Breakfast + Lunch + Dinner"},
    ]
}

monthly_results = {}

for label, weeks in scenarios.items():
    total_after_tax = 0
    for w in weeks:
        per_diem_list = [w["per_diem"]] * w["days"]  # full per diem every day
        _, _, after_tax = calc_weekly_pay(
            w["hours"], per_diem_list, w["days"], base_weekly, site_bonus_day, tax_rate
        )
        total_after_tax += after_tax
    monthly_results[label] = total_after_tax

# Convert to DataFrame for chart
df = pd.DataFrame.from_dict(monthly_results, orient="index", columns=["After Tax Take-Home"])
st.bar_chart(df)

