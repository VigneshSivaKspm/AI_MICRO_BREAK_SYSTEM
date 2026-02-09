"""
Groq AI Integration Module (Enhanced)
Comprehensive AI-powered analysis for fatigue detection, recommendations, and personalization
"""

import logging
import json
from typing import Dict, Optional, List
from datetime import datetime
from groq import Groq
from config.config import ML_CONFIG

logger = logging.getLogger(__name__)


class GroqAIIntegration:
    """Comprehensive Groq AI integration for intelligent break management"""
    
    def __init__(self):
        self.api_key = ML_CONFIG.get('groq_api_key', '')
        self.model = ML_CONFIG.get('groq_model', 'llama-3.1-8b-instant')
        self.client = None
        self.conversation_history = {}
        self._initialize_client()
    
    def _initialize_client(self) -> bool:
        """Initialize Groq client"""
        try:
            if not self.api_key:
                logger.warning("Groq API key not configured. Please set GROQ_API_KEY environment variable")
                return False
            
            self.client = Groq(api_key=self.api_key)
            logger.info("[OK] Groq AI client initialized successfully")
            return True
        except Exception as e:
            logger.error(f"[ERROR] Failed to initialize Groq AI client: {e}")
            return False
    
    def analyze_activity_and_fatigue(self, user_id: int, activity_data: Dict, fatigue_metrics: Dict) -> Dict:
        """
        Comprehensive analysis of user activity and fatigue using Groq AI
        
        Args:
            user_id: User identifier
            activity_data: User's recent activity metrics
            fatigue_metrics: Detected fatigue indicators
            
        Returns:
            Complete analysis with recommendations
        """
        try:
            if not self.client:
                return self._fallback_activity_analysis(activity_data, fatigue_metrics)
            
            # Build context from activity and fatigue data
            context = self._build_analysis_context(activity_data, fatigue_metrics)
            
            prompt = f"""You are an AI wellness expert analyzing user work patterns and fatigue. Provide intelligent insights.

CURRENT USER METRICS:
{context}

ANALYZE and provide:
1. FATIGUE_LEVEL: (Low/Moderate/High/Critical) - based on all metrics
2. BREAK_URGENCY: (Immediate/Soon/Optional/None) - when should user take a break
3. BREAK_DURATION: Minutes (3-10) - appropriate break length
4. BREAK_TYPE: (Micro/Standard/Long) - which type of break
5. PRIMARY_FACTORS: List the top 2 factors causing fatigue
6. RECOMMENDATIONS: 1-2 actionable suggestions for user

Format your response as JSON for easy parsing."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            result = self._parse_json_response(analysis_text)
            
            return {
                'status': 'success',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                **result,
                'raw_analysis': analysis_text
            }
        except Exception as e:
            logger.error(f"Groq activity analysis failed: {e}")
            return self._fallback_activity_analysis(activity_data, fatigue_metrics)
    
    def get_adaptive_break_schedule(self, user_id: int, work_history: List[Dict], user_preferences: Dict) -> Dict:
        """
        Generate adaptive break schedule based on AI analysis
        
        Args:
            user_id: User identifier
            work_history: Recent work session data
            user_preferences: User's break preferences
            
        Returns:
            Personalized break schedule
        """
        try:
            if not self.client:
                return self._fallback_break_schedule()
            
            history_summary = self._summarize_work_history(work_history)
            
            prompt = f"""You are an AI productivity coach. Create an adaptive break schedule.

USER WORK PATTERNS:
{history_summary}

USER PREFERENCES:
- Preferred break types: {', '.join(user_preferences.get('preferred_types', ['general']))}
- Max break duration: {user_preferences.get('max_duration', 10)} minutes
- Preferred break times: {user_preferences.get('preferred_times', 'flexible')}
- Activity level: {user_preferences.get('activity_level', 'moderate')}

CREATE an adaptive schedule that:
1. Learns from user's work patterns
2. Suggests optimal break intervals (in minutes)
3. Recommends break types based on patterns
4. Accounts for productivity peaks and dips
5. Personalizes to user preferences

