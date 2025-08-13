import matplotlib.pyplot as plt
import streamlit as st
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.preprocessing import LabelEncoder
import pandas as pd

# ----- Defining Extraction Functions -----
def extract_disruption_risk(text):
    text = text.lower()
    if any(term in text for term in ["major regulatory", "public scrutiny", "geopolitical", "high reputational risk"]):
        return "High"
    elif any(term in text for term in ["moderate disruption","spill", "regulatory volatility", "esg", "indigenous", "aging infrastructure", "climate policy"]):
        return "Medium"
    elif any(term in text for term in ["stable demand", "long-term contracts", "deeply embedded", "secured revenue"]):
        return "Low"
    else:
        return "Medium"


def extract_innovation_capability(text):
    text = text.lower()
    if any(term in text for term in ["strong innovation", "electrification", "bifacial", "rfp", "digital inspection", "modernizing", "pumped-hydro", "solar+storage", "robust project"]):
        return "Strong"
    elif any(term in text for term in ["reactive", "compliance", "legacy", "not yet mature", "minimal capability"]):
        return "Weak"
    else:
        return "Average"

def detect_business_unit(text):
    text = text.lower()
    
    if "carbon capture" in text or "ccs" in text or "co2" in text:
        return "Carbon Capture"
    elif "natural gas" in text:
        return "Natural Gas Pipelines"
    elif "liquids" in text or "keystone" in text or "oil transport" in text:
        return "Liquids Pipelines"
    elif "pumped-hydro" in text or "grid" in text or "utility-scale solar+storage" in text or "energy dispatch" in text:
        return "Power & Storage"
    elif "renewable" in text or "solar" in text or "wind" in text or "agrivoltaics" in text:
        return "Renewable Energy"
    else:
        return "Unknown"

# ----- Defining the business units with descriptions and years active -----
business_units = [
    {
        "name": "Natural Gas Pipelines",
        "years_active": 30,
        "description": "TC Energy began natural gas pipeline operations in 1951 and remains a core provider, delivering ~30% of North America’s clean-burning natural gas. The segment is central to TC Energy’s identity and revenue base. Although demand is forecasted to grow through 2035 (+40 Bcf/d), aging infrastructure, regulatory oversight, Indigenous consultations, and ESG scrutiny introduce medium-term risks. TC Energy is actively modernizing its network through initiatives like hybrid electric compression, digital inspection tools, and the $900M Northwoods Expansion. These investments show a strong but not yet industry-leading innovation posture."
    },
    {
        "name": "Liquids Pipelines",
        "years_active": 14,
        "description": "TC Energy’s Liquids Pipelines division has been operational since the mid-2000s, with its oldest pipelines (e.g., Keystone) starting service in 2010. While less mature than the gas segment, it remains a key unit with long-term contracts securing 88% of EBITDA. The division navigates regulatory volatility and occasional environmental incidents, such as spills, which contribute to moderate disruption risk. Capacity limits and shifting market dynamics also impact operations. Public sentiment varies across regions. The team has implemented industry-standard practices such as API 1173, remote sensing, and advanced inspection tools. While these efforts ensure operational integrity, broader innovation remains at an average level, with a focus on incremental improvements rather than transformational shifts."
    },
    {
        "name": "Renewable Energy",
        "years_active": 5,
        "description": "The company has a stake in Bruce Power, which is longstanding (nuclear), but wind/solar/storage investments only ramped up after 2020. Much of the current renewable strategy is still under development or early execution (e.g., RFIs, pilot projects). Faces moderate disruption risk: regulatory volatility, market fluctuations, and project complexity. However, this is supported by strong long-term trends in demand and contracts. Bruce Power offers some stability, though there are nuclear maintenance issues. Strong innovation pipeline: utility-scale storage, electrification of operations, bifacial solar panels, strategic integration of renewables such as wind, and robust project development across Canada and the U.S."
    },
    {
    "name": "Power & Storage",
    "years_active": 40,
    "description": "TC Energy’s Power division spans decades, including its 48.4% stake in Bruce Power (nuclear since 1967) and ~4,650 MW across seven generation plants (nuclear, gas-fired, etc.). The division plays a central role in regional energy systems but faces regulatory volatility, fuel price fluctuations, and nuclear maintenance outages (e.g., Bruce Unit 5). Integrating intermittent renewables adds operational complexity and introduces moderate disruption risk. High innovation maturity is evident through pumped-hydro storage projects (1,000 MW in Ontario, 75 MW at Canyon Creek), utility-scale solar+storage (Saddlebrook ~100 MW), electrification of gas fleets, and RFPs for renewables for pipeline loads—demonstrating strong cross-technological capabilities."
   },
    {
        "name": "Carbon Capture",
        "years_active": 2,
        "description": "The Alberta Carbon Grid (ACG) is in advanced development and aims to capture up to 20 Mt CO₂/year in Alberta. Operational efforts are just beginning, including initial ACG hubs and feasibility studies such as TVA. Strong technical ambition (large-scale CCS infrastructure and feasibility work), but the unit is still building execution capacity. The unit faces regulatory volatility, evolving climate policy, and economic uncertainty—resulting in medium disruption risk. While projects are capital-intensive and subject to public and environmental review, they align with long-term energy transition goals. The team has outlined a clear roadmap for delivery, supported by partnerships and technical planning. Innovation efforts are underway, with foundational technologies being explored and frameworks taking shape."
    }
]

