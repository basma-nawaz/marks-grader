from typing import Optional, List, Dict, Any
import os


def validate_file_type(filename: str) -> Optional[str]:
    """
    Validate and return the file type based on file extension

    Args:
        filename: Name of the file to validate

    Returns:
        File type (pdf, docx, jpg, jpeg, png) or None if invalid
    """
    if not filename:
        return None

    # Get file extension
    _, ext = os.path.splitext(filename.lower())
    ext = ext.lstrip('.')

    # Supported file types
    supported_types = {
        'pdf': 'pdf',
        'docx': 'docx',
        'doc': 'docx',  # Treat .doc as docx for processing
        'jpg': 'jpg',
        'jpeg': 'jpeg',
        'png': 'png'
    }

    return supported_types.get(ext)


def format_grade_display(percentage: float) -> str:
    """
    Format percentage into a readable grade display

    Args:
        percentage: Grade percentage (0-100)

    Returns:
        Formatted grade string with letter grade and color coding
    """
    if percentage >= 90:
        return f"A ({percentage:.1f}%)"
    elif percentage >= 80:
        return f"B ({percentage:.1f}%)"
    elif percentage >= 70:
        return f"C ({percentage:.1f}%)"
    elif percentage >= 60:
        return f"D ({percentage:.1f}%)"
    else:
        return f"F ({percentage:.1f}%)"


def get_grade_color(percentage: float) -> str:
    """
    Get color code for grade display

    Args:
        percentage: Grade percentage (0-100)

    Returns:
        Color code for Streamlit markdown
    """
    if percentage >= 90:
        return "green"
    elif percentage >= 80:
        return "blue"
    elif percentage >= 70:
        return "orange"
    elif percentage >= 60:
        return "red"
    else:
        return "darkred"


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe storage and display

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove or replace problematic characters
    import re

    # Replace problematic characters with underscores
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)

    # Trim underscores from start and end
    sanitized = sanitized.strip('_')

    return sanitized


def calculate_statistics(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate comprehensive statistics from grading results

    Args:
        results: List of grading result dictionaries

    Returns:
        Dictionary containing various statistics
    """
    if not results:
        return {}

    percentages = [result['percentage'] for result in results]

    stats = {
        'total_submissions': len(results),
        'average_score': sum(percentages) / len(percentages),
        'median_score': sorted(percentages)[len(percentages) // 2],
        'highest_score': max(percentages),
        'lowest_score': min(percentages),
        'standard_deviation': calculate_std_dev(percentages),
        'grade_distribution': calculate_grade_distribution(percentages),
        'pass_rate': sum(1 for p in percentages if p >= 60) / len(percentages) * 100
    }

    return stats


def calculate_std_dev(values: List[float]) -> float:
    """Calculate standard deviation of a list of values"""
    if len(values) <= 1:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
    return variance ** 0.5


def calculate_grade_distribution(percentages: List[float]) -> Dict[str, int]:
    """
    Calculate distribution of letter grades

    Args:
        percentages: List of percentage scores

    Returns:
        Dictionary with grade distribution
    """
    distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}

    for percentage in percentages:
        if percentage >= 90:
            distribution['A'] += 1
        elif percentage >= 80:
            distribution['B'] += 1
        elif percentage >= 70:
            distribution['C'] += 1
        elif percentage >= 60:
            distribution['D'] += 1
        else:
            distribution['F'] += 1

    return distribution


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format

    Args:
        size_bytes: File size in bytes

    Returns:
        Formatted file size string
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    else:
        return f"{size_bytes / (1024 ** 3):.1f} GB"


def validate_grading_criteria(criteria: Dict[str, int], total_marks: int) -> Dict[str, str]:
    """
    Validate custom grading criteria

    Args:
        criteria: Dictionary of criteria and their marks
        total_marks: Total marks available

    Returns:
        Dictionary of validation errors (empty if no errors)
    """
    errors = {}

    if not criteria:
        return errors

    # Check if sum exceeds total marks
    total_criteria_marks = sum(criteria.values())
    if total_criteria_marks > total_marks:
        errors['total_exceeded'] = f"Sum of criteria marks ({total_criteria_marks}) exceeds total marks ({total_marks})"

    # Check for negative values
    negative_criteria = [name for name, marks in criteria.items() if marks < 0]
    if negative_criteria:
        errors['negative_values'] = f"Negative marks not allowed for: {', '.join(negative_criteria)}"

    # Check for empty criteria names
    empty_names = [name for name in criteria.keys() if not name.strip()]
    if empty_names:
        errors['empty_names'] = "Criteria names cannot be empty"

    return errors


def create_progress_message(current: int, total: int, current_file: str) -> str:
    """
    Create a progress message for file processing

    Args:
        current: Current file number
        total: Total number of files
        current_file: Name of current file being processed

    Returns:
        Formatted progress message
    """
    percentage = (current / total) * 100 if total > 0 else 0
    return f"Processing file {current} of {total} ({percentage:.0f}%): {current_file}"


def extract_text_preview(text: str, max_length: int = 200) -> str:
    """
    Extract a preview of text content for display

    Args:
        text: Full text content
        max_length: Maximum length of preview

    Returns:
        Truncated text with ellipsis if needed
    """
    if not text:
        return "No text content available"

    # Clean up the text
    cleaned_text = ' '.join(text.split())

    if len(cleaned_text) <= max_length:
        return cleaned_text

    # Truncate and add ellipsis
    truncated = cleaned_text[:max_length].rsplit(' ', 1)[0]
    return truncated + "..."


def is_valid_api_key_format(api_key: str, service: str) -> bool:
    """
    Validate API key format for different services

    Args:
        api_key: The API key to validate
        service: The service name (deepseek, google_vision)

    Returns:
        True if format appears valid, False otherwise
    """
    if not api_key or not api_key.strip():
        return False

    # Basic validation based on known patterns
    if service.lower() == 'deepseek':
        # DeepSeek API keys typically start with 'sk-'
        return api_key.startswith('sk-') and len(api_key) > 10
    elif service.lower() == 'google_vision':
        # Google API keys are typically 39 characters
        return len(api_key) >= 30 and api_key.replace('-', '').replace('_', '').isalnum()

    return True  # Default to valid if service not recognized
