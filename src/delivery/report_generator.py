import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Reads processed AI clusters and formats them into a professional Markdown One-Pager."""

    def __init__(self):
        self.insights_dir = Path("data/insights")
        self.insights_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(self, clusters_data: List[Dict[str, Any]], timestamp: str = None) -> str:
        if not timestamp:
            timestamp = datetime.now().strftime("%Y-%m")
            
        report_path = self.insights_dir / f"report_{timestamp}.md"
        
        # Filter out noise cluster
        valid_clusters = [c for c in clusters_data if c.get("cluster_id", -1) != -1]
        
        # Sort clusters by size (most impactful first)
        valid_clusters.sort(key=lambda x: x.get("size", 0), reverse=True)

        md_content = f"# Blinkit Discovery Engine - Monthly Insight Report ({timestamp})\n\n"
        md_content += "## Executive Summary\n"
        md_content += f"This automated report synthesizes user feedback across the App Store, Play Store, and Reddit into actionable insights, categorized by the 4 Discovery Pillars. This month, we identified **{len(valid_clusters)}** major recurring themes.\n\n"
        md_content += "---\n\n"

        # Group by Pillar
        pillars = ["Habit & Velocity", "Trust & Information", "UX Friction", "Segment Propensity"]
        
        for pillar in pillars:
            pillar_clusters = [c for c in valid_clusters if c.get("pillar") == pillar]
            
            if not pillar_clusters:
                continue
                
            md_content += f"## 🏛️ Pillar: {pillar}\n\n"
            
            for cluster in pillar_clusters:
                md_content += f"### 🔴 {cluster.get('theme_name', 'Unnamed Theme')} (Impact: {cluster.get('size', 0)} users)\n"
                md_content += f"> *\"{cluster.get('best_quote', 'No quote available.')}\"*\n\n"
                md_content += f"**Actionable Insight:** {cluster.get('actionable_insight', 'N/A')}\n\n"
                
            md_content += "---\n\n"

        with open(report_path, "w") as f:
            f.write(md_content)
            
        logger.info(f"Generated Markdown Report at {report_path}")
        return str(report_path)
