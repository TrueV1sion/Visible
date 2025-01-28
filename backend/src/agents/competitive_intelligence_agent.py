class CompetitiveIntelligenceAgent:
    def __init__(self):
        pass

    def compare_competitor_vs_our_product(self, competitor_info, our_product_info):
        """
        Returns a diff or a structured comparison between competitor data and our product data.
        """
        comparison_result = {
            "pricing": "Competitor is cheaper by 10%" if "discount" in competitor_info else "Pricing is comparable",
            "features": "They released a new integration we don't have yet",
        }
        return comparison_result

    def run(self, competitor_info, our_product_info):
        return self.compare_competitor_vs_our_product(competitor_info, our_product_info) 