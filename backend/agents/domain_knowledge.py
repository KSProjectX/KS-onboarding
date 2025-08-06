import logging
from typing import Dict, Any, List
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DomainKnowledgeAgent:
    """Domain Knowledge Agent for processing industry-specific insights and best practices"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.name = "Domain Knowledge Agent"
        
        # Predefined domain knowledge base
        self.knowledge_base = {
            "automotive": {
                "best_practices": [
                    "Define clear KPIs early in the project",
                    "Use Salesforce Sales Cloud for lead tracking",
                    "Ensure clear customer journey mapping",
                    "Implement robust data analytics for performance tracking",
                    "Focus on scalability for growing lead volumes"
                ],
                "common_challenges": [
                    "Complex lead qualification processes",
                    "Integration with existing CRM systems",
                    "Data quality and consistency issues",
                    "User adoption and training requirements"
                ],
                "recommended_tools": ["Salesforce", "HubSpot", "Pipedrive", "Java", "Python"]
            },
            "healthcare": {
                "best_practices": [
                    "Ensure HIPAA compliance from day one",
                    "Use encrypted databases for patient data",
                    "Conduct regular security audits",
                    "Implement role-based access controls",
                    "Maintain detailed audit logs"
                ],
                "common_challenges": [
                    "Regulatory compliance requirements",
                    "Data security and privacy concerns",
                    "Integration with existing healthcare systems",
                    "User training on compliance procedures"
                ],
                "recommended_tools": ["AWS RDS", "Python", "PostgreSQL", "Docker", "Kubernetes"]
            },
            "retail": {
                "best_practices": [
                    "Simplify checkout forms to reduce abandonment",
                    "Implement one-click checkout options",
                    "Optimize for mobile-first experience",
                    "Use A/B testing for conversion optimization",
                    "Implement real-time inventory management"
                ],
                "common_challenges": [
                    "High cart abandonment rates",
                    "Mobile optimization requirements",
                    "Payment gateway integration",
                    "Inventory synchronization issues"
                ],
                "recommended_tools": ["Shopify", "WooCommerce", "Node.js", "React", "Stripe"]
            }
        }
    
    async def process_domain_knowledge(self, industry: str, problem_statement: str, 
                                     tech_stack: str) -> Dict[str, Any]:
        """Process domain knowledge for the given industry and problem"""
        start_time = datetime.now()
        
        try:
            industry_key = industry.lower()
            
            # Get domain-specific knowledge
            domain_info = self.knowledge_base.get(industry_key, {})
            
            if not domain_info:
                # Generate generic knowledge for unknown industries
                domain_info = self._generate_generic_knowledge(industry, problem_statement)
            
            # Analyze problem statement for specific insights
            problem_insights = self._analyze_problem_statement(problem_statement, domain_info)
            
            # Analyze tech stack compatibility
            tech_analysis = self._analyze_tech_stack(tech_stack, domain_info)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                industry, problem_statement, tech_stack, domain_info
            )
            
            result = {
                "status": "success",
                "agent": self.name,
                "industry": industry,
                "domain_knowledge": {
                    "best_practices": domain_info.get("best_practices", []),
                    "common_challenges": domain_info.get("common_challenges", []),
                    "recommended_tools": domain_info.get("recommended_tools", []),
                    "problem_insights": problem_insights,
                    "tech_analysis": tech_analysis,
                    "recommendations": recommendations
                },
                "confidence_score": self._calculate_confidence_score(industry_key, domain_info)
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            
            logger.info(f"{self.name} completed analysis for {industry} in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return {
                "status": "error",
                "message": f"Domain knowledge processing failed: {str(e)}",
                "agent": self.name
            }
    
    def _analyze_problem_statement(self, problem_statement: str, domain_info: Dict) -> List[str]:
        """Analyze problem statement for domain-specific insights"""
        insights = []
        problem_lower = problem_statement.lower()
        
        # Check for common patterns
        if "lead management" in problem_lower:
            insights.append("Focus on lead qualification and nurturing processes")
            insights.append("Consider implementing lead scoring mechanisms")
        
        if "patient record" in problem_lower or "hipaa" in problem_lower:
            insights.append("Prioritize data security and compliance requirements")
            insights.append("Implement comprehensive audit logging")
        
        if "checkout" in problem_lower or "e-commerce" in problem_lower:
            insights.append("Focus on reducing friction in the purchase process")
            insights.append("Consider mobile-first design principles")
        
        if "salesforce" in problem_lower:
            insights.append("Leverage Salesforce's built-in automation features")
            insights.append("Plan for user training and adoption strategies")
        
        # Add domain-specific insights
        best_practices = domain_info.get("best_practices", [])
        if best_practices:
            insights.extend(best_practices[:2])  # Add top 2 best practices
        
        return insights
    
    def _analyze_tech_stack(self, tech_stack: str, domain_info: Dict) -> Dict[str, Any]:
        """Analyze technology stack compatibility and recommendations"""
        tech_items = [item.strip().lower() for item in tech_stack.split(',')]
        recommended_tools = [tool.lower() for tool in domain_info.get("recommended_tools", [])]
        
        compatible_tools = [tool for tool in tech_items if tool in recommended_tools]
        missing_tools = [tool for tool in recommended_tools if tool not in tech_items]
        
        analysis = {
            "compatible_tools": compatible_tools,
            "missing_recommended_tools": missing_tools[:3],  # Top 3 missing tools
            "compatibility_score": len(compatible_tools) / max(len(recommended_tools), 1),
            "suggestions": []
        }
        
        # Add specific suggestions
        if "python" in tech_items and "healthcare" in str(domain_info):
            analysis["suggestions"].append("Consider using Django for HIPAA-compliant web applications")
        
        if "salesforce" in tech_items:
            analysis["suggestions"].append("Utilize Salesforce APIs for seamless integration")
        
        if "node.js" in tech_items and "retail" in str(domain_info):
            analysis["suggestions"].append("Consider Express.js for building scalable e-commerce APIs")
        
        return analysis
    
    def _generate_recommendations(self, industry: str, problem_statement: str, 
                                tech_stack: str, domain_info: Dict) -> List[str]:
        """Generate specific recommendations based on analysis"""
        recommendations = []
        
        # Industry-specific recommendations
        if industry.lower() == "automotive":
            recommendations.extend([
                "Define KPIs early to avoid project delays",
                "Implement comprehensive lead tracking system",
                "Plan for integration with existing automotive systems"
            ])
        elif industry.lower() == "healthcare":
            recommendations.extend([
                "Use AWS RDS for HIPAA-compliant data storage",
                "Implement end-to-end encryption for patient data",
                "Establish regular compliance audit procedures"
            ])
        elif industry.lower() == "retail":
            recommendations.extend([
                "Implement one-click checkout to improve conversion rates",
                "Optimize checkout flow for mobile devices",
                "Use A/B testing to validate design changes"
            ])
        
        # Problem-specific recommendations
        if "management" in problem_statement.lower():
            recommendations.append("Establish clear process workflows and approval chains")
        
        if "optimization" in problem_statement.lower():
            recommendations.append("Implement analytics to measure optimization impact")
        
        return recommendations
    
    def _generate_generic_knowledge(self, industry: str, problem_statement: str) -> Dict[str, Any]:
        """Generate generic knowledge for unknown industries"""
        return {
            "best_practices": [
                "Define clear project requirements and scope",
                "Implement proper testing and quality assurance",
                "Plan for scalability and future growth",
                "Ensure proper documentation and knowledge transfer"
            ],
            "common_challenges": [
                "Scope creep and changing requirements",
                "Integration with legacy systems",
                "User adoption and training",
                "Performance and scalability issues"
            ],
            "recommended_tools": ["Python", "JavaScript", "PostgreSQL", "Docker", "Git"]
        }
    
    def _calculate_confidence_score(self, industry_key: str, domain_info: Dict) -> float:
        """Calculate confidence score for the domain knowledge"""
        if industry_key in self.knowledge_base:
            return 0.9  # High confidence for known industries
        elif domain_info:
            return 0.6  # Medium confidence for generic knowledge
        else:
            return 0.3  # Low confidence for minimal information
    
    def get_industry_overview(self, industry: str) -> Dict[str, Any]:
        """Get comprehensive industry overview"""
        industry_key = industry.lower()
        domain_info = self.knowledge_base.get(industry_key, {})
        
        if not domain_info:
            return {
                "industry": industry,
                "knowledge_available": False,
                "message": "Limited domain knowledge available for this industry"
            }
        
        return {
            "industry": industry,
            "knowledge_available": True,
            "overview": domain_info,
            "total_best_practices": len(domain_info.get("best_practices", [])),
            "total_challenges": len(domain_info.get("common_challenges", [])),
            "recommended_tools_count": len(domain_info.get("recommended_tools", []))
        }