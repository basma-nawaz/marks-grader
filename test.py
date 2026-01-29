
import text_parser

def run_tests():
    print("---- Running Tests for text_parser.py ----\n")

    # Test 1: Roll number extraction
    text1 = "Name: Ali\nRoll: 123456\nQ1. What is AI?\nAI stands for Artificial Intelligence."
    roll = text_parser.extract_roll_number(text1)
    print("Test 1 - Extract Roll Number:", roll)
    assert roll == "123456", "❌ Roll number extraction failed!"

    # Test 2: Split questions
    questions = text_parser.split_questions(text1)
    print("\nTest 2 - Split Questions:", questions)
    assert questions[0][0] == "1" and "AI stands for" in questions[0][1], "❌ Question splitting failed!"

    # Test 3: Clean text
    messy_text = "   This is \n a  test\t\tstring. "
    clean = text_parser.clean_text(messy_text)
    print("\nTest 3 - Clean Text:", clean)
    assert clean == "This is a test string.", "❌ Clean text failed!"

    # Test 4: Extract student answers
    student_data = text_parser.extract_student_answers(text1)
    print("\nTest 4 - Extract Student Answers:", student_data)
    assert student_data["roll_number"] == "123456", "❌ Extract student data failed!"

    # Test 5: Format rubric
    rubric = {"syntax": 2, "logic": 3}
    formatted = text_parser.format_rubric(rubric)
    print("\nTest 5 - Format Rubric:\n", formatted)
    assert "- Syntax: 2 marks" in formatted and "- Logic: 3 marks" in formatted, "❌ Rubric formatting failed!"

    # Test 6: Merge pages
    pages = ["Page 1 content.", "Page 2 content."]
    merged = text_parser.merge_pages(pages)
    print("\nTest 6 - Merge Pages:\n", merged)
    assert "Page 1 content." in merged and "Page 2 content." in merged, "❌ Page merging failed!"

    # Test 7: Parse questions (dict format)
    parsed_qs = text_parser.parse_text_to_questions(text1)
    print("\nTest 7 - Parse Text to Questions:", parsed_qs)
    assert "Q1" in parsed_qs, "❌ Question dict parsing failed!"

    # Test 8: Parse full text
    questions, student = text_parser.parse_text_to_questions_and_answers(text1)
    print("\nTest 8 - Parse Text to Questions and Answers:")
    print("Questions:", questions)
    print("Student:", student)
    assert student["roll_number"] == "123456", "❌ Combined parsing failed!"

    print("\n✅ All tests passed successfully!")

if __name__ == "__main__":
    run_tests()
