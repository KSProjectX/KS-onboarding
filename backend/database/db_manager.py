import sqlite3
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from textblob import TextBlob

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = None
    
    def get_connection(self):
        """Get database connection"""
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def check_connection(self) -> bool:
        """Check if database connection is healthy"""
        try:
            conn = self.get_connection()
            conn.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    def initialize_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create use_cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS use_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                industry TEXT NOT NULL,
                problem_statement TEXT NOT NULL,
                tech_stack TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                profile_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create insights table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                insight_type TEXT NOT NULL,
                content TEXT NOT NULL,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create meetings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS meetings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_name TEXT NOT NULL,
                transcript TEXT NOT NULL,
                action_items TEXT,
                engagement_metrics TEXT,
                sentiment_score REAL,
                sentiment_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create validations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS validations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                output_id INTEGER NOT NULL,
                relevant BOOLEAN NOT NULL,
                feedback TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create setup_sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS setup_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                setup_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        logger.info("Database initialized successfully")
    
    def analyze_sentiment(self, text: str) -> tuple:
        """Analyze sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            category = "positive"
        elif polarity < -0.1:
            category = "negative"
        else:
            category = "neutral"
        
        return polarity, category
    
    def load_use_cases(self):
        """Load predefined use cases into database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if use cases already exist
        cursor.execute("SELECT COUNT(*) FROM use_cases")
        if cursor.fetchone()[0] > 0:
            logger.info("Use cases already loaded")
            return
        
        use_cases = [
            {
                "client_name": "GT Automotive",
                "industry": "Automotive",
                "problem_statement": "Implement a lead management process using Salesforce",
                "tech_stack": "Salesforce, Java",
                "transcript": "Discussion on lead management. VP of Product emphasized clear KPIs. Action item: Clarify MVP scope by next meeting. Engagement: 70%.",
                "profile": {
                    "name": "GT Automotive",
                    "industry": "Automotive",
                    "founded": 1970,
                    "region": "USA, Latin America",
                    "stakeholders": [
                        {"name": "John Doe", "role": "VP of Product"},
                        {"name": "Jane Smith", "role": "CTO"}
                    ]
                },
                "domain_knowledge": "Best practices: Define KPIs early, use Salesforce Sales Cloud for lead tracking, ensure clear customer journey mapping.",
                "recommendations": "Define KPIs early to avoid delays."
            },
            {
                "client_name": "MediCare Solutions",
                "industry": "Healthcare",
                "problem_statement": "Develop a patient record system with HIPAA compliance",
                "tech_stack": "Python, AWS",
                "transcript": "Discussion on patient record system. CTO requested data encryption. Action item: Finalize encryption plan. Engagement: 80%.",
                "profile": {
                    "name": "MediCare Solutions",
                    "industry": "Healthcare",
                    "founded": 2010,
                    "region": "USA",
                    "stakeholders": [
                        {"name": "Alice Brown", "role": "CTO"},
                        {"name": "Bob Wilson", "role": "Compliance Officer"}
                    ]
                },
                "domain_knowledge": "Best practices: Ensure HIPAA compliance, use encrypted databases, conduct regular audits.",
                "recommendations": "Use AWS RDS for HIPAA-compliant storage."
            },
            {
                "client_name": "ShopTrend Inc.",
                "industry": "Retail",
                "problem_statement": "Optimize e-commerce platform checkout process",
                "tech_stack": "Shopify, Node.js",
                "transcript": "Discussion on checkout optimization. Marketing lead suggested one-click checkout. Action item: Test checkout flow. Engagement: 65%.",
                "profile": {
                    "name": "ShopTrend Inc.",
                    "industry": "Retail",
                    "founded": 2015,
                    "region": "Global",
                    "stakeholders": [
                        {"name": "Emma Davis", "role": "Marketing Lead"},
                        {"name": "Tom Clark", "role": "CTO"}
                    ]
                },
                "domain_knowledge": "Best practices: Simplify checkout forms, implement one-click checkout, optimize for mobile.",
                "recommendations": "Implement one-click checkout to improve conversion rates."
            }
        ]
        
        for case in use_cases:
            # Insert use case
            cursor.execute("""
                INSERT INTO use_cases (client_name, industry, problem_statement, tech_stack)
                VALUES (?, ?, ?, ?)
            """, (case["client_name"], case["industry"], case["problem_statement"], case["tech_stack"]))
            
            # Insert profile
            cursor.execute("""
                INSERT INTO profiles (client_name, profile_data)
                VALUES (?, ?)
            """, (case["client_name"], json.dumps(case["profile"])))
            
            # Insert domain knowledge
            cursor.execute("""
                INSERT INTO insights (client_name, insight_type, content, tags)
                VALUES (?, ?, ?, ?)
            """, (case["client_name"], "domain_knowledge", case["domain_knowledge"], "Best Practices"))
            
            # Insert recommendations
            cursor.execute("""
                INSERT INTO insights (client_name, insight_type, content, tags)
                VALUES (?, ?, ?, ?)
            """, (case["client_name"], "recommendations", case["recommendations"], "Recommendations"))
            
            # Analyze sentiment and insert meeting data
            sentiment_score, sentiment_category = self.analyze_sentiment(case["transcript"])
            
            cursor.execute("""
                INSERT INTO meetings (client_name, transcript, action_items, engagement_metrics, sentiment_score, sentiment_category)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                case["client_name"],
                case["transcript"],
                json.dumps(["Clarify MVP scope", "Finalize encryption plan", "Test checkout flow"][use_cases.index(case)]),
                json.dumps({"engagement": [70, 80, 65][use_cases.index(case)]}),
                sentiment_score,
                sentiment_category
            ))
        
        conn.commit()
        logger.info(f"Loaded {len(use_cases)} use cases successfully")
    
    def get_use_cases(self) -> List[Dict]:
        """Get all use cases"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM use_cases")
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_client_profiles(self) -> List[Dict]:
        """Get all client profiles"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM profiles")
        rows = cursor.fetchall()
        
        profiles = []
        for row in rows:
            profile = dict(row)
            profile["profile_data"] = json.loads(profile["profile_data"])
            profiles.append(profile)
        
        return profiles
    
    def save_client_profile(self, client_name: str, profile_data: Dict[str, Any]):
        """Save or update client profile in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if profile already exists
            cursor.execute("SELECT id FROM profiles WHERE client_name = ?", (client_name,))
            existing = cursor.fetchone()
            
            profile_json = json.dumps(profile_data)
            
            if existing:
                # Update existing profile
                cursor.execute(
                    "UPDATE profiles SET profile_data = ?, updated_at = CURRENT_TIMESTAMP WHERE client_name = ?",
                    (profile_json, client_name)
                )
                logger.info(f"Updated existing profile for {client_name}")
            else:
                # Insert new profile
                cursor.execute(
                    "INSERT INTO profiles (client_name, profile_data) VALUES (?, ?)",
                    (client_name, profile_json)
                )
                logger.info(f"Created new profile for {client_name}")
            
            conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving client profile for {client_name}: {e}")
            conn.rollback()
            raise
    
    def get_domain_knowledge(self) -> List[Dict]:
        """Get domain knowledge insights"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM insights WHERE insight_type = 'domain_knowledge'
        """)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_meeting_insights(self) -> List[Dict]:
        """Get meeting insights with sentiment data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM meetings")
        rows = cursor.fetchall()
        
        insights = []
        for row in rows:
            insight = dict(row)
            insight["action_items"] = json.loads(insight["action_items"]) if insight["action_items"] else []
            insight["engagement_metrics"] = json.loads(insight["engagement_metrics"]) if insight["engagement_metrics"] else {}
            insights.append(insight)
        
        return insights
    
    def get_recommendations(self) -> List[Dict]:
        """Get recommendations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM insights WHERE insight_type = 'recommendations'
        """)
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_sentiment_data(self) -> Dict:
        """Get sentiment analysis data for visualization"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT sentiment_category, COUNT(*) as count
            FROM meetings
            GROUP BY sentiment_category
        """)
        rows = cursor.fetchall()
        
        sentiment_counts = {row["sentiment_category"]: row["count"] for row in rows}
        total = sum(sentiment_counts.values())
        
        if total == 0:
            return {"positive": 0, "neutral": 0, "negative": 0}
        
        return {
            "positive": round((sentiment_counts.get("positive", 0) / total) * 100, 1),
            "neutral": round((sentiment_counts.get("neutral", 0) / total) * 100, 1),
            "negative": round((sentiment_counts.get("negative", 0) / total) * 100, 1)
        }
    
    def search_knowledge_base(self, query: str, tags: Optional[List[str]] = None) -> List[Dict]:
        """Search knowledge base by query and tags"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Search in insights table
        sql = "SELECT * FROM insights WHERE content LIKE ?"
        params = [f"%{query}%"]
        
        if tags:
            tag_conditions = " OR ".join(["tags LIKE ?" for _ in tags])
            sql += f" AND ({tag_conditions})"
            params.extend([f"%{tag}%" for tag in tags])
        
        cursor.execute(sql, params)
        results = [dict(row) for row in cursor.fetchall()]
        
        # Also search in meetings
        sql = "SELECT * FROM meetings WHERE transcript LIKE ?"
        params = [f"%{query}%"]
        
        cursor.execute(sql, params)
        meeting_results = [dict(row) for row in cursor.fetchall()]
        
        return {
            "insights": results,
            "meetings": meeting_results
        }
    
    def store_validation(self, output_id: int, relevant: bool, feedback: Optional[str] = None):
        """Store user validation feedback"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO validations (output_id, relevant, feedback)
            VALUES (?, ?, ?)
        """, (output_id, relevant, feedback))
        
        conn.commit()
        logger.info(f"Validation stored for output {output_id}")