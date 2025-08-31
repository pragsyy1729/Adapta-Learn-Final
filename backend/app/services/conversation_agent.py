import os
import ast
import asyncio
from typing import List, Dict, Any
from langchain.schema import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chat_models import init_chat_model
from .document_processor import document_processor
from langchain_groq import ChatGroq
from transformers import AutoModel
from sentence_transformers import SentenceTransformer
model_name = "BAAI/bge-small-en-v1.5"  
model = SentenceTransformer(model_name)

class ConversationAgent:
    def __init__(self):
        self.llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0)
        self.embeddings = model

    def get_department_vector_store(self, department_id: str) -> FAISS:
        """Get vector store for a specific department."""
        print(f"DEBUG: Getting vector store for department: {department_id}")
        return document_processor.get_vector_store(department_id)

    def search_by_chunks(self, query: str, department_id: str, k: int = 3) -> List[str]:
        """Search for relevant chunks in department's vector store."""
        try:
            vector_store = self.get_department_vector_store(department_id)
            results = vector_store.similarity_search_with_score(query=query, k=k)

            chunks = []
            for result in results:
                doc = result[0]
                # Accept any document type, not just "chunk"
                if doc.page_content and len(doc.page_content.strip()) > 0:
                    chunks.append(doc.page_content)

            print(f"DEBUG: Found {len(chunks)} chunks for query: {query[:50]}...")
            return chunks
        except Exception as e:
            print(f"Error searching chunks: {e}")
            return []

    def search_by_nodes(self, keywords: List[str], department_id: str, k: int = 2) -> List[str]:
        """Search for relevant nodes in department's vector store."""
        try:
            vector_store = self.get_department_vector_store(department_id)
            chunks = []

            for keyword in keywords:
                results = vector_store.similarity_search_with_score(query=keyword, k=k)
                for result in results:
                    doc = result[0]
                    # Accept any document with content
                    if doc.page_content and len(doc.page_content.strip()) > 0:
                        chunks.append(doc.page_content)

            return list(set(chunks))  # Remove duplicates
        except Exception as e:
            print(f"Error searching nodes: {e}")
            return []

    def search_by_relationships(self, keywords: List[str], department_id: str, k: int = 2) -> List[str]:
        """Search for relevant relationships in department's vector store."""
        try:
            vector_store = self.get_department_vector_store(department_id)
            chunks = []

            # Create relationship patterns
            relationships = [f"{keywords[i].lower()} -> {keywords[i+1].lower()}"
                           for i in range(len(keywords)-1)]

            for relationship in relationships:
                results = vector_store.similarity_search_with_score(query=relationship, k=k)
                for result in results:
                    doc = result[0]
                    # Accept any document with content
                    if doc.page_content and len(doc.page_content.strip()) > 0:
                        chunks.append(doc.page_content)

            return list(set(chunks))  # Remove duplicates
        except Exception as e:
            print(f"Error searching relationships: {e}")
            return []

    def extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from user query using LLM."""
        try:
            keyword_extract_prompt = f"""
            Role - You are an expert in extracting keywords from a given text. Your task is to extract the keywords from the provided text.
            Just return the keywords in a list format like ['keyword1', 'keyword2', 'keyword3']. Don't return it as JSON.

            Input: {query}
            """

            response = self.llm.invoke(keyword_extract_prompt)
            keywords = ast.literal_eval(response.content.strip())
            return [keyword.lower() for keyword in keywords if keyword]
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            # Fallback: simple keyword extraction
            return [word.lower() for word in query.split() if len(word) > 3]

    def get_relevant_chunks(self, query: str, department_id: str) -> List[str]:
        """Get all relevant chunks for a query from department's documents."""
        print(f"DEBUG: Getting relevant chunks for department: {department_id}")
        
        keywords = self.extract_keywords(query)
        print(f"DEBUG: Extracted keywords: {keywords}")

        chunks = []
        
        # Try different search strategies
        try:
            # Primary search: direct query similarity
            direct_chunks = self.search_by_chunks(query, department_id, k=5)
            chunks.extend(direct_chunks)
            print(f"DEBUG: Direct search found {len(direct_chunks)} chunks")
        except Exception as e:
            print(f"DEBUG: Direct search failed: {e}")
        
        try:
            # Secondary search: keyword-based
            if keywords:
                keyword_chunks = self.search_by_nodes(keywords, department_id, k=3)
                chunks.extend(keyword_chunks)
                print(f"DEBUG: Keyword search found {len(keyword_chunks)} chunks")
        except Exception as e:
            print(f"DEBUG: Keyword search failed: {e}")
        
        try:
            # Tertiary search: relationship-based
            if len(keywords) > 1:
                relationship_chunks = self.search_by_relationships(keywords, department_id, k=2)
                chunks.extend(relationship_chunks)
                print(f"DEBUG: Relationship search found {len(relationship_chunks)} chunks")
        except Exception as e:
            print(f"DEBUG: Relationship search failed: {e}")

        # Remove duplicates while preserving order
        seen = set()
        unique_chunks = []
        for chunk in chunks:
            if chunk not in seen and len(chunk.strip()) > 50:  # Filter out very short chunks
                seen.add(chunk)
                unique_chunks.append(chunk)

        print(f"DEBUG: Total unique chunks found: {len(unique_chunks)}")
        return unique_chunks

    def summarize_chunks(self, chunks: List[str]) -> str:
        """Summarize relevant chunks for context."""
        if not chunks:
            return "No relevant information found in the department documents."

        text = "\n".join(chunks)

        summarize_prompt = f"""
        Role - You are a summarization expert. Your task is to summarize the provided text in a concise and informative manner.

        Here are the key points to consider while summarizing:
        1. Identify key concepts and ideas from the text.
        2. Summarize content around these key concepts, avoiding unnecessary details.
        3. Include all important numbers and quantitative data from the text.
        4. Keep the summary focused and relevant to potential questions.

        Input text: {text}

        Summary:
        """

        try:
            response = self.llm.invoke(summarize_prompt)
            return response.content
        except Exception as e:
            print(f"Error summarizing chunks: {e}")
            return text[:1000] + "..." if len(text) > 1000 else text

    def answer_question(self, context: str, question: str, department_name: str) -> str:
        """Answer user question based on department context."""
        qa_prompt = f"""Role - You are an experienced person in a banking organization who is going to act as an Onboarding Mentor for New Joiners in the {department_name} department. Your task is to answer the question based on the context provided.

        Here's how you should format your response:
        1. The response should be concise and informative.
        2. Make sure the New Joiner's curiosity is intrigued by providing relevant details.
        3. Format your response in a structured manner with clear sections if needed.
        4. Don't overly simplify the answer, but also don't explain too much unnecessary detail.
        5. If there are any numbers or statistics, make sure to include them.
        6. If the context doesn't contain enough information to fully answer, acknowledge this and provide what information is available.

        Context from {department_name} documents: {context}

        Question: {question}

        Answer:"""

        try:
            response = self.llm.invoke(qa_prompt)
            return response.content
        except Exception as e:
            print(f"Error answering question: {e}")
            return "I'm sorry, I encountered an error while processing your question. Please try again."

    def process_question(self, question: str, department_id: str, department_name: str) -> Dict[str, Any]:
        """Main method to process a user question and return an answer."""
        print(f"DEBUG: Processing question for department_id: {department_id}, department_name: {department_name}")
        try:
            # Get relevant chunks
            relevant_chunks = self.get_relevant_chunks(question, department_id)

            if not relevant_chunks:
                print(f"WARNING: No relevant chunks found for department {department_id}")
                return {
                    "answer": f"I don't have specific documentation for the {department_name} department yet. However, I can help you with general onboarding questions or guide you to the right resources. Here are some common topics I can assist with:\n\n• General onboarding processes\n• Learning path recommendations\n• Department overview\n• Best practices for new joiners\n\nPlease ask me a specific question, or contact your manager to have department-specific documents uploaded to our knowledge base.",
                    "chunks_found": 0,
                    "department": department_name
                }

            print(f"SUCCESS: Found {len(relevant_chunks)} relevant chunks")
            
            # Summarize chunks for context
            context = self.summarize_chunks(relevant_chunks)
            print(f"DEBUG: Context summary length: {len(context)} characters")

            # Generate answer
            answer = self.answer_question(context, question, department_name)
            print(f"DEBUG: Generated answer length: {len(answer)} characters")

            return {
                "answer": answer,
                "chunks_found": len(relevant_chunks),
                "department": department_name,
                "context_summary": context[:200] + "..." if len(context) > 200 else context
            }

        except Exception as e:
            print(f"Error processing question: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return {
                "answer": "I'm sorry, I encountered an error while processing your question. Please try again.",
                "chunks_found": 0,
                "department": department_name,
                "error": str(e)
            }

# Global conversation agent instance
conversation_agent = ConversationAgent()