Provide JSON with:
- NEXT_BREAK_IN: minutes until next recommended break
- OPTIMAL_INTERVALS: list of recommended intervals for next 8 hours
- BREAK_TYPES: [type1, type2, ...] in suggested order
- REASONING: brief explanation of schedule
- FLEXIBILITY_SCORE: how much user can adjust (0-1)"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=500
            )
            
            schedule_text = response.choices[0].message.content
            result = self._parse_json_response(schedule_text)
            
            return {
                'status': 'success',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                **result,
                'raw_schedule': schedule_text
            }
        except Exception as e:
            logger.error(f"Groq schedule generation failed: {e}")
            return self._fallback_break_schedule()
    
    def generate_personalized_recommendation(self, user_id: int, current_state: Dict, history: List[str]) -> Dict:
        """
        Generate highly personalized break activity recommendation
        
        Args:
            user_id: User identifier
            current_state: Current user state (fatigue, activity, etc.)
            history: Recent break activity history
            
        Returns:
            Personalized activity recommendation
        """
        try:
            if not self.client:
                return self._fallback_recommendation(current_state)
            
            recent_activities = ", ".join(history[-5:]) if history else "None yet"
            
            prompt = f"""You are a wellness expert recommending the perfect break activity.

CURRENT STATE:
- Fatigue level: {current_state.get('fatigue_level', 'medium')}
- Time available: {current_state.get('available_time', 5)} minutes
- Energy level: {current_state.get('energy_level', 'normal')}
- Previous activities (today): {recent_activities}
- Location: {current_state.get('location', 'office')}
- Preferences: {', '.join(current_state.get('preferences', ['general']))}

RECOMMEND an activity that:
1. Hasn't been done recently (avoid repetition)
2. Fits in available time
3. Matches current fatigue and energy levels
4. Aligns with user preferences
5. Provides appropriate relief for current state

Provide JSON with:
- ACTIVITY: Specific activity name
- REASON: Why this activity now
- DURATION_MIN: Minimum minutes
- DURATION_MAX: Maximum minutes  
- BENEFITS: Main health benefits
- STEPS: Simple numbered steps (2-4 steps)
- INTENSITY: (Low/Medium/High)
- EFFECTIVENESS_SCORE: 0-100 for this user's state"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=600
            )
            
            rec_text = response.choices[0].message.content
            result = self._parse_json_response(rec_text)
            
            return {
                'status': 'success',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                **result,
                'raw_recommendation': rec_text
            }
        except Exception as e:
            logger.error(f"Groq recommendation failed: {e}")
            return self._fallback_recommendation(current_state)
    
    def analyze_compliance_and_adapt(self, user_id: int, compliance_data: Dict, performance_data: Dict) -> Dict:
        """
        Analyze user compliance and suggest adaptations
        
        Args:
            user_id: User identifier
            compliance_data: Break compliance metrics
            performance_data: Work performance metrics
            
        Returns:
            Compliance analysis and adaptation suggestions
        """
        try:
            if not self.client:
                return self._fallback_compliance_analysis(compliance_data)
            
            prompt = f"""You are an AI wellness analyst. Analyze break compliance and suggest adaptations.

COMPLIANCE METRICS:
- Break taken: {compliance_data.get('breaks_taken', 0)} of {compliance_data.get('breaks_recommended', 0)}
- Compliance rate: {compliance_data.get('compliance_rate', 0):.0%}
- Average break duration: {compliance_data.get('avg_break_duration', 0)} minutes
- Breaks skipped (reason): {compliance_data.get('skip_reasons', 'unknown')}

PERFORMANCE METRICS:
- Productivity score: {performance_data.get('productivity', 0)}/100
- Focus level: {performance_data.get('focus', 0)}/100
- Error rate: {performance_data.get('error_rate', 0):.1%}
- Output quality: {performance_data.get('quality', 0)}/100

