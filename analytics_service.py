"""
Analytics Service for AI Grading System
Provides comprehensive analytics and visualizations for grading results
"""

import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict, Any
import numpy as np


class AnalyticsService:
    """Service for generating analytics and visualizations from grading results"""
    
    def __init__(self):
        self.results = []
        self.df = None
    
    def load_results(self, results: List[Dict[str, Any]]):
        """Load grading results for analysis"""
        self.results = results
        self.df = self._create_dataframe()
    
    def _create_dataframe(self) -> pd.DataFrame:
        """Create a structured DataFrame from grading results"""
        if not self.results:
            return pd.DataFrame()
        
        # Extract basic information
        data = []
        for result in self.results:
            student_data = {
                'filename': result.get('filename', ''),
                'total_marks': result.get('total_marks', 0),
                'awarded_marks': result.get('awarded_marks', 0),
                'percentage': result.get('percentage', 0)
            }
            
            # Extract question-level data
            questions = result.get('questions', [])
            for i, question in enumerate(questions, 1):
                student_data[f'question_{i}_attempted'] = question.get('attempted', False)
                student_data[f'question_{i}_score'] = question.get('score', 0)
                student_data[f'question_{i}_max_score'] = question.get('max_score', 0)
                student_data[f'question_{i}_percentage'] = (
                    (question.get('score', 0) / question.get('max_score', 1)) * 100 
                    if question.get('max_score', 0) > 0 else 0
                )
            
            data.append(student_data)
        
        return pd.DataFrame(data)
    
    def get_max_questions(self) -> int:
        """Get the maximum number of questions across all submissions"""
        if self.df is None or self.df.empty:
            return 0
        
        question_cols = [col for col in self.df.columns if col.startswith('question_') and col.endswith('_attempted')]
        return len(question_cols)
    
    def analyze_question_attempts(self, question_number: int) -> Dict[str, Any]:
        """Analyze attempts for a specific question"""
        if self.df is None or self.df.empty:
            return {'attempted_count': 0, 'total_students': 0, 'percentage': 0}
        
        col_name = f'question_{question_number}_attempted'
        if col_name not in self.df.columns:
            return {'attempted_count': 0, 'total_students': len(self.df), 'percentage': 0}
        
        attempted_count = self.df[col_name].sum()
        total_students = len(self.df)
        percentage = (attempted_count / total_students) * 100 if total_students > 0 else 0
        
        return {
            'attempted_count': int(attempted_count),
            'total_students': total_students,
            'percentage': percentage
        }
    
    def get_most_attempted_question(self) -> Dict[str, Any]:
        """Find which question was attempted by the most students"""
        if self.df is None or self.df.empty:
            return {'question_number': 0, 'attempts': 0, 'percentage': 0}
        
        max_questions = self.get_max_questions()
        if max_questions == 0:
            return {'question_number': 0, 'attempts': 0, 'percentage': 0}
        
        attempts_data = []
        for i in range(1, max_questions + 1):
            analysis = self.analyze_question_attempts(i)
            attempts_data.append({
                'question': i,
                'attempts': analysis['attempted_count'],
                'percentage': analysis['percentage']
            })
        
        if not attempts_data:
            return {'question_number': 0, 'attempts': 0, 'percentage': 0}
        
        most_attempted = max(attempts_data, key=lambda x: x['attempts'])
        return {
            'question_number': most_attempted['question'],
            'attempts': most_attempted['attempts'],
            'percentage': most_attempted['percentage']
        }
    
    def get_average_questions_attempted(self) -> float:
        """Calculate average number of questions attempted per student"""
        if self.df is None or self.df.empty:
            return 0.0
        
        max_questions = self.get_max_questions()
        if max_questions == 0:
            return 0.0
        
        total_attempts = 0
        for i in range(1, max_questions + 1):
            col_name = f'question_{i}_attempted'
            if col_name in self.df.columns:
                total_attempts += self.df[col_name].sum()
        
        return total_attempts / len(self.df) if len(self.df) > 0 else 0.0
    
    def get_most_skipped_question(self) -> Dict[str, Any]:
        """Find which question was skipped by the most students"""
        if self.df is None or self.df.empty:
            return {'question_number': 0, 'skipped_count': 0, 'percentage': 0}
        
        max_questions = self.get_max_questions()
        if max_questions == 0:
            return {'question_number': 0, 'skipped_count': 0, 'percentage': 0}
        
        skip_data = []
        for i in range(1, max_questions + 1):
            analysis = self.analyze_question_attempts(i)
            skipped_count = analysis['total_students'] - analysis['attempted_count']
            skip_percentage = (skipped_count / analysis['total_students']) * 100 if analysis['total_students'] > 0 else 0
            
            skip_data.append({
                'question': i,
                'skipped_count': skipped_count,
                'percentage': skip_percentage
            })
        
        if not skip_data:
            return {'question_number': 0, 'skipped_count': 0, 'percentage': 0}
        
        most_skipped = max(skip_data, key=lambda x: x['skipped_count'])
        return {
            'question_number': most_skipped['question'],
            'skipped_count': most_skipped['skipped_count'],
            'percentage': most_skipped['percentage']
        }
    
    def get_grade_distribution(self) -> Dict[str, Any]:
        """Analyze overall grade distribution"""
        if self.df is None or self.df.empty:
            return {'grades': {}, 'average': 0, 'median': 0, 'std_dev': 0}
        
        percentages = self.df['percentage'].tolist()
        
        # Define grade ranges
        grade_ranges = {
            'A (90-100%)': (90, 100),
            'B (80-89%)': (80, 89),
            'C (70-79%)': (70, 79),
            'D (60-69%)': (60, 69),
            'F (0-59%)': (0, 59)
        }
        
        grade_counts = {}
        for grade, (min_val, max_val) in grade_ranges.items():
            count = sum(1 for p in percentages if min_val <= p <= max_val)
            grade_counts[grade] = count
        
        return {
            'grades': grade_counts,
            'average': np.mean(percentages) if percentages else 0,
            'median': np.median(percentages) if percentages else 0,
            'std_dev': np.std(percentages) if percentages else 0
        }
    
    def get_consistent_performers(self) -> List[Dict[str, Any]]:
        """Find students who performed consistently across all questions"""
        if self.df is None or self.df.empty:
            return []
        
        max_questions = self.get_max_questions()
        if max_questions < 2:
            return []
        
        consistent_students = []
        
        for _, row in self.df.iterrows():
            question_percentages = []
            for i in range(1, max_questions + 1):
                score_col = f'question_{i}_percentage'
                if score_col in row and pd.notna(row[score_col]):
                    question_percentages.append(row[score_col])
            
            if len(question_percentages) >= 2:
                std_dev = np.std(question_percentages)
                avg_score = np.mean(question_percentages)
                
                # Consider consistent if std deviation is low (< 15%) and average is decent (> 50%)
                if std_dev < 15 and avg_score > 50:
                    consistent_students.append({
                        'filename': row['filename'],
                        'average_score': avg_score,
                        'std_deviation': std_dev,
                        'question_scores': question_percentages
                    })
        
        return sorted(consistent_students, key=lambda x: x['std_deviation'])
    
    def get_inconsistent_performers(self) -> List[Dict[str, Any]]:
        """Find students with large discrepancies between questions"""
        if self.df is None or self.df.empty:
            return []
        
        max_questions = self.get_max_questions()
        if max_questions < 2:
            return []
        
        inconsistent_students = []
        
        for _, row in self.df.iterrows():
            question_percentages = []
            for i in range(1, max_questions + 1):
                score_col = f'question_{i}_percentage'
                if score_col in row and pd.notna(row[score_col]):
                    question_percentages.append(row[score_col])
            
            if len(question_percentages) >= 2:
                std_dev = np.std(question_percentages)
                min_score = min(question_percentages)
                max_score = max(question_percentages)
                score_range = max_score - min_score
                
                # Consider inconsistent if std deviation is high (> 25%) or large score range (> 40%)
                if std_dev > 25 or score_range > 40:
                    inconsistent_students.append({
                        'filename': row['filename'],
                        'std_deviation': std_dev,
                        'score_range': score_range,
                        'min_score': min_score,
                        'max_score': max_score,
                        'question_scores': question_percentages
                    })
        
        return sorted(inconsistent_students, key=lambda x: x['std_deviation'], reverse=True)
    
    def get_above_average_percentage(self) -> Dict[str, Any]:
        """Calculate percentage of students scoring above class average"""
        if self.df is None or self.df.empty:
            return {'percentage': 0, 'count': 0, 'total': 0, 'class_average': 0}
        
        percentages = self.df['percentage'].tolist()
        class_average = np.mean(percentages) if percentages else 0
        
        above_average_count = sum(1 for p in percentages if p > class_average)
        total_students = len(percentages)
        percentage_above = (above_average_count / total_students) * 100 if total_students > 0 else 0
        
        return {
            'percentage': percentage_above,
            'count': above_average_count,
            'total': total_students,
            'class_average': class_average
        }
    
    def create_question_attempts_chart(self) -> go.Figure:
        """Create interactive chart for question attempts"""
        max_questions = self.get_max_questions()
        if max_questions == 0:
            return go.Figure()
        
        questions = list(range(1, max_questions + 1))
        attempts = []
        skipped = []
        
        for q in questions:
            analysis = self.analyze_question_attempts(q)
            attempts.append(analysis['attempted_count'])
            skipped.append(analysis['total_students'] - analysis['attempted_count'])
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Attempted',
            x=questions,
            y=attempts,
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Skipped',
            x=questions,
            y=skipped,
            marker_color='lightcoral'
        ))
        
        fig.update_layout(
            title='Question Attempts vs Skipped',
            xaxis_title='Question Number',
            yaxis_title='Number of Students',
            barmode='stack',
            height=400
        )
        
        return fig
    
    def create_grade_distribution_chart(self) -> go.Figure:
        """Create grade distribution pie chart"""
        distribution = self.get_grade_distribution()
        
        if not distribution['grades']:
            return go.Figure()
        
        labels = list(distribution['grades'].keys())
        values = list(distribution['grades'].values())
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.3,
            textinfo='label+percent+value'
        )])
        
        fig.update_layout(
            title='Grade Distribution',
            height=400
        )
        
        return fig
    
    def create_performance_consistency_chart(self) -> go.Figure:
        """Create chart showing performance consistency"""
        if self.df is None or self.df.empty:
            return go.Figure()
        
        max_questions = self.get_max_questions()
        if max_questions < 2:
            return go.Figure()
        
        students = []
        std_devs = []
        avg_scores = []
        
        for _, row in self.df.iterrows():
            question_percentages = []
            for i in range(1, max_questions + 1):
                score_col = f'question_{i}_percentage'
                if score_col in row and pd.notna(row[score_col]):
                    question_percentages.append(row[score_col])
            
            if len(question_percentages) >= 2:
                students.append(row['filename'][:15] + '...' if len(row['filename']) > 15 else row['filename'])
                std_devs.append(np.std(question_percentages))
                avg_scores.append(np.mean(question_percentages))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=std_devs,
            y=avg_scores,
            mode='markers+text',
            text=students,
            textposition='top center',
            marker=dict(
                size=10,
                color=avg_scores,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Average Score (%)")
            ),
            name='Students'
        ))
        
        fig.update_layout(
            title='Performance Consistency Analysis',
            xaxis_title='Standard Deviation (Lower = More Consistent)',
            yaxis_title='Average Score (%)',
            height=500
        )
        
        return fig