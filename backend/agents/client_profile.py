import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ClientProfileAgent:
    """Client Profile Agent for building detailed client profiles"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.name = "Client Profile Agent"
    
    async def build_client_profile(self, client_name: str, industry: str, 
                                 problem_statement: str, tech_stack: str) -> Dict[str, Any]:
        """Build comprehensive client profile from input data"""
        start_time = datetime.now()
        
        try:
            # Check if client profile already exists in database
            existing_profiles = self.db_manager.get_client_profiles()
            existing_profile = None
            
            for profile in existing_profiles:
                if profile["client_name"].lower() == client_name.lower():
                    existing_profile = profile
                    break
            
            if existing_profile:
                # Use existing profile and enhance it
                profile_data = existing_profile["profile_data"]
                logger.info(f"Found existing profile for {client_name}")
            else:
                # Create new profile
                profile_data = self._create_new_profile(client_name, industry, problem_statement, tech_stack)
                logger.info(f"Created new profile for {client_name}")
            
            # Enhance profile with additional insights
            enhanced_profile = self._enhance_profile(profile_data, industry, problem_statement, tech_stack)
            
            # Calculate profile completeness
            completeness_score = self._calculate_profile_completeness(enhanced_profile)
            
            # Generate profile insights
            insights = self._generate_profile_insights(enhanced_profile, industry, problem_statement)
            
            result = {
                "status": "success",
                "agent": self.name,
                "client_profile": enhanced_profile,
                "completeness_score": completeness_score,
                "insights": insights,
                "profile_exists": existing_profile is not None
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            
            logger.info(f"{self.name} completed profile for {client_name} in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return {
                "status": "error",
                "message": f"Client profile building failed: {str(e)}",
                "agent": self.name
            }
    
    def _create_new_profile(self, client_name: str, industry: str, 
                          problem_statement: str, tech_stack: str) -> Dict[str, Any]:
        """Create a new client profile from scratch"""
        # Extract company size estimation from problem complexity
        company_size = self._estimate_company_size(problem_statement, tech_stack)
        
        # Estimate founding year based on industry and tech stack
        founded_year = self._estimate_founding_year(industry, tech_stack)
        
        # Determine likely regions based on industry
        regions = self._determine_regions(industry)
        
        # Generate stakeholder roles based on problem statement
        stakeholders = self._generate_stakeholders(problem_statement, industry)
        
        profile = {
            "name": client_name,
            "industry": industry,
            "founded": founded_year,
            "company_size": company_size,
            "region": regions,
            "stakeholders": stakeholders,
            "tech_stack": [tech.strip() for tech in tech_stack.split(',')],
            "primary_challenge": self._extract_primary_challenge(problem_statement),
            "profile_created": datetime.now().isoformat(),
            "profile_source": "generated"
        }
        
        return profile
    
    def _enhance_profile(self, profile_data: Dict[str, Any], industry: str, 
                        problem_statement: str, tech_stack: str) -> Dict[str, Any]:
        """Enhance existing profile with additional information"""
        enhanced = profile_data.copy()
        
        # Update tech stack if new information is available
        current_tech = enhanced.get("tech_stack", [])
        new_tech = [tech.strip() for tech in tech_stack.split(',')]
        
        # Merge tech stacks
        all_tech = list(set(current_tech + new_tech))
        enhanced["tech_stack"] = all_tech
        
        # Add project context
        enhanced["current_project"] = {
            "problem_statement": problem_statement,
            "technologies": new_tech,
            "project_type": self._classify_project_type(problem_statement),
            "complexity_level": self._assess_complexity(problem_statement, tech_stack)
        }
        
        # Add business context
        enhanced["business_context"] = self._generate_business_context(industry, problem_statement)
        
        # Update last modified
        enhanced["last_updated"] = datetime.now().isoformat()
        
        return enhanced
    
    def _estimate_company_size(self, problem_statement: str, tech_stack: str) -> str:
        """Estimate company size based on problem complexity and tech stack"""
        complexity_indicators = [
            "enterprise", "scale", "multiple", "integration", "complex",
            "large", "global", "distributed", "microservices"
        ]
        
        problem_lower = problem_statement.lower()
        tech_lower = tech_stack.lower()
        
        complexity_score = sum(1 for indicator in complexity_indicators 
                             if indicator in problem_lower or indicator in tech_lower)
        
        if complexity_score >= 3:
            return "Large (1000+ employees)"
        elif complexity_score >= 1:
            return "Medium (100-1000 employees)"
        else:
            return "Small (10-100 employees)"
    
    def _estimate_founding_year(self, industry: str, tech_stack: str) -> int:
        """Estimate founding year based on industry and technology choices"""
        current_year = datetime.now().year
        
        # Modern tech stack suggests newer company
        modern_tech = ["react", "node.js", "kubernetes", "docker", "aws", "microservices"]
        tech_lower = tech_stack.lower()
        
        modern_score = sum(1 for tech in modern_tech if tech in tech_lower)
        
        if modern_score >= 2:
            return current_year - (5 + (modern_score * 2))  # 5-15 years old
        elif industry.lower() in ["automotive", "healthcare"]:
            return current_year - (20 + (modern_score * 5))  # Older established industries
        else:
            return current_year - (10 + (modern_score * 3))  # Medium age
    
    def _determine_regions(self, industry: str) -> str:
        """Determine likely operational regions based on industry"""
        industry_regions = {
            "automotive": "USA, Europe, Asia",
            "healthcare": "USA, Canada",
            "retail": "Global",
            "technology": "USA, Europe",
            "finance": "USA, Europe, Asia",
            "manufacturing": "USA, Europe, Asia"
        }
        
        return industry_regions.get(industry.lower(), "USA")
    
    def _generate_stakeholders(self, problem_statement: str, industry: str) -> List[Dict[str, str]]:
        """Generate likely stakeholders based on problem statement and industry"""
        stakeholders = []
        problem_lower = problem_statement.lower()
        
        # Always include CTO for tech projects
        stakeholders.append({"name": "Technical Lead", "role": "CTO"})
        
        # Add role-specific stakeholders
        if "lead management" in problem_lower or "sales" in problem_lower:
            stakeholders.append({"name": "Sales Director", "role": "VP of Sales"})
        
        if "patient" in problem_lower or "healthcare" in industry.lower():
            stakeholders.append({"name": "Compliance Officer", "role": "Compliance Officer"})
        
        if "checkout" in problem_lower or "e-commerce" in problem_lower:
            stakeholders.append({"name": "Marketing Lead", "role": "VP of Marketing"})
        
        if "product" in problem_lower:
            stakeholders.append({"name": "Product Manager", "role": "VP of Product"})
        
        # Ensure we have at least 2 stakeholders
        if len(stakeholders) < 2:
            stakeholders.append({"name": "Project Manager", "role": "Project Manager"})
        
        return stakeholders
    
    def _extract_primary_challenge(self, problem_statement: str) -> str:
        """Extract the primary business challenge from problem statement"""
        problem_lower = problem_statement.lower()
        
        if "lead management" in problem_lower:
            return "Lead Management and Conversion"
        elif "patient record" in problem_lower:
            return "Healthcare Data Management and Compliance"
        elif "checkout" in problem_lower:
            return "E-commerce Conversion Optimization"
        elif "optimization" in problem_lower:
            return "Process Optimization"
        elif "integration" in problem_lower:
            return "System Integration"
        else:
            return "Digital Transformation"
    
    def _classify_project_type(self, problem_statement: str) -> str:
        """Classify the type of project based on problem statement"""
        problem_lower = problem_statement.lower()
        
        if "implement" in problem_lower or "develop" in problem_lower:
            return "Implementation"
        elif "optimize" in problem_lower or "improve" in problem_lower:
            return "Optimization"
        elif "integrate" in problem_lower:
            return "Integration"
        elif "migrate" in problem_lower:
            return "Migration"
        else:
            return "Custom Development"
    
    def _assess_complexity(self, problem_statement: str, tech_stack: str) -> str:
        """Assess project complexity level"""
        complexity_factors = [
            "integration", "compliance", "scale", "multiple", "complex",
            "enterprise", "distributed", "microservices", "real-time"
        ]
        
        text = (problem_statement + " " + tech_stack).lower()
        complexity_score = sum(1 for factor in complexity_factors if factor in text)
        
        if complexity_score >= 4:
            return "High"
        elif complexity_score >= 2:
            return "Medium"
        else:
            return "Low"
    
    def _generate_business_context(self, industry: str, problem_statement: str) -> Dict[str, Any]:
        """Generate business context information"""
        return {
            "industry_trends": self._get_industry_trends(industry),
            "business_drivers": self._extract_business_drivers(problem_statement),
            "success_metrics": self._suggest_success_metrics(problem_statement),
            "risk_factors": self._identify_risk_factors(industry, problem_statement)
        }
    
    def _get_industry_trends(self, industry: str) -> List[str]:
        """Get relevant industry trends"""
        trends = {
            "automotive": ["Digital transformation", "Connected vehicles", "Data analytics"],
            "healthcare": ["Digital health records", "Telemedicine", "AI diagnostics"],
            "retail": ["Omnichannel experience", "Mobile commerce", "Personalization"]
        }
        return trends.get(industry.lower(), ["Digital transformation", "Cloud adoption"])
    
    def _extract_business_drivers(self, problem_statement: str) -> List[str]:
        """Extract business drivers from problem statement"""
        drivers = []
        problem_lower = problem_statement.lower()
        
        if "efficiency" in problem_lower or "optimize" in problem_lower:
            drivers.append("Operational efficiency")
        if "customer" in problem_lower or "user" in problem_lower:
            drivers.append("Customer experience")
        if "cost" in problem_lower or "save" in problem_lower:
            drivers.append("Cost reduction")
        if "growth" in problem_lower or "scale" in problem_lower:
            drivers.append("Business growth")
        
        return drivers if drivers else ["Digital transformation"]
    
    def _suggest_success_metrics(self, problem_statement: str) -> List[str]:
        """Suggest relevant success metrics"""
        problem_lower = problem_statement.lower()
        
        if "lead" in problem_lower:
            return ["Lead conversion rate", "Sales cycle time", "Lead quality score"]
        elif "checkout" in problem_lower:
            return ["Conversion rate", "Cart abandonment rate", "Average order value"]
        elif "patient" in problem_lower:
            return ["Data accuracy", "Compliance score", "User adoption rate"]
        else:
            return ["User adoption rate", "System performance", "ROI"]
    
    def _identify_risk_factors(self, industry: str, problem_statement: str) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        if industry.lower() == "healthcare":
            risks.extend(["Regulatory compliance", "Data security"])
        if "integration" in problem_statement.lower():
            risks.append("System compatibility")
        if "new" in problem_statement.lower() or "implement" in problem_statement.lower():
            risks.append("User adoption")
        
        return risks if risks else ["Technical complexity", "Timeline constraints"]
    
    def _calculate_profile_completeness(self, profile: Dict[str, Any]) -> float:
        """Calculate profile completeness score"""
        required_fields = [
            "name", "industry", "founded", "region", "stakeholders",
            "tech_stack", "primary_challenge"
        ]
        
        completed_fields = sum(1 for field in required_fields if profile.get(field))
        base_score = completed_fields / len(required_fields)
        
        # Bonus for additional context
        bonus = 0
        if profile.get("current_project"):
            bonus += 0.1
        if profile.get("business_context"):
            bonus += 0.1
        if len(profile.get("stakeholders", [])) >= 2:
            bonus += 0.05
        
        return min(base_score + bonus, 1.0)
    
    def _generate_profile_insights(self, profile: Dict[str, Any], industry: str, 
                                 problem_statement: str) -> List[str]:
        """Generate insights about the client profile"""
        insights = []
        
        # Company maturity insight
        founded = profile.get("founded", datetime.now().year)
        age = datetime.now().year - founded
        
        if age < 5:
            insights.append("Young company likely focused on rapid growth and scalability")
        elif age > 20:
            insights.append("Established company with potential legacy system challenges")
        
        # Tech stack insight
        tech_stack = profile.get("tech_stack", [])
        if len(tech_stack) > 3:
            insights.append("Diverse technology stack suggests complex technical requirements")
        
        # Stakeholder insight
        stakeholders = profile.get("stakeholders", [])
        if len(stakeholders) >= 3:
            insights.append("Multiple stakeholders indicate need for comprehensive change management")
        
        # Industry-specific insights
        if industry.lower() == "healthcare":
            insights.append("Healthcare industry requires strict compliance and security measures")
        elif industry.lower() == "retail":
            insights.append("Retail focus suggests emphasis on customer experience and conversion")
        
        return insights