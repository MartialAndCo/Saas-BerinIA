from utils.llm import ask_gpt_4_1

def test_prompt_gpt():
    prompt = "Donne-moi une niche B2B pertinente pour une entreprise qui installe des chatbots et des répondeurs IA."
    result = ask_gpt_4_1(prompt)
    assert "niche" in result or "text" in result 