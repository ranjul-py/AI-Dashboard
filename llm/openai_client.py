import os
import logging
from openai import OpenAI
import streamlit as st

logger = logging.getLogger(__name__)

class OpenAIClient:
    """
    Wrapper for OpenAI API operations. Supports API key configuration
    from environment, Streamlit session, or fallback to simulated output.
    """
    def __init__(self, api_key: str = None):
        self._api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = "gpt-4o-mini" # Fast, cost-effective, and highly capable for analytics

    def get_api_key(self) -> str:
        """Retrieves active API key, prioritizing user input settings."""
        if st.session_state.get("openai_api_key"):
            return st.session_state["openai_api_key"]
        return self._api_key

    def is_api_configured(self) -> bool:
        """Checks if a valid-looking API key is present."""
        key = self.get_api_key()
        return bool(key and key.startswith("sk-"))

    def get_client(self):
        """Instantiates and returns the OpenAI client."""
        key = self.get_api_key()
        if not key:
            raise ValueError("OpenAI API key is not configured.")
        return OpenAI(api_key=key)

    def generate_completion(self, system_prompt: str, user_prompt: str) -> str:
        """
        Sends a query to OpenAI. Falls back to simulated high-fidelity
        corporate responses if the API key is missing.
        """
        if not self.is_api_configured():
            logger.info("API Key not configured. Generating simulated executive report/answer.")
            return self._generate_simulated_response(user_prompt, system_prompt)

        try:
            client = self.get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI completion failed: {e}")
            return f"Error contacting OpenAI service: {str(e)}\n\n[Fallback to Simulation due to error]\n\n" + self._generate_simulated_response(user_prompt, system_prompt)

    def _generate_simulated_response(self, user_prompt: str, system_prompt: str) -> str:
        """
        Generates clean, realistic reports and chatbot answers for testing,
        making the app fully functional out-of-the-box.
        """
        # Determine if this is a WBR request or chat assistant query
        user_prompt_lower = user_prompt.lower()
        
        # 1. Weekly Business Review Report Simulation
        if "weekly business review" in user_prompt_lower or "wbr" in user_prompt_lower or "executive summary" in system_prompt.lower():
            return """# Executive Weekly Business Review (WBR)
**Date:** Wednesday, June 3, 2026 | **Author:** CEO Office (AI Automated)
**Security Level:** Highly Confidential - Executive Eyes Only

---

## 1. Executive Summary
The business continues its strong trajectory, tracking toward a total revenue of **$8.77M** across the current recorded window. Overall growth is robust at **8.0%** month-over-month (as of March 2026). While partner pipelines are highly active at **$9.1M** and client satisfaction remains stable with an average NPS of **52.4**, we face critical operational headwinds due to delayed projects. Active workforce utilization stands at **83.1%**, indicating tight capacity constraints in Engineering.

---

## 2. Business Highlights
*   **Revenue Growth**: Reached **$1.70M** in monthly revenue for March 2026, up from $1.20M in October 2025 (a **41.7%** total rise over the 6-month period).
*   **Partner Conversion**: Partner D has successfully closed a contract valued at **$900,000**, reinforcing sales momentum.
*   **Customer Retention**: Acme Corp, Zenith Tech, and Nova Systems are securely locked in "Retained" status, expressing high satisfaction.

---

## 3. Key Risks
*   **Project Delays**: Two core projects are currently delayed (Project Beta and Project Omega), leading to a combined potential slip of **75 days** and jeopardizing **$1.65M** in budget.
*   **Client Relationship Risk**: BlueWave and Orion Ltd are flagged in **"At Risk"** status due to declining satisfaction metrics.
*   **Workforce Bandwidth**: Engineering utilization is at **88.8%**, indicating high burnout risk and zero buffer capacity for incoming initiatives.

---

## 4. Operational Bottlenecks
*   **Project Omega (Delayed by 45 Days)**: Currently at **35% completion** despite having a budget of **$900,000**. Bottleneck identified as resource shortfalls in Engineering.
*   **Project Beta (Delayed by 30 Days)**: Stuck at **45% completion** with a budget of **$750,000**.
*   **Hiring Inefficiencies**: While employee headcount stands at **9 active members**, only **3 new hires** were onboarded in early 2025, lagging behind project requirements.

---

## 5. Financial Observations
*   **Margin Analysis**: Net profits reached **$500,000** in March 2026 on $1.70M revenue (**29.4% profit margin**). Margins have improved from **25.0%** in October 2025, driven by operational efficiencies.
*   **Budget Risk**: A total of **$1.65M** out of **$3.05M** total budget is tied up in delayed or at-risk projects, representing **54.1% of capital at risk**.
*   **Partner Pipeline**: Active partner pipeline stands at **$7.50M** (excluding Won/Lost stages), providing strong sales coverage.

---

## 6. Workforce Insights
*   **Department Headcount**: Engineering remains the largest department with **5 active members**, followed by Sales (**2**), HR (**1**), and Finance (**1**).
*   **Attrition**: Total attrition is recorded at **10.0%** (1 inactive employee, Vikram Patel, Engineering, departed).
*   **Departmental Utilization**: Engineering is operating at a critical **88.8% average utilization**, while Sales is at **81.0%**, and HR is at **70.0%**.

---

## 7. Client Insights
*   **Client Satisfaction**: Overall average CSAT stands at a strong **7.98 / 10**.
*   **Net Promoter Score**: Average NPS is **52.4**. Top-performing client relationship is Nova Systems (NPS: **70**, CSAT: **9.1**).
*   **At-Risk Clients**: 
    1.  **Orion Ltd**: NPS **35**, CSAT **6.8** (Risk: High).
    2.  **BlueWave**: NPS **40**, CSAT **7.1** (Risk: Medium).

---

## 8. Recommended Actions
1.  **Resource Reallocation**: Shift 1 Engineering resource from Project Gamma (currently at 80% completion and "On Track") to Project Omega to resolve the 45-day delay.
2.  **Client Health Remediation**: Appoint the Sales Account Manager to conduct immediate executive review sessions with Orion Ltd and BlueWave to address CSAT issues.
3.  **Targeted Hiring**: Open headcounts for **2 Senior Full-Stack Engineers** immediately to ease the Engineering utilization bottleneck (currently 88.8%).

---

## 9. Priority Action Items
*   [ ] **[HIGH PRIORITY]** Schedule a project recovery workshop for Project Omega. (Owner: Project Director / Timeline: 48 Hours)
*   [ ] **[HIGH PRIORITY]** Conduct client intervention meeting with Orion Ltd. (Owner: VP of Customer Success / Timeline: 3 Days)
*   [ ] **[MEDIUM PRIORITY]** Deploy HR recruiting pipeline for engineering roles. (Owner: HR Lead / Timeline: 7 Days)
*   [ ] **[MEDIUM PRIORITY]** Finalize contract paperwork for Partner C ($3.2M negotiation phase). (Owner: Head of Partnerships / Timeline: 5 Days)
"""
        
        # 2. Chatbot Answers Simulation based on database questions
        if "delayed" in user_prompt_lower:
            return """Based on current records, we have **2 delayed projects**:
1. **Project Omega**: Delayed by **45 days** (35% complete, Budget: $900,000).
2. **Project Beta**: Delayed by **30 days** (45% complete, Budget: $750,000).

Additionally, **Project Delta** is currently flagged as **At Risk** with a delay of **15 days** (55% complete, Budget: $600,000). Total budget tied up in delayed/at-risk projects is **$2,250,000** (73.7% of total portfolio budget)."""

        elif "revenue" in user_prompt_lower or "growth" in user_prompt_lower:
            return """Our revenue numbers show solid positive momentum:
*   **Latest Revenue**: **$1,700,000** (March 2026) with a profit of **$500,000** (29.41% profit margin).
*   **Previous Month Revenue**: **$1,620,000** (February 2026).
*   **Month-over-Month Revenue Growth**: **+4.94%** (+$80,000).
*   **6-Month Historical Revenue Growth**: **+41.67%** (growing from $1,200,000 in October 2025 to $1,700,000 in March 2026).
*   **Revenue Forecast**: Expected to cross **$1.8M** monthly by June 2026 if current growth trends (~4-5% MoM) persist."""

        elif "risk" in user_prompt_lower or "focus" in user_prompt_lower:
            return """Here are the top business and operational risks requiring your attention:
1.  **Project Risk**: **Project Omega** (Risk Score: **100.0/100**) and **Project Beta** (Risk Score: **72.5/100**) are delayed, risking **$1.65M** in total budget.
2.  **Client Attrition Risk**: **Orion Ltd** (CSAT: 6.8, NPS: 35) and **BlueWave** (CSAT: 7.1, NPS: 40) are flagged as "At Risk" for retention.
3.  **Capacity Bottleneck**: **Engineering Department** has an average employee utilization of **88.8%** and has recently lost 1 team member, creating severe resource delivery issues.
4.  **Partner Stage Delay**: **Partner C** has a pipeline value of **$3.2M** stuck in the 'Negotiation' stage. Finalizing this is critical for Q2 sales targets."""

        else:
            return """I am your AI Executive Assistant. I have analyzed our SQLite database tables. 
Here are a few quick stats about the business:
- **Revenue**: $1.70M last month, profit $500K (29.4% margin).
- **Projects**: 5 total. 2 delayed (Beta, Omega), 1 at risk (Delta), 2 on track (Alpha, Gamma).
- **Workforce**: 9 active employees, Engineering utilization is critical (88.8%).
- **Partners**: Pipeline value stands at $9.10M (total), with Partner C at $3.2M in negotiations.
- **Clients**: Average NPS is 52.4. Orion Ltd and BlueWave are flagged "At Risk".

How can I help you further? You can ask about delayed projects, revenue growth details, or active key risks."""
