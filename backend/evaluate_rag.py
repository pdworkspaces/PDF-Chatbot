
from backend.graph.rag_graph import ask_pdf


DOCUMENT_ID = "test_document_001"

evaluation_data = [
    {
        "question": "How many annual leave days are provided?",
        "expected": "20 working days",
        "expected_page": 3
    },
    {
        "question": "How many sick leave days are provided?",
        "expected": "10 working days",
        "expected_page": 3
    },
    {
        "question": "What is the carry-forward leave limit?",
        "expected": "5 days",
        "expected_page": 3
    },
    {
        "question": "What are the standard working hours?",
        "expected": "9:30 AM to 6:00 PM",
        "expected_page": 3
    },
    {
        "question": "What is the notice period?",
        "expected": "30 calendar days",
        "expected_page": 5
    },
    {
        "question": "When are salaries normally paid?",
        "expected": "last working day",
        "expected_page": 4
    }
]


def evaluate_rag():

    total = len(evaluation_data)
    passed = 0

    print("\n========== RAG EVALUATION ==========")

    for index, test in enumerate(evaluation_data, start=1):

        question = test["question"]
        expected = test["expected"]
        expected_page = test["expected_page"]

        print(f"\nTest {index}")
        print("Question:", question)

        try:
            result = ask_pdf(
                question=question,
                document_id=DOCUMENT_ID,
                provider="ollama"
            )

            answer = result["answer"]
            source_pages = result["source_pages"]

            answer_correct = expected.lower() in answer.lower()
            source_correct = expected_page in source_pages

            if answer_correct and source_correct:
                passed += 1
                status = "PASS"
            else:
                status = "FAIL"

            print("Expected:", expected)
            print("Actual:", answer)
            print("Source pages:", source_pages)
            print("Answer check:", answer_correct)
            print("Source check:", source_correct)
            print("Result:", status)

        except Exception as error:
            print("Error:", error)
            print("Result: ERROR")

    failed = total - passed
    pass_rate = (passed / total) * 100 if total else 0

    print("\n========== FINAL REPORT ==========")
    print("Total tests:", total)
    print("Passed:", passed)
    print("Failed:", failed)
    print("Pass rate:", round(pass_rate, 2), "%")


if __name__ == "__main__":
    evaluate_rag()
