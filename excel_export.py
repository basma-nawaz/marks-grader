import pandas as pd
import streamlit as st
from typing import List, Dict, Any
from io import BytesIO
from datetime import datetime


class ExcelExporter:
    """Service for exporting grading results to Excel format"""

    def __init__(self):
        pass

    def create_excel_report(self, results: List[Dict[str, Any]]) -> BytesIO:
        """
        Create a comprehensive Excel report from grading results

        Args:
            results: List of grading result dictionaries

        Returns:
            BytesIO object containing the Excel file
        """
        try:
            # Create a BytesIO buffer
            output = BytesIO()

            # Create workbook and worksheets
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:

                # Create main summary sheet
                self._create_summary_sheet(results, writer)

                # Create detailed results sheet
                self._create_detailed_sheet(results, writer)

                # Create criteria breakdown sheet (if custom criteria used)
                self._create_criteria_sheet(results, writer)

                # Create questions breakdown sheet (if multiple questions detected)
                self._create_questions_sheet(results, writer)

                # Add formatting
                self._format_workbook(writer)

            output.seek(0)
            return output.getvalue()

        except Exception as e:
            st.error(f"Error creating Excel report: {str(e)}")
            return None

    def _create_summary_sheet(self, results: List[Dict[str, Any]], writer):
        """Create the main summary sheet"""
        # Prepare summary data
        summary_data = []
        for result in results:
            summary_data.append({
                'Student File': result['filename'],
                'Score': f"{result['awarded_marks']}/{result['total_marks']}",
                'Percentage': round(result['percentage'], 1),
                'Letter Grade': self._calculate_letter_grade(result['percentage']),
                'File Type': result['file_type'].upper(),
                'Status': 'Graded'
            })

        # Create DataFrame and write to Excel
        df_summary = pd.DataFrame(summary_data)
        df_summary.to_excel(writer, sheet_name='Summary', index=False)

        # Add statistics
        stats_data = {
            'Metric': [
                'Total Submissions',
                'Average Score (%)',
                'Highest Score (%)',
                'Lowest Score (%)',
                'Students Above 80%',
                'Students Above 60%',
                'Students Below 60%'
            ],
            'Value': [
                len(results),
                round(sum(r['percentage'] for r in results) / len(results), 1) if results else 0,
                round(max(r['percentage'] for r in results), 1) if results else 0,
                round(min(r['percentage'] for r in results), 1) if results else 0,
                sum(1 for r in results if r['percentage'] >= 80),
                sum(1 for r in results if r['percentage'] >= 60),
                sum(1 for r in results if r['percentage'] < 60)
            ]
        }

        df_stats = pd.DataFrame(stats_data)

        # Write statistics starting from a specific cell
        startrow = len(df_summary) + 3
        df_stats.to_excel(writer, sheet_name='Summary', startrow=startrow, index=False)

        # Add metadata
        metadata = {
            'Report Generated': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'Total Files Processed': [len(results)],
            'System': ['AI Grading System v1.0']
        }
        df_metadata = pd.DataFrame(metadata)

        metadata_startrow = startrow + len(df_stats) + 3
        df_metadata.to_excel(writer, sheet_name='Summary', startrow=metadata_startrow, index=False)

    def _create_detailed_sheet(self, results: List[Dict[str, Any]], writer):
        """Create detailed results sheet with feedback"""
        detailed_data = []

        for result in results:
            detailed_data.append({
                'Student File': result['filename'],
                'Total Score': result['awarded_marks'],
                'Max Score': result['total_marks'],
                'Percentage': round(result['percentage'], 1),
                'Letter Grade': self._calculate_letter_grade(result['percentage']),
                'Feedback': result.get('feedback', ''),
                'Strengths': '; '.join(result.get('strengths', [])),
                'Areas for Improvement': '; '.join(result.get('areas_for_improvement', [])),
                'Grade Justification': result.get('grade_justification', ''),
                'File Type': result['file_type'].upper()
            })

        df_detailed = pd.DataFrame(detailed_data)
        df_detailed.to_excel(writer, sheet_name='Detailed Results', index=False)

    def _create_criteria_sheet(self, results: List[Dict[str, Any]], writer):
        """Create criteria breakdown sheet"""
        # Check if any results have criteria breakdown
        has_criteria = any(result.get('criteria_scores') for result in results)

        if not has_criteria:
            return

        # Collect all unique criteria
        all_criteria = set()
        for result in results:
            if result.get('criteria_scores'):
                all_criteria.update(result['criteria_scores'].keys())

        if not all_criteria:
            return

        # Create criteria breakdown data
        criteria_data = []
        for result in results:
            row = {'Student File': result['filename']}
            criteria_scores = result.get('criteria_scores', {})

            for criterion in all_criteria:
                row[criterion] = criteria_scores.get(criterion, 0)

            row['Total'] = result['awarded_marks']
            criteria_data.append(row)

        df_criteria = pd.DataFrame(criteria_data)
        df_criteria.to_excel(writer, sheet_name='Criteria Breakdown', index=False)

    def _create_questions_sheet(self, results: List[Dict[str, Any]], writer):
        """Create questions breakdown sheet"""
        questions_data = []

        for result in results:
            questions = result.get('questions', [])

            if not questions:
                # If no questions breakdown, add a single row
                questions_data.append({
                    'Student File': result['filename'],
                    'Question Number': 'Overall',
                    'Question Description': 'Complete Assignment',
                    'Score Awarded': result['awarded_marks'],
                    'Max Score': result['total_marks'],
                    'Percentage': round(result['percentage'], 1),
                    'Feedback': result.get('feedback', '')[:200] + '...' if len(
                        result.get('feedback', '')) > 200 else result.get('feedback', '')
                })
            else:
                # Add each question
                for question in questions:
                    questions_data.append({
                        'Student File': result['filename'],
                        'Question Number': question.get('question_number', 'N/A'),
                        'Question Description': question.get('question_text', 'N/A'),
                        'Score Awarded': question.get('score', 0),
                        'Max Score': question.get('max_score', 0),
                        'Percentage': round((question.get('score', 0) / question.get('max_score', 1)) * 100,
                                            1) if question.get('max_score', 0) > 0 else 0,
                        'Feedback': question.get('feedback', '')[:200] + '...' if len(
                            question.get('feedback', '')) > 200 else question.get('feedback', '')
                    })

        if questions_data:
            df_questions = pd.DataFrame(questions_data)
            df_questions.to_excel(writer, sheet_name='Questions Breakdown', index=False)

    def _format_workbook(self, writer):
        """Apply formatting to the Excel workbook"""
        try:
            workbook = writer.book

            # Define formats
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })

            percentage_format = workbook.add_format({
                'num_format': '0.0"%"',
                'align': 'center'
            })

            center_format = workbook.add_format({
                'align': 'center'
            })

            # Format each worksheet
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]

                # Auto-adjust column widths
                worksheet.set_column('A:Z', 15)

                # Format headers (assuming headers are in row 1)
                worksheet.set_row(0, None, header_format)

                # Format percentage columns
                if 'Percentage' in [cell.value for cell in worksheet.table.header]:
                    # This is a simplified approach - in practice, you'd need to identify the actual column
                    pass

        except Exception as e:
            # Formatting errors shouldn't break the export
            st.warning(f"Warning: Could not apply all formatting to Excel file: {str(e)}")

    def _calculate_letter_grade(self, percentage: float) -> str:
        """Calculate letter grade based on percentage"""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'

    def export_simple_csv(self, results: List[Dict[str, Any]]) -> str:
        """
        Create a simple CSV export as an alternative to Excel

        Args:
            results: List of grading result dictionaries

        Returns:
            CSV content as string
        """
        try:
            # Prepare data for CSV
            csv_data = []
            for result in results:
                csv_data.append({
                    'Student_File': result['filename'],
                    'Score': f"{result['awarded_marks']}/{result['total_marks']}",
                    'Percentage': round(result['percentage'], 1),
                    'Letter_Grade': self._calculate_letter_grade(result['percentage']),
                    'File_Type': result['file_type'].upper(),
                    'Feedback': result.get('feedback', '').replace('\n', ' ').replace('\r', ' ')
                })

            # Create DataFrame and return CSV
            df = pd.DataFrame(csv_data)
            return df.to_csv(index=False)

        except Exception as e:
            st.error(f"Error creating CSV export: {str(e)}")
            return ""