ANALYZE and provide JSON with:
- COMPLIANCE_ASSESSMENT: Current compliance quality
- IMPACT_ON_PERFORMANCE: How breaks affect productivity
- ADAPTATION_NEEDED: (Yes/No) - is current schedule working?
- ADJUSTMENTS: Specific changes to try
- MOTIVATION: Why these changes matter
- PREDICTED_IMPROVEMENT: Expected performance boost if adapted
- ACTION_PLAN: 3-5 specific actions user can take"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=600
            )
            
            analysis_text = response.choices[0].message.content
            result = self._parse_json_response(analysis_text)
            
            return {
                'status': 'success',
                'user_id': user_id,
                'timestamp': datetime.now().isoformat(),
                **result,
                'raw_analysis': analysis_text
            }
        except Exception as e:
            logger.error(f"Groq compliance analysis failed: {e}")
            return self._fallback_compliance_analysis(compliance_data)
    
    # ==================== HELPER METHODS ====================
    
    def _build_analysis_context(self, activity_data: Dict, fatigue_metrics: Dict) -> str:
        """Build context string for AI analysis"""
        context_lines = [
            "ACTIVITY DATA:",
            f"  - Mouse clicks (last hour): {activity_data.get('mouse_clicks', 0)}",
            f"  - Keyboard presses (last hour): {activity_data.get('keyboard_presses', 0)}",
            f"  - Idle time: {activity_data.get('idle_time', 0)} minutes",
            f"  - Activity level: {activity_data.get('activity_level', 0):.0%}",
            f"  - Work duration (current session): {activity_data.get('session_duration', 0)} minutes",
            "",
            "FATIGUE INDICATORS:",
            f"  - Fatigue score: {fatigue_metrics.get('fatigue_score', 0):.2f} (0-1 scale)",
            f"  - Eye strain: {fatigue_metrics.get('eye_strain', 'unknown')}",
            f"  - Posture quality: {fatigue_metrics.get('posture_quality', 'unknown')}",
            f"  - Blink rate: {fatigue_metrics.get('blink_rate', 0):.1f} blinks/min (normal: 15-20)",
            f"  - Facial expression: {fatigue_metrics.get('facial_expression', 'neutral')}",
            f"  - Fatigue trend: {fatigue_metrics.get('trend', 'stable')}",
        ]
        return "\n".join(context_lines)
    
    def _summarize_work_history(self, work_history: List[Dict]) -> str:
        """Summarize work history for scheduling"""
        if not work_history:
            return "No history available"
        
        summary_lines = []
        for i, session in enumerate(work_history[-7:], 1):  # Last 7 sessions
            summary_lines.append(f"Session {i}: {session.get('duration', 0)}min @ {session.get('hour', '?')}:00, "
                               f"fatigue={session.get('end_fatigue', 0):.1f}, "
                               f"productivity={session.get('productivity', 0):.0%}")
        
        return "\n".join(summary_lines)
    
    def _parse_json_response(self, response_text: str) -> Dict:
        """Parse JSON response from Groq"""
        try:
            # Try to extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response, attempting line-by-line parsing")
        
        # Fallback: parse key-value pairs
        result = {}
        for line in response_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                result[key.strip().upper()] = value.strip()
        
        return result
    
    # ==================== FALLBACK METHODS ====================
    
    def _fallback_activity_analysis(self, activity_data: Dict, fatigue_metrics: Dict) -> Dict:
        """Fallback analysis when Groq is unavailable"""
        fatigue_score = fatigue_metrics.get('fatigue_score', 0.5)
        activity_level = activity_data.get('activity_level', 0.5)
        
        if fatigue_score > 0.75:
            level = "Critical"
            urgency = "Immediate"
        elif fatigue_score > 0.6:
            level = "High"
            urgency = "Soon"
        elif fatigue_score > 0.4:
            level = "Moderate"
            urgency = "Optional"
        else:
            level = "Low"
            urgency = "None"
        
        duration = 10 if fatigue_score > 0.7 else 5
        break_type = "Long" if fatigue_score > 0.75 else "Micro"
        
        return {
            'status': 'fallback',
            'FATIGUE_LEVEL': level,
            'BREAK_URGENCY': urgency,
            'BREAK_DURATION': duration,
            'BREAK_TYPE': break_type,
            'PRIMARY_FACTORS': ['Screen time', 'Low activity'],
            'RECOMMENDATIONS': ['Take a break soon', 'Move around']
        }
    
    def _fallback_break_schedule(self) -> Dict:
        """Fallback break schedule"""
        return {
            'status': 'fallback',
            'NEXT_BREAK_IN': 20,
            'OPTIMAL_INTERVALS': [20, 20, 25, 30],
            'BREAK_TYPES': ['Micro', 'Standard', 'Micro'],
            'FLEXIBILITY_SCORE': 0.7
        }
    
    def _fallback_recommendation(self, current_state: Dict) -> Dict:
        """Fallback recommendation"""
        recommendations = [
            {
                'ACTIVITY': '20-20-20 Eye Exercise',
                'REASON': 'Reduces eye strain',
                'DURATION_MIN': 1,
                'DURATION_MAX': 2,
                'STEPS': ['Look 20 feet away', 'Focus for 20 seconds']
            },
            {
                'ACTIVITY': 'Neck Stretches',
                'REASON': 'Relieves tension',
                'DURATION_MIN': 2,
                'DURATION_MAX': 3,
                'STEPS': ['Slow neck rolls', '10 rolls each direction']
            },
            {
                'ACTIVITY': 'Short Walk',
                'REASON': 'Improves circulation',
                'DURATION_MIN': 3,
                'DURATION_MAX': 5,
                'STEPS': ['Stand up', 'Walk around']
            }
        ]
        
        return {'status': 'fallback', **recommendations[0]}
    
    def _fallback_compliance_analysis(self, compliance_data: Dict) -> Dict:
        """Fallback compliance analysis"""
        compliance_rate = compliance_data.get('compliance_rate', 0.5)
        
        return {
            'status': 'fallback',
            'COMPLIANCE_ASSESSMENT': 'Good' if compliance_rate > 0.7 else 'Needs improvement',
            'ADAPTATION_NEEDED': 'No' if compliance_rate > 0.7 else 'Yes',
            'ADJUSTMENTS': ['Shorter break intervals', 'More flexible timing'],
            'ACTION_PLAN': ['Track break patterns', 'Adjust schedule based on work']
        }


# Global instance
groq_ai = None


def get_groq_ai() -> GroqAIIntegration:
    """Get or create Groq AI integration instance"""
    global groq_ai
    if groq_ai is None:
        groq_ai = GroqAIIntegration()
    return groq_ai
