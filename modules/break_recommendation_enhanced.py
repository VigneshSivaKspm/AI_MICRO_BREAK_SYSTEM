"""
Module 4: AI-Powered Break Recommendation Module (Enhanced)
Generates highly personalized break activities using Groq AI
"""

import logging
import random
from datetime import datetime
from typing import List, Dict, Optional
from config.config import RECOMMENDATION_CONFIG, ML_CONFIG
from modules.groq_ai_integration import get_groq_ai

logger = logging.getLogger(__name__)


class BreakRecommender:
    """Recommends personalized break activities using AI"""
    
    def __init__(self):
        self.use_ai = ML_CONFIG.get('enable_ai_recommendations', True)
        self.groq_ai = get_groq_ai() if self.use_ai else None
        self.user_preferences = {}
        self.recommendation_history = []
        self.max_history = 20
        self.rotation_strategy = RECOMMENDATION_CONFIG.get('rotation_strategy', 'weighted_random')
    
    def get_recommendation(self, user_id: int, current_state: Dict) -> Dict:
        """
        Get AI-powered personalized break recommendation
        
        Args:
            user_id: User identifier
            current_state: Current user state (fatigue, time available, etc.)
            
        Returns:
            Personalized break recommendation
        """
        try:
            # Get recent history to avoid repetition
            recent_activities = [r['activity'] for r in self.recommendation_history[-5:]]
            
            # Use Groq AI for recommendation
            if self.use_ai and self.groq_ai and self.groq_ai.client:
                logger.info(f"Generating AI-powered recommendation for user {user_id}...")
                
                recommendation = self.groq_ai.generate_personalized_recommendation(
                    user_id=user_id,
                    current_state=current_state,
                    history=recent_activities
                )
                
                if recommendation.get('status') == 'success':
                    # Add to history
                    self.recommendation_history.append({
                        'timestamp': datetime.now().isoformat(),
                        'activity': recommendation.get('ACTIVITY', 'Unknown'),
                        'user_id': user_id
                    })
                    if len(self.recommendation_history) > self.max_history:
                        self.recommendation_history.pop(0)
                    
                    return {
                        'status': 'success',
                        'user_id': user_id,
                        'activity': recommendation.get('ACTIVITY', 'Take a break'),
                        'reason': recommendation.get('REASON', ''),
                        'duration_min': recommendation.get('DURATION_MIN', 3),
                        'duration_max': recommendation.get('DURATION_MAX', 5),
                        'benefits': recommendation.get('BENEFITS', ''),
                        'steps': recommendation.get('STEPS', ''),
                        'intensity': recommendation.get('INTENSITY', 'Low'),
                        'effectiveness': recommendation.get('EFFECTIVENESS_SCORE', 75),
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Fallback to standard recommendations if AI unavailable
            logger.info("Using fallback recommendation system...")
            return self._get_fallback_recommendation(user_id, current_state, recent_activities)
        
        except Exception as e:
            logger.error(f"Error getting recommendation: {e}")
            return self._get_fallback_recommendation(user_id, current_state, [])
    
    def _get_fallback_recommendation(self, user_id: int, current_state: Dict, recent: List[str]) -> Dict:
        """Get fallback recommendation from predefined list"""
        fatigue_level = current_state.get('fatigue_level', 'medium')
        available_time = current_state.get('available_time', 5)
        
        # Curated wellness activities
        activities_db = [
            {
                'activity': '20-20-20 Eye Exercise',
                'category': 'eye_exercise',
                'reason': 'Reduces digital eye strain and refocuses vision',
                'duration_min': 1,
                'duration_max': 2,
                'benefits': 'Prevents eye fatigue and improves focus',
                'steps': '1. Look away from screen\n2. Find object 20 feet away\n3. Focus on it for 20 seconds\n4. Blink naturally',
                'intensity': 'Low',
                'effectiveness': 85,
                'for_fatigue': ['low', 'moderate']
            },
            {
                'activity': 'Neck and Shoulder Stretch',
                'category': 'stretching',
                'reason': 'Relieves tension from prolonged typing',
                'duration_min': 2,
                'duration_max': 3,
                'benefits': 'Improves flexibility and reduces muscle tension',
                'steps': '1. Rotate neck slowly 10 times each direction\n2. Shrug shoulders 10 times\n3. Stretch neck to each side gently',
                'intensity': 'Low',
                'effectiveness': 80,
                'for_fatigue': ['low', 'moderate', 'high']
            },
            {
                'activity': '4-7-8 Breathing Exercise',
                'category': 'breathing',
                'reason': 'Calms mind and reduces stress',
                'duration_min': 3,
                'duration_max': 5,
                'benefits': 'Promotes relaxation and mental clarity',
                'steps': '1. Sit comfortably\n2. Inhale for 4 counts\n3. Hold for 7 counts\n4. Exhale for 8 counts\n5. Repeat 4 times',
                'intensity': 'Low',
                'effectiveness': 90,
                'for_fatigue': ['high', 'critical']
            },
            {
                'activity': 'Hydration Break',
                'category': 'hydration',
                'reason': 'Maintains hydration and encourages movement',
                'duration_min': 2,
                'duration_max': 3,
                'benefits': 'Improves focus and cognitive function',
                'steps': '1. Stand up\n2. Walk to water source\n3. Drink water slowly\n4. Return to desk',
                'intensity': 'Low',
                'effectiveness': 75,
                'for_fatigue': ['moderate', 'high']
            },
            {
                'activity': 'Posture Correction Stretch',
                'category': 'posture',
                'reason': 'Corrects slouching and improves alignment',
                'duration_min': 2,
                'duration_max': 4,
                'benefits': 'Reduces back pain and improves breathing',
                'steps': '1. Stand up straight\n2. Stretch arms above head\n3. Bend backward gently for 10 seconds\n4. Roll shoulders backward 5 times',
                'intensity': 'Low',
                'effectiveness': 80,
                'for_fatigue': ['moderate', 'high']
            },
            {
                'activity': 'Mindfulness Meditation',
                'category': 'meditation',
                'reason': 'Resets mental focus and reduces stress',
                'duration_min': 3,
                'duration_max': 5,
                'benefits': 'Enhances mental clarity and emotional regulation',
                'steps': '1. Close eyes\n2. Focus on breathing\n3. Notice sensations without judgment\n4. Gently bring attention back to breath',
                'intensity': 'Low',
                'effectiveness': 88,
                'for_fatigue': ['high', 'critical']
            },
            {
                'activity': 'Short Walk',
                'category': 'walking',
                'reason': 'Improves circulation and provides mental break',
                'duration_min': 5,
                'duration_max': 10,
                'benefits': 'Increases energy and resets mental state',
                'steps': '1. Stand up\n2. Walk around office/home\n3. Change scenery if possible\n4. Return refreshed',
                'intensity': 'Moderate',
                'effectiveness': 92,
                'for_fatigue': ['high', 'critical']
            },
            {
                'activity': 'Wrist and Hand Stretch',
                'category': 'stretching',
                'reason': 'Prevents carpal tunnel and hand strain',
                'duration_min': 2,
                'duration_max': 3,
                'benefits': 'Improves hand dexterity and reduces pain',
                'steps': '1. Extend one arm\n2. Gently pull fingers backward\n3. Hold 15 seconds\n4. Repeat other hand',
                'intensity': 'Low',
                'effectiveness': 78,
                'for_fatigue': ['low', 'moderate']
            },
            {
                'activity': 'Face Massage',
                'category': 'relaxation',
                'reason': 'Improves facial blood flow and reduces tension',
                'duration_min': 2,
                'duration_max': 3,
                'benefits': 'Reduces facial tension and promotes relaxation',
                'steps': '1. Gently massage temples\n2. Massage jawline\n3. Massage forehead\n4. Relax face',
                'intensity': 'Low',
                'effectiveness': 75,
                'for_fatigue': ['moderate', 'high']
            },
            {
                'activity': 'Desk Yoga',
                'category': 'yoga',
                'reason': 'Builds strength and flexibility at desk',
                'duration_min': 5,
                'duration_max': 8,
                'benefits': 'Improves flexibility and reduces stress',
                'steps': '1. Seated cat-cow stretch\n2. Spinal twist\n3. Shoulder roll\n4. Finish with breathing',
                'intensity': 'Moderate',
                'effectiveness': 85,
                'for_fatigue': ['moderate', 'high']
            }
        ]
        
        # Filter by available time
        suitable = [a for a in activities_db if a['duration_max'] <= available_time]
        
        # Filter by fatigue level
        if suitable:
            suitable = [a for a in suitable if fatigue_level in a['for_fatigue']]
        
        # Rotate to avoid repetition
        if not suitable:
            suitable = activities_db
        
        # Avoid recent activities
        for activity in suitable:
            if activity['activity'] not in recent:
                rec = activity
                break
        else:
            rec = random.choice(suitable)
        
        return {
            'status': 'fallback',
            'user_id': user_id,
            'activity': rec['activity'],
            'reason': rec['reason'],
            'duration_min': rec['duration_min'],
            'duration_max': rec['duration_max'],
            'benefits': rec['benefits'],
            'steps': rec['steps'],
            'intensity': rec['intensity'],
            'effectiveness': rec['effectiveness'],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_adaptive_schedule(self, user_id: int, work_history: List[Dict], preferences: Dict) -> Dict:
        """Get adaptive break schedule from AI"""
        try:
            if self.use_ai and self.groq_ai and self.groq_ai.client:
                logger.info(f"Generating adaptive schedule for user {user_id}...")
                
                schedule = self.groq_ai.get_adaptive_break_schedule(
                    user_id=user_id,
                    work_history=work_history,
                    user_preferences=preferences
                )
                
                if schedule.get('status') == 'success':
                    return {
                        'status': 'success',
                        'user_id': user_id,
                        'next_break_in': schedule.get('NEXT_BREAK_IN', 20),
                        'optimal_intervals': schedule.get('OPTIMAL_INTERVALS', [20, 25, 30]),
                        'break_types': schedule.get('BREAK_TYPES', ['Micro', 'Standard']),
                        'flexibility_score': schedule.get('FLEXIBILITY_SCORE', 0.7),
                        'reasoning': schedule.get('REASONING', ''),
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Fallback schedule
            return self._get_fallback_schedule()
        
        except Exception as e:
            logger.error(f"Error getting schedule: {e}")
            return self._get_fallback_schedule()
    
    def _get_fallback_schedule(self) -> Dict:
        """Get default break schedule"""
        return {
            'status': 'fallback',
            'next_break_in': 20,
            'optimal_intervals': [20, 25, 30, 30, 35],
            'break_types': ['Micro', 'Micro', 'Standard', 'Micro', 'Standard'],
            'flexibility_score': 0.6,
            'timestamp': datetime.now().isoformat()
        }


# Global instance
break_recommender = None


def get_break_recommender() -> BreakRecommender:
    """Get or create break recommender instance"""
    global break_recommender
    if break_recommender is None:
        break_recommender = BreakRecommender()
    return break_recommender
