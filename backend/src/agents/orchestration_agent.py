from .aggregator_agent import AggregatorAgent
from .summarization_agent import SummarizationAgent
from .competitive_intelligence_agent import CompetitiveIntelligenceAgent
from .objection_handling_agent import ObjectionHandlingAgent

class OrchestrationAgent:
    def __init__(self):
        self.aggregator = AggregatorAgent()
        self.summarizer = SummarizationAgent()
        self.competitive = CompetitiveIntelligenceAgent()
        self.objections_agent = ObjectionHandlingAgent()

    def run_all(self):
        # 1. Aggregate Data
        aggregated_data = self.aggregator.run()

        # 2. Summarize relevant sections
        competitor_updates = aggregated_data.get("competitor_updates", [])
        combined_competitor_text = " ".join(competitor_updates)
        summarized_competitor_info = self.summarizer.run(combined_competitor_text)

        # 3. Run competitive comparison
        our_product_info = "Key features: ..."  # Placeholder
        comp_analysis = self.competitive.run(summarized_competitor_info, our_product_info)

        # 4. Gather and respond to objections
        crm_data = {}  # Placeholder
        support_tickets = {}  # Placeholder
        objections = self.objections_agent.run(crm_data, support_tickets)

        # Combine all outputs
        return {
            "summarized_competitors": summarized_competitor_info,
            "competitive_analysis": comp_analysis,
            "objections_responses": objections
        } 