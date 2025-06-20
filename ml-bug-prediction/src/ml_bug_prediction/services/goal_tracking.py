"""
🎯 Goal Tracking System - Complete Implementation
Complete goal tracking with targets, progress, badges, and forecasting
"""

import json
import pandas as pd
from datetime import datetime, timedelta
import numpy as np
from typing import Dict, List, Optional, Tuple
import math
from .settings_manager import SettingsManager

class GoalTrackingSystem:
    """Complete goal tracking system with real data integration"""
    
    def __init__(self):
        self.goals_db = "data/goals.json"  # Persistent goal storage
        self.achievements_db = "data/achievements.json"  # Achievement history
        self.load_goals()
        self.load_achievements()
    
    def load_goals(self):
        """Load goals from persistent storage"""
        try:
            with open(self.goals_db, 'r') as f:
                content = f.read().strip()
                if content:
                    self.goals = json.loads(content)
                else:
                    self.goals = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.goals = {}
    
    def save_goals(self):
        """Save goals to persistent storage"""
        with open(self.goals_db, 'w') as f:
            json.dump(self.goals, f, indent=2, default=str)
    
    def load_achievements(self):
        """Load achievement history"""
        try:
            with open(self.achievements_db, 'r') as f:
                content = f.read().strip()
                if content:
                    self.achievements = json.loads(content)
                else:
                    self.achievements = {}
        except (FileNotFoundError, json.JSONDecodeError):
            self.achievements = {}
    
    def save_achievements(self):
        """Save achievements to persistent storage"""
        with open(self.achievements_db, 'w') as f:
            json.dump(self.achievements, f, indent=2, default=str)

    def create_goal(self, project_id: str, goal_data: Dict) -> Dict:
        """Create a new goal with smart defaults"""
        
        goal_id = f"{project_id}_{goal_data['type']}_{datetime.now().strftime('%Y%m%d')}"
        
        # Smart goal creation with real data baseline
        goal = {
            'id': goal_id,
            'project_id': project_id,
            'type': goal_data['type'],  # 'bug_reduction', 'health_improvement', 'component_stability'
            'title': goal_data['title'],
            'description': goal_data.get('description', ''),
            'target_value': goal_data['target_value'],
            'current_value': goal_data.get('current_value', 0),
            'baseline_value': goal_data.get('baseline_value', goal_data.get('current_value', 0)),
            'target_date': goal_data['target_date'],
            'created_date': datetime.now().isoformat(),
            'priority': goal_data.get('priority', 'medium'),  # low, medium, high, critical
            'category': goal_data.get('category', 'quality'),  # quality, performance, stability
            'metrics': {
                'progress_percentage': 0,
                'days_remaining': self._calculate_days_remaining(goal_data['target_date']),
                'velocity_required': 0,
                'current_velocity': 0,
                'confidence_score': 0
            },
            'milestones': self._generate_milestones(goal_data),
            'status': 'active',  # active, completed, paused, cancelled
            'team_assigned': goal_data.get('team_assigned', 'QA Team'),
            'stakeholders': goal_data.get('stakeholders', [])
        }
        
        # Calculate initial metrics
        goal = self._update_goal_metrics(goal)
        
        # Store goal
        if project_id not in self.goals:
            self.goals[project_id] = {}
        
        self.goals[project_id][goal_id] = goal
        self.save_goals()
        
        return goal

    def update_goal_progress(self, project_id: str, goal_id: str, current_value: float) -> Dict:
        """Update goal progress with real data"""
        
        if project_id not in self.goals or goal_id not in self.goals[project_id]:
            raise ValueError(f"Goal {goal_id} not found")
        
        goal = self.goals[project_id][goal_id]
        
        # Update current value
        old_value = goal['current_value']
        goal['current_value'] = current_value
        goal['last_updated'] = datetime.now().isoformat()
        
        # Calculate velocity
        if 'progress_history' not in goal:
            goal['progress_history'] = []
        
        goal['progress_history'].append({
            'date': datetime.now().isoformat(),
            'value': current_value,
            'change': current_value - old_value
        })
        
        # Keep only last 30 data points
        goal['progress_history'] = goal['progress_history'][-30:]
        
        # Update metrics
        goal = self._update_goal_metrics(goal)
        
        # Check for achievements
        achievements = self._check_achievements(goal)
        
        # Save updated goal
        self.goals[project_id][goal_id] = goal
        self.save_goals()
        
        return {
            'goal': goal,
            'new_achievements': achievements
        }

    def _update_goal_metrics(self, goal: Dict) -> Dict:
        """Calculate all goal metrics"""
        
        baseline = goal['baseline_value']
        current = goal['current_value']
        target = goal['target_value']
        
        # Calculate progress percentage
        if goal['type'] == 'bug_reduction':
            # For bug reduction, progress is reverse (fewer bugs = more progress)
            if baseline > 0:
                progress = max(0, (baseline - current) / (baseline - target) * 100)
            else:
                progress = 100 if current <= target else 0
        else:
            # For improvements (health score, etc.)
            if target > baseline:
                progress = max(0, (current - baseline) / (target - baseline) * 100)
            else:
                progress = 100 if current >= target else 0
        
        goal['metrics']['progress_percentage'] = min(100, max(0, progress))
        
        # Calculate days remaining
        goal['metrics']['days_remaining'] = self._calculate_days_remaining(goal['target_date'])
        
        # Calculate required velocity
        days_remaining = goal['metrics']['days_remaining']
        if days_remaining > 0:
            remaining_work = abs(target - current)
            goal['metrics']['velocity_required'] = remaining_work / days_remaining
        else:
            goal['metrics']['velocity_required'] = 0
        
        # Calculate current velocity (from last 7 days)
        goal['metrics']['current_velocity'] = self._calculate_current_velocity(goal)
        
        # Calculate confidence score
        goal['metrics']['confidence_score'] = self._calculate_confidence_score(goal)
        
        return goal

    def _generate_milestones(self, goal_data: Dict) -> List[Dict]:
        """Generate smart milestones for the goal"""
        
        milestones = []
        baseline = goal_data.get('baseline_value', 0)
        target = goal_data['target_value']
        
        # Generate 25%, 50%, 75%, and 100% milestones
        for percentage in [25, 50, 75, 100]:
            if goal_data['type'] == 'bug_reduction':
                milestone_value = baseline - ((baseline - target) * percentage / 100)
            else:
                milestone_value = baseline + ((target - baseline) * percentage / 100)
            
            milestones.append({
                'percentage': percentage,
                'value': round(milestone_value, 1),
                'title': self._get_milestone_title(percentage),
                'description': self._get_milestone_description(percentage, goal_data['type']),
                'achieved': False,
                'achieved_date': None,
                'badge_earned': self._get_milestone_badge(percentage)
            })
        
        return milestones

    def _get_milestone_title(self, percentage: int) -> str:
        """Get milestone title based on percentage"""
        titles = {
            25: "🚀 Great Start!",
            50: "🔥 Halfway Hero!",
            75: "⭐ Almost There!",
            100: "🏆 Goal Achieved!"
        }
        return titles.get(percentage, f"{percentage}% Complete")

    def _get_milestone_description(self, percentage: int, goal_type: str) -> str:
        """Get milestone description"""
        if goal_type == 'bug_reduction':
            descriptions = {
                25: "First quarter of bugs eliminated - momentum building!",
                50: "Halfway to your bug reduction target - excellent progress!",
                75: "Three-quarters complete - the finish line is in sight!",
                100: "Bug reduction goal achieved - outstanding work!"
            }
        else:
            descriptions = {
                25: "Quarter of the way to your improvement target!",
                50: "Halfway to excellence - keep up the great work!",
                75: "Almost there - final push to reach your goal!",
                100: "Goal achieved - exceptional performance!"
            }
        return descriptions.get(percentage, f"{percentage}% milestone reached")

    def _get_milestone_badge(self, percentage: int) -> str:
        """Get badge for milestone"""
        badges = {
            25: "🥉 Bronze Achiever",
            50: "🥈 Silver Performer",
            75: "🥇 Gold Standard",
            100: "💎 Diamond Excellence"
        }
        return badges.get(percentage, f"{percentage}% Badge")

    def _calculate_days_remaining(self, target_date: str) -> int:
        """Calculate days remaining to target"""
        target = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
        now = datetime.now()
        return max(0, (target - now).days)

    def _calculate_current_velocity(self, goal: Dict) -> float:
        """Calculate current velocity from recent progress"""
        if 'progress_history' not in goal or len(goal['progress_history']) < 2:
            return 0
        
        # Use last 7 days or all available data
        recent_data = goal['progress_history'][-7:]
        
        if len(recent_data) < 2:
            return 0
        
        # Calculate average daily change
        total_change = 0
        days_count = 0
        
        for i in range(1, len(recent_data)):
            change = recent_data[i]['change']
            total_change += abs(change)
            days_count += 1
        
        return total_change / days_count if days_count > 0 else 0

    def _calculate_confidence_score(self, goal: Dict) -> int:
        """Calculate confidence score for goal achievement"""
        
        metrics = goal['metrics']
        
        # Base confidence from progress
        progress_conf = min(50, metrics['progress_percentage'] * 0.5)
        
        # Velocity confidence
        velocity_conf = 0
        if metrics['velocity_required'] > 0:
            velocity_ratio = metrics['current_velocity'] / metrics['velocity_required']
            velocity_conf = min(30, velocity_ratio * 30)
        
        # Time confidence
        time_conf = 0
        if metrics['days_remaining'] > 0:
            if metrics['days_remaining'] > 30:
                time_conf = 20
            elif metrics['days_remaining'] > 7:
                time_conf = 15
            else:
                time_conf = 5
        
        return min(100, int(progress_conf + velocity_conf + time_conf))

    def _check_achievements(self, goal: Dict) -> List[Dict]:
        """Check and award achievements"""
        
        new_achievements = []
        current_progress = goal['metrics']['progress_percentage']
        
        # Check milestone achievements
        for milestone in goal['milestones']:
            if not milestone['achieved'] and current_progress >= milestone['percentage']:
                milestone['achieved'] = True
                milestone['achieved_date'] = datetime.now().isoformat()
                
                achievement = {
                    'id': f"{goal['id']}_milestone_{milestone['percentage']}",
                    'goal_id': goal['id'],
                    'type': 'milestone',
                    'title': milestone['title'],
                    'description': milestone['description'],
                    'badge': milestone['badge_earned'],
                    'achieved_date': milestone['achieved_date'],
                    'points': milestone['percentage']  # Points based on milestone
                }
                
                new_achievements.append(achievement)
                
                # Store achievement
                if goal['project_id'] not in self.achievements:
                    self.achievements[goal['project_id']] = []
                
                self.achievements[goal['project_id']].append(achievement)
        
        if new_achievements:
            self.save_achievements()
        
        return new_achievements

    def get_project_goals(self, project_id: str) -> Dict:
        """Get all goals for a project with analytics"""
        
        if project_id not in self.goals:
            return {
                'goals': [],
                'analytics': {
                    'total_goals': 0,
                    'active_goals': 0,
                    'completed_goals': 0,
                    'average_progress': 0,
                    'goals_on_track': 0,
                    'achievements_earned': 0
                }
            }
        
        goals = list(self.goals[project_id].values())
        
        # Calculate analytics
        analytics = {
            'total_goals': len(goals),
            'active_goals': len([g for g in goals if g['status'] == 'active']),
            'completed_goals': len([g for g in goals if g['status'] == 'completed']),
            'average_progress': np.mean([g['metrics']['progress_percentage'] for g in goals]) if goals else 0,
            'goals_on_track': len([g for g in goals if g['metrics']['confidence_score'] >= 70]),
            'achievements_earned': len(self.achievements.get(project_id, []))
        }
        
        return {
            'goals': goals,
            'analytics': analytics
        }

    def predict_goal_completion(self, project_id: str, goal_id: str) -> Dict:
        """Predict when goal will be completed"""
        
        if project_id not in self.goals or goal_id not in self.goals[project_id]:
            raise ValueError(f"Goal {goal_id} not found")
        
        goal = self.goals[project_id][goal_id]
        
        current_velocity = goal['metrics']['current_velocity']
        remaining_work = abs(goal['target_value'] - goal['current_value'])
        
        prediction = {
            'goal_id': goal_id,
            'current_progress': goal['metrics']['progress_percentage'],
            'days_remaining_scheduled': goal['metrics']['days_remaining'],
            'predicted_completion_date': None,
            'confidence': goal['metrics']['confidence_score'],
            'status': 'unknown'
        }
        
        if current_velocity > 0:
            predicted_days = remaining_work / current_velocity
            predicted_date = datetime.now() + timedelta(days=predicted_days)
            
            prediction['predicted_completion_date'] = predicted_date.isoformat()
            
            # Determine status
            scheduled_date = datetime.fromisoformat(goal['target_date'].replace('Z', '+00:00'))
            
            if predicted_date <= scheduled_date:
                prediction['status'] = 'on_track'
            elif predicted_date <= scheduled_date + timedelta(days=7):
                prediction['status'] = 'slight_delay'
            else:
                prediction['status'] = 'at_risk'
        
        return prediction

    def get_achievement_summary(self, project_id: str) -> Dict:
        """Get achievement summary for project"""
        
        achievements = self.achievements.get(project_id, [])
        
        # Calculate achievement stats
        total_points = sum(a.get('points', 0) for a in achievements)
        
        # Group by type
        milestone_achievements = [a for a in achievements if a['type'] == 'milestone']
        
        # Recent achievements (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        recent_achievements = [
            a for a in achievements 
            if datetime.fromisoformat(a['achieved_date'].replace('Z', '+00:00')) >= thirty_days_ago
        ]
        
        return {
            'total_achievements': len(achievements),
            'total_points': total_points,
            'milestone_achievements': len(milestone_achievements),
            'recent_achievements': len(recent_achievements),
            'achievement_list': achievements[-10:],  # Last 10 achievements
            'badge_collection': list(set(a.get('badge', '') for a in achievements if a.get('badge')))
        }

    def create_default_goals(self, project_id: str, current_data: Dict) -> List[Dict]:
        """Create intelligent default goals based on current project data"""
        
        default_goals = []
        current_date = datetime.now()
        
        # Determine goal context based on project
        if project_id == 'ALL':
            settings_manager = SettingsManager()
            project_name = f'All {settings_manager.get_company_name()} Projects'
            team_context = 'All Teams'
        else:
            project_name = project_id
            team_context = f'{project_id} Team'
        
        # Goal 1: Bug Reduction (30-day target)
        if current_data.get('total_bugs', 0) > 0:
            total_bugs = current_data['total_bugs']
            reduction_target = max(1, int(total_bugs * 0.7))  # 30% reduction
            
            bug_goal = self.create_goal(project_id, {
                'type': 'bug_reduction',
                'title': f'Reduce {project_name} Bugs by 30%',
                'description': f'Reduce total bugs from {total_bugs} to {reduction_target} or fewer across {project_name}',
                'target_value': reduction_target,
                'current_value': total_bugs,
                'baseline_value': total_bugs,
                'target_date': (current_date + timedelta(days=30)).isoformat(),
                'priority': 'high',
                'category': 'quality',
                'team_assigned': team_context
            })
            default_goals.append(bug_goal)
        
        # Goal 2: Health Score Improvement (60-day target)
        current_health = current_data.get('health_score', 50)
        target_health = min(95, current_health + 20)
        
        health_goal = self.create_goal(project_id, {
            'type': 'health_improvement',
            'title': f'Improve {project_name} Health Score to {target_health}',
            'description': f'Increase {project_name} health score from {current_health} to {target_health}',
            'target_value': target_health,
            'current_value': current_health,
            'baseline_value': current_health,
            'target_date': (current_date + timedelta(days=60)).isoformat(),
            'priority': 'medium',
            'category': 'quality',
            'team_assigned': team_context
        })
        default_goals.append(health_goal)
        
        # Goal 3: Component Stability (90-day target)
        critical_components = current_data.get('critical_components', 0)
        if critical_components > 0:
            target_critical = max(0, critical_components - 1)
            
            stability_goal = self.create_goal(project_id, {
                'type': 'component_stability',
                'title': f'Reduce {project_name} Critical Components',
                'description': f'Reduce critical risk components from {critical_components} to {target_critical} in {project_name}',
                'target_value': target_critical,
                'current_value': critical_components,
                'baseline_value': critical_components,
                'target_date': (current_date + timedelta(days=90)).isoformat(),
                'priority': 'high',
                'category': 'stability',
                'team_assigned': team_context
            })
            default_goals.append(stability_goal)
        
        return default_goals

    def generate_goal_insights(self, project_id: str) -> Dict:
        """Generate AI insights about goal progress"""
        
        project_goals = self.get_project_goals(project_id)
        goals = project_goals['goals']
        analytics = project_goals['analytics']
        
        insights = {
            'summary': '',
            'recommendations': [],
            'risk_alerts': [],
            'success_stories': [],
            'next_actions': []
        }
        
        if not goals:
            insights['summary'] = "🎯 Ready to set your first goals! Start with bug reduction and health improvement targets."
            insights['recommendations'] = [
                "Create a 30-day bug reduction goal",
                "Set a health score improvement target",
                "Define component stability objectives"
            ]
            return insights
        
        # Generate summary
        avg_progress = analytics['average_progress']
        if avg_progress >= 80:
            insights['summary'] = f"🔥 Exceptional progress! {analytics['active_goals']} goals averaging {avg_progress:.1f}% completion."
        elif avg_progress >= 60:
            insights['summary'] = f"📈 Good momentum! {analytics['active_goals']} goals with {avg_progress:.1f}% average progress."
        elif avg_progress >= 40:
            insights['summary'] = f"⚡ Building progress on {analytics['active_goals']} goals. {avg_progress:.1f}% average completion."
        else:
            insights['summary'] = f"🎯 Early stage: {analytics['active_goals']} goals need attention. {avg_progress:.1f}% average progress."
        
        # Analyze individual goals
        for goal in goals:
            if goal['status'] != 'active':
                continue
                
            progress = goal['metrics']['progress_percentage']
            confidence = goal['metrics']['confidence_score']
            days_remaining = goal['metrics']['days_remaining']
            
            # Success stories
            if progress >= 75:
                insights['success_stories'].append(
                    f"🏆 '{goal['title']}' at {progress:.1f}% - excellent progress!"
                )
            
            # Risk alerts
            if confidence < 50 and days_remaining < 7:
                insights['risk_alerts'].append(
                    f"🚨 '{goal['title']}' at risk - {days_remaining} days left, {confidence}% confidence"
                )
            elif progress < 25 and days_remaining < 14:
                insights['risk_alerts'].append(
                    f"⚠️ '{goal['title']}' needs attention - slow progress with {days_remaining} days remaining"
                )
        
        # Recommendations
        if analytics['goals_on_track'] < analytics['active_goals'] / 2:
            insights['recommendations'].append("Focus resources on highest priority goals")
            insights['recommendations'].append("Consider extending timelines for realistic targets")
        
        if analytics['average_progress'] > 60:
            insights['recommendations'].append("Great momentum! Consider setting stretch goals")
        
        # Next actions
        at_risk_goals = [g for g in goals if g['metrics']['confidence_score'] < 60 and g['status'] == 'active']
        if at_risk_goals:
            insights['next_actions'].append(f"Review {len(at_risk_goals)} at-risk goals this week")
        
        completing_goals = [g for g in goals if g['metrics']['progress_percentage'] > 80 and g['status'] == 'active']
        if completing_goals:
            insights['next_actions'].append(f"Plan completion celebration for {len(completing_goals)} nearly-finished goals")
        
        return insights 

    def delete_goal(self, project_id: str, goal_id: str) -> bool:
        """Delete a goal and its associated achievements"""
        
        if project_id not in self.goals or goal_id not in self.goals[project_id]:
            raise ValueError(f"Goal {goal_id} not found in project {project_id}")
        
        # Get goal details for logging
        goal = self.goals[project_id][goal_id]
        
        # Remove the goal
        del self.goals[project_id][goal_id]
        
        # Clean up empty project
        if not self.goals[project_id]:
            del self.goals[project_id]
        
        # Remove associated achievements
        if project_id in self.achievements:
            self.achievements[project_id] = [
                achievement for achievement in self.achievements[project_id]
                if achievement.get('goal_id') != goal_id
            ]
            
            # Clean up empty achievements
            if not self.achievements[project_id]:
                del self.achievements[project_id]
        
        # Save updated data
        self.save_goals()
        self.save_achievements()
        
        return True

    def cancel_goal(self, project_id: str, goal_id: str) -> Dict:
        """Cancel a goal (mark as cancelled instead of deleting)"""
        
        if project_id not in self.goals or goal_id not in self.goals[project_id]:
            raise ValueError(f"Goal {goal_id} not found in project {project_id}")
        
        goal = self.goals[project_id][goal_id]
        
        # Update status to cancelled
        goal['status'] = 'cancelled'
        goal['cancelled_date'] = datetime.now().isoformat()
        goal['last_updated'] = datetime.now().isoformat()
        
        # Save updated goal
        self.goals[project_id][goal_id] = goal
        self.save_goals()
        
        return goal