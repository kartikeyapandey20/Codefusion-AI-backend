from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser


class AIUtility:
    def __init__(self, model_name: str = "gemini-2.0-flash", temperature: float = 0.5):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )
        self.output_parser = StrOutputParser()

    def generate_title(self, query: str) -> str:
        """
        Generates a short title for a given user query.
        """
        prompt = PromptTemplate.from_template(
            "You are an AI assistant. Generate a short, meaningful title (max 6 words) for the user's query.\n\n"
            "Query: {query}\n\n"
            "Title:"
        )
        chain = prompt | self.llm | self.output_parser
        return chain.invoke({"query": query}).strip()
