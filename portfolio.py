# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.22.4",
#     "pandas>=2.3.3",
#     "plotly>=6.5.1",
#     "pyarrow>=22.0.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.23.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    import micropip

    return micropip, mo, pd


@app.cell
def _(pd):
    csv_url = (
        "https://gist.githubusercontent.com/DrAYim/"
        "80393243abdbb4bfe3b45fef58e8d3c8/raw/"
        "acd66213efc7ae2c353ab913e58c694534ae90f7/"
        "sp500_ZScore_avgCoDebt.csv"
    )
    df_final = pd.read_csv(csv_url)
    df_final = df_final.dropna(subset=["AvgCost_of_Debt", "Z_Score_lag", "Sector_Key"])
    df_final = df_final[df_final["AvgCost_of_Debt"] < 5]
    df_final["Debt_Cost_Percent"] = df_final["AvgCost_of_Debt"] * 100
    df_final["Market_Cap_B"] = df_final["Market_Cap"] / 1e9

    def zscore_band(z):
        if z < 1.81:
            return "Distress Zone"
        elif z < 2.99:
            return "Grey Zone"
        else:
            return "Safe Zone"

    df_final["Risk_Band"] = df_final["Z_Score_lag"].apply(zscore_band)
    return (df_final,)


@app.cell
def _(df_final, mo):
    all_sectors = sorted(df_final["Sector_Key"].unique().tolist())
    sector_dropdown = mo.ui.multiselect(
        options=all_sectors,
        value=all_sectors[:4],
        label="Filter by Sector",
    )
    cap_slider = mo.ui.slider(
        start=0,
        stop=200,
        step=10,
        value=0,
        label="Min Market Cap ($ Billions)",
    )
    return cap_slider, sector_dropdown


@app.cell
def _(cap_slider, df_final, sector_dropdown):
    filtered_portfolio = df_final[
        (df_final["Sector_Key"].isin(sector_dropdown.value))
        & (df_final["Market_Cap_B"] >= cap_slider.value)
    ]
    count = len(filtered_portfolio)
    return count, filtered_portfolio


@app.cell
async def _(micropip):
    await micropip.install("plotly")
    import plotly.express as px
    import plotly.graph_objects as go

    return go, px


