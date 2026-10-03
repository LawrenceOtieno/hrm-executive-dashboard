# SimbaNet Solutions Workforce Analytics Dashboard

A real-time Human Resource Management (HRM) operational insight and workforce analytics application built specifically for managing regional telecommunications hubs across Kenya. 

👉 **[Live Project Demo](https://streamlit.app)**

---

## Dashboard at a Glance
For the better part of a decade, SimbaNet Solutions has been quietly rewiring how Kenya gets online—trenching fibre down streets in Nairobi, Mombasa, Kisumu, and Nakuru, lighting up homes and businesses that never had a reliable connection before. Because this slow, technical work relies heavily on institutional memory, managing talent attrition is vital. 

The **SimbaNet Workforce Analytics Dashboard** provides high-level stakeholders with a bird's-eye view of organizational health, departing from generic assumptions to uncover the operational truths behind staff turnover.

* **Interactive Operational Slicing:** Dynamically filter global metrics, tenure trends, and salary tracking by specific hubs, departments, and exit dynamics.
* **Geospatial Concentration Mapping:** An interactive GIS mapping interface pinpointing operational focus centers and tracking where attrition pressures are physically concentrated.
* **Operational Control Suite:** Built-in sidebar tools allowing administrators to clear system session cache (`C`), print active analytical dashboards, or capture screen recordings of real-time query states.

---

## Core Operational Metrics
The dashboard aggregates core high-level metrics globally or filters down seamlessly across individual regional hubs:

* **Active Headcount:** 443 Staff members distributed across 4 strategic Kenyan hubs.
* **Turnover Rate:** 11.4% *(Totaling 57 departures over the current tracking period)*.
* **Involuntary Exits:** 58% of all departures. *(Crucially, more than half of the workforce departures were driven by organizational decisions rather than individual resignations—reframing the problem from a retention story to a recruitment and management alignment story).*
* **Gender Pay Gap:** 2.2% on average, trending slightly in favor of female personnel.

---

## Deep-Dive Visual Analytics & Key Findings

### Chapter 1: Geographic Attrition Realities
Geographically, **Mombasa** experiences the company's highest regional turnover rate at **13.2%**, sharply contrasting with **Nakuru**, which sits at a lean **9.2%**. 

Before jumping to compensation conclusions, checking the financial charts reveals a tight regional parity. The wage variance between cities is significantly smaller than the variance in departures. 
* **Strategic Takeaway:** Because compensation structures remain uniformly competitive across regions, the data suggests that Mombasa's attrition is caused by localized office management practices or heavy workload distributions, rather than wage gaps.

| Regional Hub Location | Turnover Rate (%) |
| :--- | :---: |
| **Mombasa** | **13.2% (Highest)** |
| **Nairobi** | 12.5% |
| **Kisumu** | 10.9% |
| **Nakuru** | 9.2% |

---

### Chapter 2: Departmental Insights
The story so far: SimbaNet loses about 11 in every 100 people it employs each year—and most of them didn't quit. They were let go. Sales is where it shows up worst.

Company-wide turnover numbers hide a more useful split: why people are leaving each department. A department losing people to resignations needs a different response than one losing them to terminations.

#### The Sales Attrition Vector
The first assumption in attrition is often compensation, but the data refutes this. The **Sales** department experiences the highest turnover rate in the company at **12.7%**, which is more than double the **Finance** department's baseline of **10.8%**. 
* **Strategic Takeaway:** Instead of concluding that pay or generic workplace culture is broken everywhere, resources should target how staff are evaluated, managed, and performance-tracked in Sales over the past year.

| Department | Turnover Rate (%) |
| :--- | :---: |
| **Sales** | **12.7% (Highest)** |
| **Engineering** | 11.5% |
| **Human Resources** | 11.4% |
| **Operations** | 11.2% |
| **Marketing** | 11.0% |
| **Finance** | 10.8% |

---

### Chapter 3: Composition of the Active Workforce
A deep dive into the demographic structures supporting individual departments shows where staffing strengths and succession baselines reside.

#### Gender Mix by Department
The workforce distribution exhibits distinct departmental splits between male and female team counts:
* **Engineering:** Female: 43 | Male: 26
* **Finance:** Female: 40 | Male: 43
* **Human Resources:** Female: 30 | Male: 40
* **Marketing:** Female: 34 | Male: 39
* **Operations:** Female: 39 | Male: 40
* **Sales:** Female: 32 | Male: 37

#### Age Profile by Department
Generational brackets across departments point out the distribution of emerging talent (`Under 30`) and senior experience pools (`50+`):
* **Engineering:** Under 30: 17 | 30-39: 10 | 40-49: 19 | 50+: 23
* **Finance:** Under 30: 11 | 30-39: 27 | 40-49: 18 | 50+: 27
* **Human Resources:** Under 30: 24 | 30-39: 18 | 40-49: 13 | 50+: 15
* **Marketing:** Under 30: 13 | 30-39: 18 | 40-49: 20 | 50+: 22
* **Operations:** Under 30: 12 | 30-39: 19 | 40-49: 29 | 50+: 19
* **Sales:** Under 30: 18 | 30-39: 13 | 40-49: 18 | 50+: 20

---

### Remuneration Benchmarks & Financial Baselines
A side-by-side financial metric layer assessing structural wage distribution across the primary hubs:

* **Kisumu:** KES 1,337,572 Average Annual Salary
* **Mombasa:** KES 1,345,296 Average Annual Salary
* **Nairobi:** KES 1,348,952 Average Annual Salary
* **Nakuru:** KES 1,389,408 Average Annual Salary *(Top baseline wage zone)*

---

### Headcount Distribution Profiles
Workforce personnel are distributed almost perfectly evenly across the main focus areas, emphasizing the need to solve hyper-local operational differences:
* **Nakuru:** 26.0%
* **Kisumu:** 25.8%
* **Mombasa:** 25.8%
* **Nairobi:** 22.4%

---

## Technical Stack & Framework
* **Core UI Framework:** Streamlit (Python-driven frontend & high-speed reactive layout engine)
* **Geospatial Mapping Engine:** OpenStreetMap / CARTO integration layers
* **Analytical Processing:** Pandas / NumPy vectorized pipelines for real-time statistical evaluation

---

## Local Setup & Installation

Create and activate an isolated Python virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
```

Install the project package requirements:

```bash
pip install -r requirements.txt
```

Launch the Streamlit executive analytical workspace locally:

```bash
streamlit run app.py
```
