import streamlit as st

class ChatBot:
    def __init__(self, kb, user_kb, water_alloc, drought_mode, ollama_available=True):
        self.kb = kb
        self.user_kb = user_kb
        self.water_alloc = water_alloc
        self.drought_mode = drought_mode
        self.ollama_available = ollama_available
        from allocations import AllocationProcessor
        self.processor = AllocationProcessor(water_alloc)
        
    def hybrid_query(self, question):
        if question.startswith("Request:"):
            req = question[8:].strip()
            return self.processor.process_request(req, self.drought_mode)

        # Try KB first
        if self.kb:
            try:
                results = self.kb.similarity_search_with_relevance_scores(question, k=1)
                if results and len(results[0]) > 1 and results[0][1] > 0.7:
                    return results[0][0].page_content, "kb"
            except Exception as e:
                pass

        # Try user uploaded KB
        if self.user_kb:
            try:
                docs = self.user_kb.similarity_search(question, k=3)
                if docs:
                    context = "\n\n".join(d.page_content for d in docs)
                    if self.ollama_available:
                        from langchain_community.llms import Ollama
                        llm = Ollama(model="tinyllama")
                        prompt = f"Answer using this context: {context}\nQuestion: {question}"
                        return llm.invoke(prompt), "rag"
                    else:
                        return f"Found in document: {context[:500]}...", "rag"
            except Exception as e:
                pass

        # Fallback to LLM or simple response
        if self.ollama_available:
            try:
                from langchain_community.llms import Ollama
                llm = Ollama(model="tinyllama")
                return llm.invoke(question), "llm"
            except:
                return "I couldn't find an answer in the knowledge base. Please try a different question or upload relevant PDFs.", "error"
        else:
            return "I'm running in offline mode. Please upload PDFs with relevant information or install Ollama for AI responses.", "offline"
    
    def render_chat(self):
        # Display chat messages
        for msg in self.water_alloc.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "source" in msg:
                    source_icons = {
                        "kb": "📚 From Knowledge Base",
                        "rag": "📄 From Uploaded PDF",
                        "rejected": "❌ Request Rejected",
                        "approved": "✅ Request Approved",
                        "llm": "🤖 From AI",
                        "offline": "💻 Offline Mode",
                        "error": "⚠️ Information"
                    }
                    icon_text = source_icons.get(msg["source"], "💬 Response")
                    st.caption(icon_text)

        # Chat input
        prompt = st.chat_input("Submit request (Format: Region: id, Population: pop, Sector: sec, Volume: vol, Cycle: cyc) or ask a question...")
        
        if prompt:
            # Add user message
            self.water_alloc.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response
            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    answer, source = self.hybrid_query(prompt)
                    st.markdown(answer)

            # Add assistant message
            self.water_alloc.messages.append({
                "role": "assistant",
                "content": answer,
                "source": source
            })
            
            st.rerun()