@app.cell
def _(count, filtered_portfolio, go, mo, pd, px):
    # ── Credit Risk: 2D Scatter ─────────────────────────────────────────────────
    fig_scatter = px.scatter(
        filtered_portfolio,
        x="Z_Score_lag",
        y="Debt_Cost_Percent",
        color="Sector_Key",
        size="Market_Cap_B",
        hover_name="Name",
        title=f"Cost of Debt vs. Altman Z-Score ({count} observations)",
        labels={
            "Z_Score_lag": "Altman Z-Score (lagged)",
            "Debt_Cost_Percent": "Avg. Cost of Debt (%)",
        },
        template="plotly_white",
        height=500,
    )
    fig_scatter.add_vline(
        x=1.81, line_dash="dash", line_color="crimson",
        annotation=dict(text="Distress (Z < 1.81)", font=dict(color="crimson"),
            x=1.5, xref="x", y=0.97, yref="paper", showarrow=False))
    fig_scatter.add_vline(
        x=2.99, line_dash="dash", line_color="seagreen",
        annotation=dict(text="Safe (Z > 2.99)", font=dict(color="seagreen"),
            x=3.08, xref="x", y=0.97, yref="paper", showarrow=False))
    chart_scatter = mo.ui.plotly(fig_scatter)

    # ── Credit Risk: Box Plot ───────────────────────────────────────────────────
    band_order = ["Distress Zone", "Grey Zone", "Safe Zone"]
    band_colors = {
        "Distress Zone": "crimson",
        "Grey Zone": "goldenrod",
        "Safe Zone": "seagreen",
    }
    fig_box = go.Figure()
    for band in band_order:
        subset = filtered_portfolio[filtered_portfolio["Risk_Band"] == band]
        fig_box.add_trace(go.Box(
            y=subset["Debt_Cost_Percent"],
            name=band,
            marker_color=band_colors[band],
            boxmean=True,
        ))
    fig_box.update_layout(
        title="Distribution of Cost of Debt by Z-Score Risk Band",
        yaxis_title="Avg. Cost of Debt (%)",
        template="plotly_white",
        height=420,
    )
    chart_box = mo.ui.plotly(fig_box)

    # ── Credit Risk: 3D Chart ───────────────────────────────────────────────────
    fig_3d = px.scatter_3d(
        filtered_portfolio,
        x="Z_Score_lag",
        y="Debt_Cost_Percent",
        z="Market_Cap_B",
        color="Risk_Band",
        color_discrete_map=band_colors,
        hover_name="Name",
        title=f"3D View: Z-Score · Cost of Debt · Market Cap ({count} observations)",
        labels={
            "Z_Score_lag": "Altman Z-Score (lagged)",
            "Debt_Cost_Percent": "Avg. Cost of Debt (%)",
            "Market_Cap_B": "Market Cap ($ Bn)",
            "Risk_Band": "Risk Band",
        },
        template="plotly_white",
        height=600,
    )
    fig_3d.update_traces(marker=dict(size=4, opacity=0.8))
    chart_3d = mo.ui.plotly(fig_3d)

    # ── Hospitality Analytics charts ────────────────────────────────────────────
    occupancy_data = pd.DataFrame({
        "Month": [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
        ],
        "Ritz_Occupancy_Pct": [72, 68, 81, 88, 84, 91, 96, 98, 87, 82, 75, 94],
        "RevPAR_GBP": [420, 390, 510, 580, 560, 640, 720, 780, 610, 540, 460, 710],
    })
    fig_occupancy = px.line(
        occupancy_data,
        x="Month",
        y="Ritz_Occupancy_Pct",
        title="Simulated Luxury Hotel Occupancy Rate by Month (%)",
        labels={"Month": "Month", "Ritz_Occupancy_Pct": "Occupancy Rate (%)"},
        template="plotly_white",
        height=380,
        markers=True,
    )
    fig_occupancy.update_traces(line_color="goldenrod", marker_color="goldenrod")
    fig_occupancy.add_hline(
        y=80, line_dash="dash", line_color="steelblue",
        annotation_text="Industry benchmark (80%)",
        annotation_position="top right",
    )
    chart_occupancy = mo.ui.plotly(fig_occupancy)

    satisfaction_data = pd.DataFrame({
        "Department": [
            "Front Desk", "Concierge", "Housekeeping",
            "Food & Beverage", "Guest Relations", "Valet",
        ],
        "Satisfaction_Score": [9.2, 8.8, 9.4, 8.6, 9.1, 8.3],
        "Response_Time_Min": [2.1, 4.3, 18.2, 8.6, 3.4, 6.2],
        "Category": [
            "Guest-Facing", "Guest-Facing", "Back-of-House",
            "Guest-Facing", "Guest-Facing", "Guest-Facing",
        ],
    })
    fig_satisfaction = px.scatter(
        satisfaction_data,
        x="Response_Time_Min",
        y="Satisfaction_Score",
        color="Category",
        size="Satisfaction_Score",
        text="Department",
        color_discrete_map={
            "Guest-Facing": "goldenrod",
            "Back-of-House": "steelblue",
        },
        title="Simulated Guest Satisfaction vs Response Time by Department",
        labels={
            "Response_Time_Min": "Avg. Response Time (minutes)",
            "Satisfaction_Score": "Guest Satisfaction Score (out of 10)",
        },
        template="plotly_white",
        height=450,
    )
    fig_satisfaction.update_traces(textposition="top center")
    chart_satisfaction = mo.ui.plotly(fig_satisfaction)

    # ── Football Coaching Analytics ─────────────────────────────────────────────
    player_data = pd.DataFrame({
        "Player": [
            "Player A", "Player B", "Player C", "Player D", "Player E",
            "Player F", "Player G", "Player H", "Player I", "Player J",
        ],
        "Sessions_Attended": [18, 15, 20, 12, 19, 16, 14, 20, 11, 17],
        "Skill_Improvement_Pct": [28, 22, 35, 18, 31, 24, 19, 38, 14, 26],
        "Position": [
            "Goalkeeper", "Defender", "Midfielder", "Defender", "Forward",
            "Midfielder", "Forward", "Midfielder", "Defender", "Forward",
        ],
    })
    position_colors_football = {
        "Goalkeeper": "steelblue",
        "Defender": "seagreen",
        "Midfielder": "goldenrod",
        "Forward": "crimson",
    }
    fig_player = px.scatter(
        player_data,
        x="Sessions_Attended",
        y="Skill_Improvement_Pct",
        color="Position",
        size="Skill_Improvement_Pct",
        text="Player",
        color_discrete_map=position_colors_football,
        title="U9 Coaching — Sessions Attended vs Skill Improvement (%)",
        labels={
            "Sessions_Attended": "Training Sessions Attended",
            "Skill_Improvement_Pct": "Skill Improvement (%)",
        },
        template="plotly_white",
        height=480,
    )
    fig_player.update_traces(textposition="top center")
    chart_player = mo.ui.plotly(fig_player)

    attendance_data = pd.DataFrame({
        "Week": [f"Wk {i}" for i in range(1, 13)],
        "Attendance": [8, 9, 7, 10, 10, 8, 9, 10, 6, 9, 10, 10],
    })
    fig_attendance = px.bar(
        attendance_data,
        x="Week",
        y="Attendance",
        title="U9 Squad Training Attendance by Week",
        labels={"Week": "Training Week", "Attendance": "Players Present"},
        template="plotly_white",
        height=360,
        color="Attendance",
        color_continuous_scale=["crimson", "goldenrod", "seagreen"],
    )
    fig_attendance.update_layout(coloraxis_showscale=False)
    chart_attendance = mo.ui.plotly(fig_attendance)

    # ── Web Scraping: Audit / Big 4 jobs ───────────────────────────────────────
    audit_data = pd.DataFrame({
        "Role_Type": [
            "Audit Graduate", "Tax Graduate", "Advisory Graduate",
            "Audit Internship", "Technology Audit", "Forensic Accounting",
        ],
        "Listings": [41, 28, 22, 19, 14, 9],
        "Avg_Salary_K": [33, 32, 34, 19, 35, 36],
        "Firm_Tier": [
            "Big 4", "Big 4", "Big 4",
            "Big 4", "Big 4", "Big 4",
        ],
    })
    fig_audit = px.bar(
        audit_data,
        x="Role_Type",
        y="Listings",
        color="Avg_Salary_K",
        color_continuous_scale=["steelblue", "seagreen"],
        title="Simulated Output — Big 4 Audit & Accounting Graduate Roles by Type",
        labels={
            "Role_Type": "Role Type",
            "Listings": "Listings Collected",
            "Avg_Salary_K": "Avg. Salary (£k)",
        },
        template="plotly_white",
        height=420,
    )
    fig_audit.update_layout(xaxis_tickangle=-15)
    chart_audit = mo.ui.plotly(fig_audit)

    # ── Travel map ─────────────────────────────────────────────────────────────
    travel_data = pd.DataFrame({
        "City": [
            "London", "Doha", "Dubai", "Marrakech", "Istanbul",
            "Paris", "Amsterdam", "Cairo", "Casablanca", "Madrid",
        ],
        "Lat": [51.5, 25.3, 25.2, 31.6, 41.0, 48.8, 52.4, 30.0, 33.6, 40.4],
        "Lon": [-0.1, 51.5, 55.3, -8.0, 28.9, 2.3, 4.9, 31.2, -7.6, -3.7],
        "Visit_Year": [
            "2022", "2018", "2023", "2022", "2024",
            "2023", "2025", "2021", "2024", "2026",
        ],
    })
    years_travel = sorted(travel_data["Visit_Year"].unique(), key=int)
    fig_travel = px.scatter_geo(
        travel_data,
        lat="Lat", lon="Lon",
        hover_name="City",
        color="Visit_Year",
        category_orders={"Visit_Year": years_travel},
        color_discrete_sequence=px.colors.qualitative.Bold,
        projection="natural earth",
        title="Places I Have Visited",
        labels={"Visit_Year": "Year"},
    )
    fig_travel.update_traces(marker=dict(size=14))
    chart_travel = mo.ui.plotly(fig_travel)

    return (
        chart_scatter, chart_box, chart_3d,
        chart_occupancy, chart_satisfaction,
        chart_player, chart_attendance,
        chart_audit, chart_travel,
    )


