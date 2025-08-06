import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ActionableInsightsAgent:
    """Actionable Insights Agent for synthesizing outputs and generating recommendations"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.name = "Actionable Insights Agent"
    
    async def generate_insights(self, client_name: str, domain_knowledge: Dict[str, Any],
                              client_profile: Dict[str, Any], meeting_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate actionable insights by synthesizing all agent outputs"""
        start_time = datetime.now()
        
        try:
            # Generate strategic recommendations
            strategic_recommendations = self._generate_strategic_recommendations(
                domain_knowledge, client_profile, meeting_analysis
            )
            
            # Generate tactical action items
            tactical_actions = self._generate_tactical_actions(
                domain_knowledge, client_profile, meeting_analysis
            )
            
            # Generate risk assessments
            risk_assessment = self._assess_risks(
                domain_knowledge, client_profile, meeting_analysis
            )
            
            # Generate success metrics
            success_metrics = self._define_success_metrics(
                domain_knowledge, client_profile, meeting_analysis
            )
            
            # Generate timeline recommendations
            timeline = self._generate_timeline_recommendations(
                domain_knowledge, client_profile, meeting_analysis
            )
            
            # Generate resource recommendations
            resources = self._recommend_resources(
                domain_knowledge, client_profile, meeting_analysis
            )
            
            # Calculate overall project health score
            health_score = self._calculate_project_health_score(
                domain_knowledge, client_profile, meeting_analysis
            )
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(
                client_name, strategic_recommendations, risk_assessment, health_score
            )
            
            result = {
                "status": "success",
                "agent": self.name,
                "client_name": client_name,
                "insights": {
                    "executive_summary": executive_summary,
                    "strategic_recommendations": strategic_recommendations,
                    "tactical_actions": tactical_actions,
                    "risk_assessment": risk_assessment,
                    "success_metrics": success_metrics,
                    "timeline_recommendations": timeline,
                    "resource_recommendations": resources,
                    "project_health_score": health_score,
                    "generated_at": datetime.now().isoformat()
                }
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            
            logger.info(f"{self.name} completed insights for {client_name} in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return {
                "status": "error",
                "message": f"Insights generation failed: {str(e)}",
                "agent": self.name
            }
    
    def _generate_strategic_recommendations(self, domain_knowledge: Dict, 
                                          client_profile: Dict, meeting_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate high-level strategic recommendations"""
        recommendations = []
        
        # Extract key information
        industry = client_profile.get("industry", "")
        best_practices = domain_knowledge.get("domain_knowledge", {}).get("best_practices", [])
        sentiment = meeting_analysis.get("meeting_analysis", {}).get("sentiment", {})
        
        # Industry-specific strategic recommendations
        if industry.lower() == "automotive":
            recommendations.extend([
                {
                    "title": "Establish Clear KPI Framework",
                    "description": "Define measurable KPIs early to track lead management success",
                    "priority": "high",
                    "category": "strategy",
                    "impact": "Prevents scope creep and ensures measurable outcomes"
                },
                {
                    "title": "Implement Phased Rollout",
                    "description": "Deploy Salesforce implementation in phases to minimize risk",
                    "priority": "medium",
                    "category": "implementation",
                    "impact": "Reduces implementation risk and allows for iterative improvements"
                }
            ])
        elif industry.lower() == "healthcare":
            recommendations.extend([
                {
                    "title": "Prioritize Compliance Framework",
                    "description": "Establish HIPAA compliance as the foundation for all development",
                    "priority": "high",
                    "category": "compliance",
                    "impact": "Ensures regulatory compliance and avoids costly violations"
                },
                {
                    "title": "Implement Security-First Architecture",
                    "description": "Design system architecture with security as the primary concern",
                    "priority": "high",
                    "category": "security",
                    "impact": "Protects patient data and maintains trust"
                }
            ])
        elif industry.lower() == "retail":
            recommendations.extend([
                {
                    "title": "Focus on Conversion Optimization",
                    "description": "Prioritize checkout flow optimization to maximize conversions",
                    "priority": "high",
                    "category": "optimization",
                    "impact": "Directly impacts revenue through improved conversion rates"
                },
                {
                    "title": "Mobile-First Approach",
                    "description": "Design and optimize for mobile experience first",
                    "priority": "medium",
                    "category": "user_experience",
                    "impact": "Captures growing mobile commerce market"
                }
            ])
        
        # Sentiment-based recommendations
        sentiment_category = sentiment.get("category", "neutral")
        if sentiment_category == "negative":
            recommendations.append({
                "title": "Address Stakeholder Concerns",
                "description": "Proactively address concerns identified in meeting sentiment analysis",
                "priority": "high",
                "category": "stakeholder_management",
                "impact": "Improves stakeholder buy-in and project success probability"
            })
        elif sentiment_category == "positive":
            recommendations.append({
                "title": "Leverage Positive Momentum",
                "description": "Capitalize on positive stakeholder sentiment to accelerate progress",
                "priority": "medium",
                "category": "momentum",
                "impact": "Accelerates project timeline and improves outcomes"
            })
        
        return recommendations
    
    def _generate_tactical_actions(self, domain_knowledge: Dict, 
                                 client_profile: Dict, meeting_analysis: Dict) -> List[Dict[str, Any]]:
        """Generate specific tactical action items"""
        actions = []
        
        # Extract meeting action items
        meeting_actions = meeting_analysis.get("meeting_analysis", {}).get("action_items", [])
        
        # Convert meeting action items to tactical actions
        for item in meeting_actions:
            actions.append({
                "title": item.get("item", "Unknown action"),
                "type": item.get("type", "general"),
                "priority": item.get("priority", "medium"),
                "source": "meeting_analysis",
                "estimated_effort": self._estimate_effort(item.get("item", "")),
                "dependencies": []
            })
        
        # Add domain-specific tactical actions
        tech_analysis = domain_knowledge.get("domain_knowledge", {}).get("tech_analysis", {})
        missing_tools = tech_analysis.get("missing_recommended_tools", [])
        
        for tool in missing_tools[:3]:  # Top 3 missing tools
            actions.append({
                "title": f"Evaluate {tool.capitalize()} integration",
                "type": "evaluation",
                "priority": "medium",
                "source": "domain_knowledge",
                "estimated_effort": "1-2 weeks",
                "dependencies": ["Technical assessment"]
            })
        
        # Add profile-based actions
        current_project = client_profile.get("current_project", {})
        complexity = current_project.get("complexity_level", "medium")
        
        if complexity == "high":
            actions.append({
                "title": "Conduct detailed technical architecture review",
                "type": "planning",
                "priority": "high",
                "source": "complexity_analysis",
                "estimated_effort": "2-3 weeks",
                "dependencies": ["Stakeholder alignment"]
            })
        
        return actions
    
    def _assess_risks(self, domain_knowledge: Dict, 
                     client_profile: Dict, meeting_analysis: Dict) -> Dict[str, Any]:
        """Assess project risks based on all available data"""
        risks = []
        
        # Technical risks
        tech_analysis = domain_knowledge.get("domain_knowledge", {}).get("tech_analysis", {})
        compatibility_score = tech_analysis.get("compatibility_score", 1.0)
        
        if compatibility_score < 0.5:
            risks.append({
                "category": "technical",
                "risk": "Low technology stack compatibility",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Conduct detailed technical assessment and consider alternative tools"
            })
        
        # Complexity risks
        current_project = client_profile.get("current_project", {})
        complexity = current_project.get("complexity_level", "medium")
        
        if complexity == "high":
            risks.append({
                "category": "complexity",
                "risk": "High project complexity may lead to delays",
                "probability": "medium",
                "impact": "medium",
                "mitigation": "Break down into smaller phases and increase testing"
            })
        
        # Stakeholder risks
        sentiment = meeting_analysis.get("meeting_analysis", {}).get("sentiment", {})
        if sentiment.get("category") == "negative":
            risks.append({
                "category": "stakeholder",
                "risk": "Negative stakeholder sentiment may impact project support",
                "probability": "medium",
                "impact": "high",
                "mitigation": "Increase communication and address specific concerns"
            })
        
        # Industry-specific risks
        industry = client_profile.get("industry", "")
        if industry.lower() == "healthcare":
            risks.append({
                "category": "compliance",
                "risk": "HIPAA compliance requirements may extend timeline",
                "probability": "high",
                "impact": "medium",
                "mitigation": "Allocate additional time for compliance review and testing"
            })
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(risks)
        
        return {
            "risks": risks,
            "overall_risk_score": risk_score,
            "risk_level": self._categorize_risk_level(risk_score),
            "top_concerns": [r["risk"] for r in risks[:3]]
        }
    
    def _define_success_metrics(self, domain_knowledge: Dict, 
                              client_profile: Dict, meeting_analysis: Dict) -> List[Dict[str, Any]]:
        """Define success metrics for the project"""
        metrics = []
        
        # Industry-specific metrics
        industry = client_profile.get("industry", "")
        
        if industry.lower() == "automotive":
            metrics.extend([
                {"name": "Lead Conversion Rate", "target": "15% improvement", "measurement": "Monthly"},
                {"name": "Sales Cycle Time", "target": "20% reduction", "measurement": "Quarterly"},
                {"name": "User Adoption Rate", "target": "80% within 3 months", "measurement": "Monthly"}
            ])
        elif industry.lower() == "healthcare":
            metrics.extend([
                {"name": "Data Accuracy", "target": "99.5%", "measurement": "Daily"},
                {"name": "Compliance Score", "target": "100%", "measurement": "Monthly"},
                {"name": "System Uptime", "target": "99.9%", "measurement": "Daily"}
            ])
        elif industry.lower() == "retail":
            metrics.extend([
                {"name": "Conversion Rate", "target": "25% improvement", "measurement": "Daily"},
                {"name": "Cart Abandonment Rate", "target": "30% reduction", "measurement": "Weekly"},
                {"name": "Mobile Conversion Rate", "target": "20% improvement", "measurement": "Weekly"}
            ])
        
        # Universal metrics
        metrics.extend([
            {"name": "Project Timeline Adherence", "target": "95%", "measurement": "Weekly"},
            {"name": "Budget Variance", "target": "<5%", "measurement": "Monthly"},
            {"name": "Stakeholder Satisfaction", "target": "4.5/5", "measurement": "Monthly"}
        ])
        
        return metrics
    
    def _generate_timeline_recommendations(self, domain_knowledge: Dict, 
                                         client_profile: Dict, meeting_analysis: Dict) -> Dict[str, Any]:
        """Generate timeline recommendations"""
        complexity = client_profile.get("current_project", {}).get("complexity_level", "medium")
        industry = client_profile.get("industry", "")
        
        # Base timeline estimates
        base_timeline = {
            "low": {"planning": 2, "development": 8, "testing": 3, "deployment": 1},
            "medium": {"planning": 3, "development": 12, "testing": 4, "deployment": 2},
            "high": {"planning": 4, "development": 16, "testing": 6, "deployment": 3}
        }
        
        timeline = base_timeline.get(complexity, base_timeline["medium"])
        
        # Industry adjustments
        if industry.lower() == "healthcare":
            timeline["testing"] += 2  # Additional compliance testing
            timeline["planning"] += 1  # Additional compliance planning
        
        total_weeks = sum(timeline.values())
        
        return {
            "phases": timeline,
            "total_duration_weeks": total_weeks,
            "recommended_start_date": datetime.now().strftime("%Y-%m-%d"),
            "critical_path": ["planning", "development", "testing"],
            "buffer_recommendation": "20% additional time for unforeseen challenges"
        }
    
    def _recommend_resources(self, domain_knowledge: Dict, 
                           client_profile: Dict, meeting_analysis: Dict) -> Dict[str, Any]:
        """Recommend required resources"""
        complexity = client_profile.get("current_project", {}).get("complexity_level", "medium")
        industry = client_profile.get("industry", "")
        
        # Base resource requirements
        base_resources = {
            "low": {"developers": 2, "designers": 1, "project_managers": 1, "qa_engineers": 1},
            "medium": {"developers": 3, "designers": 1, "project_managers": 1, "qa_engineers": 2},
            "high": {"developers": 5, "designers": 2, "project_managers": 2, "qa_engineers": 3}
        }
        
        resources = base_resources.get(complexity, base_resources["medium"])
        
        # Industry-specific additions
        if industry.lower() == "healthcare":
            resources["compliance_specialists"] = 1
            resources["security_experts"] = 1
        elif industry.lower() == "automotive":
            resources["business_analysts"] = 1
        
        return {
            "team_composition": resources,
            "total_team_size": sum(resources.values()),
            "specialized_roles": self._identify_specialized_roles(industry),
            "external_consultants": self._recommend_consultants(industry, complexity)
        }
    
    def _calculate_project_health_score(self, domain_knowledge: Dict, 
                                      client_profile: Dict, meeting_analysis: Dict) -> Dict[str, Any]:
        """Calculate overall project health score"""
        scores = []
        
        # Technical compatibility score
        tech_score = domain_knowledge.get("domain_knowledge", {}).get("tech_analysis", {}).get("compatibility_score", 0.5)
        scores.append(tech_score * 100)
        
        # Stakeholder sentiment score
        sentiment = meeting_analysis.get("meeting_analysis", {}).get("sentiment", {})
        sentiment_polarity = sentiment.get("polarity", 0)
        sentiment_score = max(0, (sentiment_polarity + 1) * 50)  # Convert -1,1 to 0,100
        scores.append(sentiment_score)
        
        # Profile completeness score
        completeness_score = client_profile.get("completeness_score", 0.5) * 100
        scores.append(completeness_score)
        
        # Domain knowledge confidence
        confidence_score = domain_knowledge.get("confidence_score", 0.5) * 100
        scores.append(confidence_score)
        
        overall_score = sum(scores) / len(scores)
        
        return {
            "overall_score": round(overall_score, 1),
            "health_level": self._categorize_health_level(overall_score),
            "component_scores": {
                "technical_compatibility": round(tech_score * 100, 1),
                "stakeholder_sentiment": round(sentiment_score, 1),
                "profile_completeness": round(completeness_score, 1),
                "domain_knowledge": round(confidence_score, 1)
            },
            "recommendations": self._generate_health_recommendations(overall_score)
        }
    
    def _generate_executive_summary(self, client_name: str, strategic_recommendations: List, 
                                  risk_assessment: Dict, health_score: Dict) -> str:
        """Generate executive summary"""
        health_level = health_score.get("health_level", "medium")
        risk_level = risk_assessment.get("risk_level", "medium")
        top_recommendation = strategic_recommendations[0]["title"] if strategic_recommendations else "No specific recommendations"
        
        summary = f"""
        Executive Summary for {client_name}:
        
        Project Health: {health_level.capitalize()} ({health_score.get('overall_score', 0)}%)
        Risk Level: {risk_level.capitalize()}
        
        Key Recommendation: {top_recommendation}
        
        The project shows {health_level} potential for success with {risk_level} risk factors identified. 
        Immediate focus should be on {top_recommendation.lower()} to ensure optimal outcomes.
        
        Total Strategic Recommendations: {len(strategic_recommendations)}
        Critical Risks Identified: {len(risk_assessment.get('risks', []))}
        """
        
        return summary.strip()
    
    # Helper methods
    def _estimate_effort(self, action_item: str) -> str:
        """Estimate effort for action item"""
        if any(word in action_item.lower() for word in ["plan", "design", "architect"]):
            return "2-3 weeks"
        elif any(word in action_item.lower() for word in ["implement", "develop", "build"]):
            return "4-6 weeks"
        elif any(word in action_item.lower() for word in ["test", "verify"]):
            return "1-2 weeks"
        else:
            return "1 week"
    
    def _calculate_risk_score(self, risks: List) -> float:
        """Calculate overall risk score"""
        if not risks:
            return 0.2
        
        risk_values = {"low": 0.3, "medium": 0.6, "high": 0.9}
        total_score = sum(risk_values.get(risk.get("probability", "medium"), 0.6) for risk in risks)
        return min(total_score / len(risks), 1.0)
    
    def _categorize_risk_level(self, risk_score: float) -> str:
        """Categorize risk level"""
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _categorize_health_level(self, health_score: float) -> str:
        """Categorize health level"""
        if health_score >= 80:
            return "excellent"
        elif health_score >= 60:
            return "good"
        elif health_score >= 40:
            return "fair"
        else:
            return "poor"
    
    def _identify_specialized_roles(self, industry: str) -> List[str]:
        """Identify specialized roles needed"""
        roles = {
            "healthcare": ["HIPAA Compliance Specialist", "Healthcare IT Consultant"],
            "automotive": ["CRM Specialist", "Sales Process Analyst"],
            "retail": ["E-commerce Specialist", "UX/UI Designer"]
        }
        return roles.get(industry.lower(), ["Business Analyst"])
    
    def _recommend_consultants(self, industry: str, complexity: str) -> List[str]:
        """Recommend external consultants"""
        if complexity == "high":
            return ["Senior Technical Architect", "Industry Expert"]
        elif industry.lower() == "healthcare":
            return ["HIPAA Compliance Consultant"]
        else:
            return []
    
    def _generate_health_recommendations(self, health_score: float) -> List[str]:
        """Generate recommendations based on health score"""
        if health_score < 40:
            return [
                "Conduct immediate stakeholder alignment meeting",
                "Review and adjust project scope",
                "Consider bringing in additional expertise"
            ]
        elif health_score < 60:
            return [
                "Increase communication frequency",
                "Review technical approach",
                "Validate requirements with stakeholders"
            ]
        else:
            return [
                "Maintain current momentum",
                "Focus on execution excellence",
                "Prepare for scaling"
            ]