# ----- Creating the scoring fuctions -----
def score_maturity(years_active):
    if years_active >= 20:
        return 5
    elif years_active >= 10:
        return 4
    elif years_active >= 5:
        return 3
    elif years_active >= 2:
        return 2
    else:
        return 1
    
def score_disruption(disruption_risk):
    risk_map = {
        "Low": 5,
        "Medium": 3,
        "High": 1
    }
    return risk_map.get(disruption_risk, 3)  # default to 3

def score_innovation(innovation_capability):
    readiness_map = {
        "Strong": 5,
        "Average": 3,
        "Weak": 1
    }
    return readiness_map.get(innovation_capability, 3)

def classify_unit(total_score):
    if total_score >= 13:
        return "Core", (70, 20, 10)
    elif total_score >= 10:
        return "Emerging", (40, 40, 20)
    elif total_score >= 7:
        return "At Risk", (20, 30, 50)
    else:
        return "Laggard", (10, 20, 70)
    
def evaluate_unit(description, years_active):
    name = detect_business_unit(description)
    maturity = score_maturity(years_active)

    # Fix: extract disruption and innovation levels before scoring
    disruption_label = extract_disruption_risk(description)
    disruption = score_disruption(disruption_label)

    innovation_label = extract_innovation_capability(description)
    readiness = score_innovation(innovation_label)

    total = maturity + disruption + readiness
    classification, mix = classify_unit(total)

    return {
        "name": name,
        "classification": classification,
        "mix": {
            "Core": mix[0],
            "Adjacent": mix[1],
            "Transformational": mix[2]
        }
    }


for unit in business_units:
    name = unit["name"]
    years = unit["years_active"]
    description = unit["description"]

    detected_unit = detect_business_unit(description)
    maturity_score = score_maturity(years)

    disruption_label = extract_disruption_risk(description)
    disruption_score = score_disruption(disruption_label)

    innovation_label = extract_innovation_capability(description)
    innovation_score = score_innovation(innovation_label)

    total = maturity_score + disruption_score + innovation_score
    classification, mix = classify_unit(total)

    print(f"\n{name}")
    print(f"Detected Unit: {detected_unit}")
    print(f"Maturity Score ({years} yrs): {maturity_score}")
    print(f"Disruption Risk: {disruption_label} → Score: {disruption_score}")
    print(f"Innovation Capability: {innovation_label} → Score: {innovation_score}")
    print(f"Total Score: {total}")
    print(f"Classification: {classification}")
    print("Investment Mix:", mix)
    print("—" * 50)


results = []

for unit in business_units:
    output = evaluate_unit(unit["description"], unit["years_active"])
    results.append(output)

# Extract names and mix values
units = [r["name"] for r in results]
core = [r["mix"]["Core"] for r in results]
adjacent = [r["mix"]["Adjacent"] for r in results]
transform = [r["mix"]["Transformational"] for r in results]

# Plot
plt.figure(figsize=(10, 6))
bar1 = plt.bar(units, core, label="Core", color="#4C72B0")
bar2 = plt.bar(units, adjacent, bottom=core, label="Adjacent", color="#55A868")
bar3 = plt.bar(units, transform, bottom=[core[i]+adjacent[i] for i in range(len(core))], label="Transformational", color="#C44E52")

plt.title("Portfolio AI – Innovation Investment Mix by Business Unit")
plt.ylabel("% of Innovation Budget")
plt.ylim(0, 100)
plt.legend()
plt.xticks(rotation=30)
plt.tight_layout()
plt.show()

## ----- Build Dataset from Rule-Based Classifications -----
data = []
for unit in business_units:
    scored = evaluate_unit(unit["description"], unit["years_active"])
    data.append({
        "Name": unit["name"],
        "Maturity": score_maturity(unit["years_active"]),
        "Disruption": score_disruption(extract_disruption_risk(unit["description"])),
        "Innovation": score_innovation(extract_innovation_capability(unit["description"])),
        "YearsActive": unit["years_active"],
        "Label": scored["classification"]
    })

df = pd.DataFrame(data)

# ----- Encode Labels -----
le = LabelEncoder()
df["LabelEncoded"] = le.fit_transform(df["Label"])

# ----- Train Decision Tree -----
tree = DecisionTreeClassifier(max_depth=3, random_state=42)
tree.fit(df[["Maturity", "Disruption", "Innovation"]], df["LabelEncoded"])

# ----- Streamlit app for the Portfolio AI Agent Prototype -----

st.title(" Portfolio AI Agent Prototype")
st.subheader("Simulates strategic innovation planning by evaluating business unit descriptions")

# User input
description = st.text_area(" Paste a business unit description here:", 
"""
Natural Gas Pipelines is a long-standing unit with stable demand. 
It uses legacy systems but has started integrating digital inspection tools. 
There is moderate regulatory pressure.
""", height=180)

