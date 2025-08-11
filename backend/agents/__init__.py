"""K-Square Programme Onboarding Agents Package

This package contains all the specialized agents for the K-Square Programme Onboarding system:
- ConversationalSetupAgent: Handles conversational AI for data input and validation
- DomainKnowledgeAgent: Processes industry-specific insights and best practices
- ClientProfileAgent: Builds detailed client profiles and generates insights
- ActionableInsightsAgent: Synthesizes outputs from other agents to generate recommendations
- MeetingsAgent: Analyzes meeting transcripts and extracts insights
"""

from agents.conversational_setup import ConversationalSetupAgent
from agents.domain_knowledge import DomainKnowledgeAgent
from agents.client_profile import ClientProfileAgent
from agents.actionable_insights import ActionableInsightsAgent
from agents.meetings import MeetingsAgent

__all__ = [
    'ConversationalSetupAgent',
    'DomainKnowledgeAgent',
    'ClientProfileAgent',
    'ActionableInsightsAgent',
    'MeetingsAgent'
]

__version__ = '1.0.0'
__author__ = 'K-Square Programme Onboarding Team'