@app.cell
def _(
    cap_slider,
    chart_scatter,
    chart_box,
    chart_3d,
    chart_occupancy,
    chart_satisfaction,
    chart_player,
    chart_attendance,
    chart_audit,
    chart_travel,
    mo,
    sector_dropdown,
):
    # ── Tab 1: About Me ─────────────────────────────────────────────────────────
    tab_about = mo.vstack([
        mo.md("""
## Kareem Taha
### BSc Accounting & Finance · Bayes Business School, City St George's, University of London

---

*Profile*

First-year Accounting and Finance student at Bayes Business School with a strong background
in luxury hospitality, customer service, and leadership. Experience working at the Ritz-Carlton
Doha — one of the world's most prestigious five-star hotels — alongside roles at Nando's,
Marks & Spencer, and coaching football at youth level. Fluent in English and Arabic, with
strong organisational, communication, and analytical skills. This portfolio showcases the
technical data science skills I have built through AF1204 Introduction to Data Science and
AI Tools.

---

*Education*

| Qualification | Institution | Period |
|---|---|---|
| BSc Accounting & Finance | Bayes Business School, City St George's, University of London | Sep 2025 – Jun 2028 |
| A-Levels: Economics (B), Maths (B), Psychology (B) | LaSWAP Sixth Form, London | Sep 2022 – Jun 2024 |
| GCSEs: Grades 6–9 (inc. Maths, English, Science, History, Business) | William Ellis School, London | Sep 2017 – Jun 2022 |

---

*Experience*

*Guest Services Assistant — The Ritz-Carlton Doha* (Summer 2024)
- Delivered personalised, high-standard service to international guests in a five-star luxury environment.
- Supported front desk operations, assisting with guest check-ins, enquiries, and requests.
- Handled guest concerns professionally, ensuring swift resolution and satisfaction.
- Coordinated with housekeeping and concierge teams to maintain seamless guest experiences.
- Developed strong communication skills with a diverse, high-end international clientele.

*Host — Nando's, London* (Nov 2025 – Present)
- Welcomed and seated guests, ensuring a positive first impression and smooth service flow.
- Managed bookings, queues, and wait times during busy periods.
- Handled customer enquiries and resolved issues professionally.
- Worked efficiently under pressure whilst delivering consistent customer service.

*Customer Assistant — Marks & Spencer, London* (Nov 2024 – Jan 2025)
- Maintained stock levels and processed transactions efficiently in a busy retail setting.
- Delivered reliable, high-quality customer service.

*Football Coach (U9) — AFA, London* (Aug 2025 – Present)
- Led structured training sessions, building teamwork and discipline in young players.
- Developed leadership and communication skills through managing a squad of ten players.

---

*Skills*

| Category | Detail |
|---|---|
| IT | Microsoft Excel, data handling, introductory coding, Python |
| Languages | English (fluent), Arabic (fluent) |
| Professional | Luxury customer service, front desk operations, problem solving, teamwork, leadership |

---

*Career Goal*

My ambition is to qualify as an auditor at a Big 4 firm, combining the attention to detail
and client-facing skills I developed at the Ritz-Carlton with the analytical and data science
capabilities I am building at Bayes. I am particularly drawn to how audit is evolving —
with data analytics and automation increasingly central to how assurance work is delivered.

---

*Interests*

⚽ Football — coaching U9s at AFA and playing regularly
🌍 Travel — visiting cities across the Middle East, Africa, and Europe
🏨 Luxury hospitality — following the global hotel and tourism industry
📊 Following financial markets and accounting sector developments
        """),
    ])

    # ── Tab 2: Credit Risk Analyser ─────────────────────────────────────────────
    tab_analysis = mo.vstack([
        mo.md("""
## Interactive Credit Risk Analyser
### Skills: Weeks 2, 3 & 4

The Altman Z-Score predicts corporate bankruptcy risk using five financial ratios.
A score below *1.81* signals financial distress; above *2.99* indicates a safe firm.
Using S&P 500 panel data fetched programmatically via Yahoo Finance, I examine whether
a firm's lagged Z-Score (Year t-1) predicts its average cost of debt (Year t).

This analysis is directly relevant to audit — understanding a client's financial health
and bankruptcy risk is a core part of the audit risk assessment process.
        """),
        mo.callout(
            mo.md("Use the filters below to explore the relationship between credit risk and borrowing costs."),
            kind="info",
        ),
        mo.hstack([sector_dropdown, cap_slider], justify="start", gap=2),
        chart_scatter,
        mo.md("---"),
        mo.md("### Distribution of Cost of Debt by Risk Band (Week 3)"),
        mo.md("This box plot shows the spread of borrowing costs within each Z-Score risk category."),
        chart_box,
        mo.md("---"),
        mo.md("### 3D View: Z-Score · Cost of Debt · Market Cap (Week 4 — Self-Exploration)"),
        mo.md("Rotate the chart by clicking and dragging. Larger firms tend to cluster in the Safe Zone, reflecting the financial resilience that comes with scale."),
        chart_3d,
    ])

    # ── Tab 3: Hospitality Analytics ────────────────────────────────────────────
    tab_hospitality = mo.vstack([
        mo.md("""
## Hospitality Analytics Dashboard
### Skills: Weeks 2, 3 & Self-Exploration

*Overview*

During the summer of 2024 I worked as a Guest Services Assistant at the Ritz-Carlton Doha —
one of the world's most prestigious five-star hotels. In this role I developed a strong
appreciation for the operational and financial metrics that drive luxury hospitality
performance: occupancy rates, revenue per available room (RevPAR), guest satisfaction
scores, and departmental response times.

In this tab I apply the data wrangling and visualisation skills from Weeks 2 and 3 to
simulated hospitality data, demonstrating how Python and Plotly can surface operational
insight from the kind of data a luxury hotel generates daily.

---

*Occupancy Rate by Month*

The line chart below shows simulated monthly occupancy for a luxury hotel, with the
industry benchmark of 80% marked as a reference line. Key observations:
- Peak occupancy occurs in summer (Jul–Aug) and over the festive period (Dec)
- The hotel consistently outperforms the 80% benchmark across most months
- February dips below benchmark — a common pattern in luxury hospitality driven by
  reduced corporate and leisure travel

In an audit context, occupancy and RevPAR data would be key inputs when assessing
the going concern status and revenue recognition of a hospitality client.
        """),
        chart_occupancy,
        mo.md("""
---

*Guest Satisfaction vs Response Time by Department*

The bubble chart maps each department's guest satisfaction score against its average
response time, with bubble size reflecting satisfaction. Key observations:
- Housekeeping achieves the highest satisfaction despite the longest response time,
  reflecting the thoroughness of the service rather than its speed
- Front Desk and Guest Relations combine fast response with high satisfaction —
  the hallmark of effective luxury service delivery
- This kind of analysis helps hotel management allocate staffing and training resources
  to the departments where improvement would have the greatest impact on guest experience

*Skills demonstrated:*
- pandas DataFrame construction and column operations (Week 2)
- Plotly Express line chart with reference line annotation (Week 3)
- Bubble scatter chart with text labels — self-explored via Plotly documentation
- Operational interpretation of simulated hospitality performance data
        """),
        chart_satisfaction,
    ])

    # ── Tab 4: Football Coaching Analytics ──────────────────────────────────────
    tab_football = mo.vstack([
        mo.md("""
## Football Coaching Analytics
### Skills: Weeks 2, 3, 7, 8 & 9 — Data Wrangling · Visualisation · Leadership Analytics

*Overview*

Since August 2025 I have been coaching a U9 squad at AFA in London, leading structured
training sessions focused on building teamwork, technical skill, and discipline in young
players. Managing a squad of ten players has developed my leadership, communication, and
organisational skills considerably.

In this tab I apply the data science skills from this module to simulated squad data,
demonstrating how Python and Plotly can be used to track player development and session
attendance — the kind of analysis increasingly used by professional academies to support
youth development decisions.

---

*Player Development — Sessions vs Skill Improvement*

The scatter plot maps each player's training attendance against their percentage skill
improvement over the season, with bubble size reflecting improvement magnitude.
Key observations:
- A clear positive relationship exists between attendance and improvement — players
  who attend more sessions consistently show higher skill development
- Midfielders show the strongest average improvement, likely reflecting the technical
  demands of the position
- This mirrors regression analysis in finance — identifying the independent variables
  that most strongly predict a given outcome

The automation techniques from Week 7 could be applied here to scrape youth football
development data from academy websites at scale. The LLM skills from Weeks 8 and 9
could classify coaching report text by sentiment — identifying which players are
described most positively by coaching staff.
        """),
        chart_player,
        mo.md("""
---

*Squad Attendance by Training Week*

The bar chart shows squad attendance across twelve training weeks, colour-coded from
low (red) to high (green). Key observations:
- Attendance is consistently high, with most weeks seeing nine or ten players present
- Weeks 3 and 9 show dips, likely reflecting school exam periods
- Monitoring attendance patterns helps coaching staff identify disengagement early
  and intervene before it affects player development

*Skills demonstrated:*
- pandas DataFrame construction and sorting (Week 2)
- Plotly Express bubble scatter with text labels (Week 3)
- Plotly bar chart with continuous colour scale — self-explored via documentation
- Cross-domain reasoning linking sports analytics to financial data techniques
        """),
        chart_attendance,
    ])

    # ── Tab 5: Web Scraping Pipeline ────────────────────────────────────────────
    tab_scraping = mo.vstack([
        mo.md("""
## Web Scraping & Automation Pipeline
### Skills: Week 7 — Playwright · PDF Extraction · Bot Evasion

*Overview*

Breaking into audit at a Big 4 firm requires tracking graduate recruitment cycles closely.
Firms like Deloitte, PwC, KPMG, and EY publish graduate scheme listings across multiple
pages of their websites, updating them frequently throughout the year. In Week 7 I built
an automated three-stage pipeline using *Playwright* to collect this data programmatically,
applying it to Big 4 and professional services career pages.

---

*Stage 1 — Bot Evasion & Cookie Handling*

Recruitment pages on large firm websites often block automated scripts.
The script launches a Chromium browser with a realistic user-agent string, suppresses
automation flags, and handles cookie consent banners before saving session data for reuse.

Key techniques:
- Launch Playwright Chromium with a custom user-agent string
- Suppress automation flags (confirmed via screenshot comparison)
- Programmatically click "Accept All" on cookie consent banners
- Save cookies and local storage to cookies.json and localStorage.json

---

*Stage 2 — Web Crawling to Collect Role URLs*

Starting from each firm's careers landing page, the crawler follows links recursively,
collecting URLs matching keywords such as "graduate", "audit", "assurance",
"early careers", and "training contract". PDF brochure links are filtered separately.

Key techniques:
- Recursive web crawling with configurable depth and maximum run time
- Keyword filtering to screen relevant role listing URLs
- Deduplication using a visited URL ledger
- Separate extraction of PDF graduate brochure links

---

*Stage 3 — PDF Download & Role Data Extraction*

For each PDF graduate brochure, the script downloads the file and extracts pages
containing keywords such as "ACA", "salary", "application deadline", and "eligibility".

Key techniques:
- Programmatic PDF download with a ledger to avoid duplicates
- Text extraction using PyMuPDF for searchable PDFs
- OCR fallback for scanned documents
- Page-by-page keyword counting and extraction

---

*Simulated Output — Big 4 Graduate Roles Collected by Type*

The chart below shows the distribution of role types that would be collected across
the Big 4 firms, with colour indicating average salary. Audit Graduate roles dominate
by volume, reflecting the scale of Big 4 audit practices.
        """),
        chart_audit,
        mo.md("""
---

*Why this matters for audit*

Big 4 firms publish graduate recruitment information across hundreds of web pages and
PDF brochures. This pipeline automates the collection and extraction of that information,
giving any aspiring auditor a data-driven view of the recruitment landscape — deadlines,
salary benchmarks, eligibility criteria, and which offices are hiring.
        """),
    ])

    # ── Tab 6: Personal Interests ───────────────────────────────────────────────
    tab_personal = mo.vstack([
        mo.md("""
## Personal Interests

---

*Travel*

I have visited cities across the Middle East, Africa, and Europe — from Doha and Dubai
to Marrakech, Cairo, Istanbul, Paris, Amsterdam, and Madrid. Living and working in Qatar
gave me a direct appreciation for how different economies, cultures, and business
environments operate — something I find directly relevant to the international dimensions
of audit and professional services.
        """),
        chart_travel,
        mo.md("""
---

*Football*

I play football regularly and coach a U9 squad at AFA. Coaching has developed my
leadership, communication, and ability to manage a group of individuals with different
skill levels and learning styles — skills that translate directly into client-facing
roles in professional services.

---

*Luxury Hospitality*

My experience at the Ritz-Carlton gave me a deep appreciation for the operational and
financial complexity of the luxury hotel industry. I continue to follow the global
hospitality and tourism sector closely, tracking how macroeconomic conditions affect
occupancy, RevPAR, and investment in the sector.

---

*Accounting & Audit Developments*

I follow developments in the UK audit market closely — including the FRC's reform agenda,
the separation of audit and consulting practices at the Big 4, and how data analytics
and AI are transforming how assurance work is delivered. These are the trends shaping
the profession I am entering.
        """),
    ])

    # ── Assemble tabs ───────────────────────────────────────────────────────────
    app_tabs = mo.ui.tabs({
        "👤 About Me": tab_about,
        "📊 Credit Risk Analyser": tab_analysis,
        "🏨 Hospitality Analytics": tab_hospitality,
        "⚽ Football Coaching": tab_football,
        "🌐 Web Scraping Pipeline": tab_scraping,
        "✈️ Personal Interests": tab_personal,
    })

    mo.md(f"""
# Kareem Taha
#### BSc Accounting & Finance · Bayes Business School
---
{app_tabs}
""")
    return


if __name__ == "__main__":
    app.run()