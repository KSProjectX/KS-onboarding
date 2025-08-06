import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from textblob import TextBlob
import json
import re

logger = logging.getLogger(__name__)

class MeetingsAgent:
    """Meetings Agent for analyzing meeting transcripts and extracting insights with sentiment analysis"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.name = "Meetings Agent"
    
    async def analyze_meeting(self, client_name: str, transcript: str) -> Dict[str, Any]:
        """Analyze meeting transcript and extract insights with sentiment analysis"""
        start_time = datetime.now()
        
        try:
            # Perform sentiment analysis
            sentiment_result = self._analyze_sentiment(transcript)
            
            # Extract action items
            action_items = self._extract_action_items(transcript)
            
            # Calculate engagement metrics
            engagement_metrics = self._calculate_engagement_metrics(transcript)
            
            # Extract key topics and themes
            topics = self._extract_topics(transcript)
            
            # Identify participants and roles
            participants = self._identify_participants(transcript)
            
            # Generate meeting summary
            summary = self._generate_meeting_summary(transcript, sentiment_result, action_items)
            
            result = {
                "status": "success",
                "agent": self.name,
                "client_name": client_name,
                "meeting_analysis": {
                    "sentiment": sentiment_result,
                    "action_items": action_items,
                    "engagement_metrics": engagement_metrics,
                    "topics": topics,
                    "participants": participants,
                    "summary": summary,
                    "transcript_length": len(transcript),
                    "analysis_timestamp": datetime.now().isoformat()
                }
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            result["execution_time"] = execution_time
            
            logger.info(f"{self.name} completed analysis for {client_name} in {execution_time:.2f} seconds")
            return result
            
        except Exception as e:
            logger.error(f"Error in {self.name}: {e}")
            return {
                "status": "error",
                "message": f"Meeting analysis failed: {str(e)}",
                "agent": self.name
            }
    
    def _analyze_sentiment(self, transcript: str) -> Dict[str, Any]:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(transcript)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Categorize sentiment
            if polarity > 0.1:
                category = "positive"
                description = "Positive sentiment detected"
            elif polarity < -0.1:
                category = "negative"
                description = "Negative sentiment detected"
            else:
                category = "neutral"
                description = "Neutral sentiment detected"
            
            # Analyze sentence-level sentiment for more detailed insights
            sentences = blob.sentences
            sentence_sentiments = []
            
            for sentence in sentences[:5]:  # Analyze first 5 sentences
                sent_polarity = sentence.sentiment.polarity
                sentence_sentiments.append({
                    "text": str(sentence)[:100] + "..." if len(str(sentence)) > 100 else str(sentence),
                    "polarity": round(sent_polarity, 3)
                })
            
            return {
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "category": category,
                "description": description,
                "confidence": abs(polarity),
                "sentence_analysis": sentence_sentiments
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return {
                "polarity": 0.0,
                "subjectivity": 0.0,
                "category": "neutral",
                "description": "Sentiment analysis failed",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _extract_action_items(self, transcript: str) -> List[Dict[str, Any]]:
        """Extract action items from meeting transcript"""
        action_items = []
        
        # Common action item patterns
        action_patterns = [
            r"action item[s]?:?\s*([^.!?]+)",
            r"todo[s]?:?\s*([^.!?]+)",
            r"follow[- ]?up:?\s*([^.!?]+)",
            r"next step[s]?:?\s*([^.!?]+)",
            r"need[s]? to\s+([^.!?]+)",
            r"should\s+([^.!?]+)",
            r"will\s+([^.!?]+)",
            r"must\s+([^.!?]+)"
        ]
        
        transcript_lower = transcript.lower()
        
        for pattern in action_patterns:
            matches = re.findall(pattern, transcript_lower, re.IGNORECASE)
            for match in matches:
                if len(match.strip()) > 10:  # Filter out very short matches
                    action_items.append({
                        "item": match.strip().capitalize(),
                        "priority": self._assess_action_priority(match),
                        "type": self._classify_action_type(match)
                    })
        
        # Remove duplicates and limit to top 5
        unique_items = []
        seen_items = set()
        
        for item in action_items:
            item_text = item["item"].lower()
            if item_text not in seen_items:
                unique_items.append(item)
                seen_items.add(item_text)
        
        return unique_items[:5]
    
    def _assess_action_priority(self, action_text: str) -> str:
        """Assess priority level of action item"""
        high_priority_words = ["urgent", "asap", "immediately", "critical", "must"]
        medium_priority_words = ["should", "need", "important", "soon"]
        
        action_lower = action_text.lower()
        
        if any(word in action_lower for word in high_priority_words):
            return "high"
        elif any(word in action_lower for word in medium_priority_words):
            return "medium"
        else:
            return "low"
    
    def _classify_action_type(self, action_text: str) -> str:
        """Classify the type of action item"""
        action_lower = action_text.lower()
        
        if any(word in action_lower for word in ["plan", "design", "architect"]):
            return "planning"
        elif any(word in action_lower for word in ["develop", "implement", "build", "code"]):
            return "development"
        elif any(word in action_lower for word in ["test", "verify", "validate"]):
            return "testing"
        elif any(word in action_lower for word in ["review", "approve", "check"]):
            return "review"
        elif any(word in action_lower for word in ["meet", "discuss", "call"]):
            return "communication"
        else:
            return "general"
    
    def _calculate_engagement_metrics(self, transcript: str) -> Dict[str, Any]:
        """Calculate engagement metrics from transcript"""
        # Extract engagement percentage if mentioned
        engagement_match = re.search(r"engagement[:]?\s*(\d+)%?", transcript.lower())
        engagement_percentage = int(engagement_match.group(1)) if engagement_match else None
        
        # Calculate basic metrics
        word_count = len(transcript.split())
        sentence_count = len(re.split(r'[.!?]+', transcript))
        
        # Estimate speaking time (assuming 150 words per minute)
        estimated_duration = max(word_count / 150, 1)  # At least 1 minute
        
        # Count questions (indicator of engagement)
        question_count = transcript.count('?')
        
        # Count exclamations (indicator of enthusiasm)
        exclamation_count = transcript.count('!')
        
        # Calculate engagement score based on various factors
        engagement_score = self._calculate_engagement_score(
            word_count, question_count, exclamation_count, engagement_percentage
        )
        
        return {
            "engagement_percentage": engagement_percentage,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "estimated_duration_minutes": round(estimated_duration, 1),
            "question_count": question_count,
            "exclamation_count": exclamation_count,
            "engagement_score": engagement_score,
            "participation_level": self._assess_participation_level(engagement_score)
        }
    
    def _calculate_engagement_score(self, word_count: int, question_count: int, 
                                  exclamation_count: int, engagement_percentage: Optional[int]) -> float:
        """Calculate overall engagement score"""
        if engagement_percentage is not None:
            return engagement_percentage / 100.0
        
        # Calculate based on content analysis
        base_score = min(word_count / 200, 1.0)  # Normalize by expected word count
        question_bonus = min(question_count * 0.1, 0.3)  # Up to 30% bonus for questions
        exclamation_bonus = min(exclamation_count * 0.05, 0.2)  # Up to 20% bonus for exclamations
        
        total_score = base_score + question_bonus + exclamation_bonus
        return min(total_score, 1.0)
    
    def _assess_participation_level(self, engagement_score: float) -> str:
        """Assess participation level based on engagement score"""
        if engagement_score >= 0.8:
            return "high"
        elif engagement_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _extract_topics(self, transcript: str) -> List[str]:
        """Extract key topics and themes from transcript"""
        # Common business/technical topics
        topic_keywords = {
            "Technology": ["system", "platform", "software", "application", "tech", "development"],
            "Project Management": ["timeline", "deadline", "milestone", "project", "scope", "requirements"],
            "Business": ["revenue", "cost", "roi", "business", "strategy", "market"],
            "User Experience": ["user", "customer", "experience", "interface", "usability"],
            "Security": ["security", "compliance", "privacy", "encryption", "audit"],
            "Performance": ["performance", "speed", "optimization", "efficiency", "scalability"]
        }
        
        transcript_lower = transcript.lower()
        detected_topics = []
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in transcript_lower for keyword in keywords):
                detected_topics.append(topic)
        
        return detected_topics
    
    def _identify_participants(self, transcript: str) -> List[Dict[str, str]]:
        """Identify participants and their roles from transcript"""
        participants = []
        
        # Common role patterns
        role_patterns = {
            "VP of Product": ["vp of product", "vice president of product", "product vp"],
            "CTO": ["cto", "chief technology officer", "tech lead"],
            "Marketing Lead": ["marketing lead", "marketing director", "marketing manager"],
            "Project Manager": ["project manager", "pm", "project lead"],
            "Developer": ["developer", "engineer", "programmer"],
            "Designer": ["designer", "ux", "ui"]
        }
        
        transcript_lower = transcript.lower()
        
        for role, patterns in role_patterns.items():
            if any(pattern in transcript_lower for pattern in patterns):
                participants.append({
                    "role": role,
                    "mentioned": True
                })
        
        return participants
    
    def _generate_meeting_summary(self, transcript: str, sentiment_result: Dict, 
                                action_items: List[Dict]) -> str:
        """Generate a concise meeting summary"""
        # Extract key phrases
        key_phrases = self._extract_key_phrases(transcript)
        
        summary_parts = []
        
        # Add sentiment overview
        sentiment_desc = sentiment_result.get("description", "Neutral sentiment")
        summary_parts.append(f"Meeting sentiment: {sentiment_desc}")
        
        # Add key discussion points
        if key_phrases:
            summary_parts.append(f"Key topics discussed: {', '.join(key_phrases[:3])}")
        
        # Add action items summary
        if action_items:
            action_count = len(action_items)
            summary_parts.append(f"Generated {action_count} action item{'s' if action_count != 1 else ''}")
        
        return ". ".join(summary_parts) + "."
    
    def _extract_key_phrases(self, transcript: str) -> List[str]:
        """Extract key phrases from transcript"""
        # Simple keyword extraction
        important_words = [
            "implementation", "development", "optimization", "integration",
            "requirements", "timeline", "budget", "resources", "testing",
            "deployment", "maintenance", "support", "training", "documentation"
        ]
        
        transcript_lower = transcript.lower()
        found_phrases = []
        
        for word in important_words:
            if word in transcript_lower:
                found_phrases.append(word.capitalize())
        
        return found_phrases[:5]  # Return top 5
    
    def get_sentiment_distribution(self, client_name: Optional[str] = None) -> Dict[str, Any]:
        """Get sentiment distribution for visualization"""
        try:
            meeting_insights = self.db_manager.get_meeting_insights()
            
            if client_name:
                meeting_insights = [m for m in meeting_insights if m["client_name"] == client_name]
            
            if not meeting_insights:
                return {"positive": 0, "neutral": 0, "negative": 0}
            
            sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
            
            for meeting in meeting_insights:
                category = meeting.get("sentiment_category", "neutral")
                sentiment_counts[category] = sentiment_counts.get(category, 0) + 1
            
            total = sum(sentiment_counts.values())
            
            if total == 0:
                return {"positive": 0, "neutral": 0, "negative": 0}
            
            return {
                "positive": round((sentiment_counts["positive"] / total) * 100, 1),
                "neutral": round((sentiment_counts["neutral"] / total) * 100, 1),
                "negative": round((sentiment_counts["negative"] / total) * 100, 1)
            }
            
        except Exception as e:
            logger.error(f"Error calculating sentiment distribution: {e}")
            return {"positive": 0, "neutral": 0, "negative": 0}