years_active = st.slider(" Years Active", 0, 40, 10)
if st.button("Run Agent"):
    result = evaluate_unit(description, years_active)
    st.markdown(f"### Detected Unit: **{result['name']}**")
    st.markdown(f"### Classification: **{result['classification']}**")

    # Add score breakdown
    maturity_score = score_maturity(years_active)
    disruption_label = extract_disruption_risk(description)
    disruption_score = score_disruption(disruption_label)
    innovation_label = extract_innovation_capability(description)
    innovation_score = score_innovation(innovation_label)
    total_score = maturity_score + disruption_score + innovation_score

    st.markdown(f"""
    ####  Scoring Breakdown
    - **Maturity Score** ({years_active} yrs): `{maturity_score}`
    - **Disruption Risk**: `{disruption_label}` → Score: `{disruption_score}`
    - **Innovation Capability**: `{innovation_label}` → Score: `{innovation_score}`
    - **Total Score**: `{total_score}`
    """)

    st.markdown("###  Innovation Investment Mix")

    # Pie chart
    labels = list(result['mix'].keys())
    values = list(result['mix'].values())
    colors = ["#4C72B0", "#55A868", "#C44E52"]

    fig, ax = plt.subplots()
    ax.pie(values, labels=labels, colors=colors, autopct='%1.1f%%', startangle=140)
    ax.axis('equal')
    st.pyplot(fig)

    # Add decision tree visualization
    with st.expander("Show Classification Tree Logic"):
        fig_tree, ax_tree = plt.subplots(figsize=(10, 5))
        plot_tree(tree, feature_names=["Maturity", "Disruption", "Innovation"],
                  class_names=le.classes_, filled=True, rounded=True, fontsize=10)
        st.pyplot(fig_tree)

    # Innovation Recommendations with Tags
    st.markdown("### Recommended Innovation Ideas")

    recommendations_by_unit = {
        "Natural Gas Pipelines": [
            {"name": "AI-Driven Predictive Maintenance", "type": "Adjacent", "desc": "Uses data from SCADA and ILI tools to forecast corrosion and schedule repairs early."},
            {"name": "Green Compression Units", "type": "Adjacent", "desc": "Upgrade compressors to hydrogen-compatible or renewable-powered units."},
            {"name": "Indigenous Infrastructure Partnerships", "type": "Core", "desc": "Offer shared ownership and profit-sharing with Indigenous communities to improve relationship."}
        ],
        "Liquids Pipelines": [
            {"name": "Smart Shutoff via Fiber-Optic Sensors", "type": "Adjacent", "desc": "Enables real-time leak detection with AI analysis."},
            {"name": "Blockchain Traceability", "type": "Transformational", "desc": "Track crude oil origins and handling through immutable blockchain records."},
            {"name": "Emissions-Linked Pricing Model", "type": "Core", "desc": "Allow customers to lower their rates by reducing emissions at origin."}
        ],
        "Renewable Energy": [
            {"name": "Dual-Use Agrivoltaics", "type": "Adjacent", "desc": "Combine solar panels and farmland to optimize land use."},
            {"name": "Floating Solar at Decommissioned Sites", "type": "Transformational", "desc": "Install panels over unused water bodies to avoid land issues."},
            {"name": "Virtual Power Plant (VPP)", "type": "Transformational", "desc": "Use distributed renewables to support pipeline energy demand dynamically."}
        ],
        "Power & Storage": [
            {"name": "AI-Based Optimization Hub", "type": "Core", "desc": "Coordinates energy dispatch across sources to improve peak management."},
            {"name": "Thermal Heat Recovery", "type": "Adjacent", "desc": "Reuse plant heat for district heating or on-site processes."},
        ],
        "Carbon Capture": [
            {"name": "CO2-to-Concrete", "type": "Transformational", "desc": "Use captured carbon in curing concrete to lock in emissions."},
            {"name": "Underground Hydrogen Storage", "type": "Adjacent", "desc": "Dual-use carbon storage sites for seasonal clean fuel storage."},
            {"name": "Bio-CCUS", "type": "Transformational", "desc": "Capture biogenic CO2 from biomass plants and convert to fuels or chemicals."}
        ]
    }

    type_colors = {
        "Core": "#4C72B0",
        "Adjacent":"#55A868",
        "Transformational": "#C44E52"
    }

    ideas = recommendations_by_unit.get(result["name"], [])
    if ideas:
        for idea in ideas:
            tag = idea["type"]
            tag_color = type_colors.get(tag, "#2196F3")
            st.markdown(f"""
                <div style='margin-bottom: 12px; padding: 10px; background-color: #f8f9fa; border-radius: 10px;'>
                    <strong>{idea['name']}</strong><br>
                    <span style='display: inline-block; margin: 6px 0 4px 0; padding: 4px 12px; background-color: {tag_color}; color: white; border-radius: 20px; font-size: 0.8em; font-weight: bold;'>
                        {tag}
                    </span><br>
                    <span style='font-size: 0.92em;'>{idea['desc']}</span>
                </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No tailored recommendations found for this business unit.")


