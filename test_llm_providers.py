from backend.services.llm_service import get_llm

question = "Explain RAG in three simple sentences."

providers = ["ollama", "gemini"]

for provider in providers:

    print("\n" + "=" * 50)
    print(f"Testing provider: {provider.upper()}")
    print("=" * 50)

    try:
        llm = get_llm(provider)

        response = llm.invoke(question)

        print("\nSUCCESS")
        print("Answer:")
        print(response.content)

    except Exception as error:
        print("\nFAILED")
        print("Error:", str(error))