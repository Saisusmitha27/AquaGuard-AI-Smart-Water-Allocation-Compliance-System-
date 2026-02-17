import streamlit as st
from allocations import AllocationProcessor

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
        
        if question.startswith("Request:") or question.startswith("request:"):
            req = question[8:].strip() if question.startswith("Request:") else question[9:].strip()
            result, status = self.processor.process_request(req, self.drought_mode)
            
        
            if status == "approved" or status == "reduced":
                return f"**{status.upper()}**\n\n{result}", status
            elif status == "rejected":
                return f"❌ **REJECTED**\n\n{result}", status
            else:
                return f"⚠️ **ERROR**\n\n{result}", "error"

        
        try:
        
            if self.kb:
                try:
                    results = self.kb.similarity_search_with_relevance_scores(question, k=3)
                    if results and len(results) > 0:
                        relevant_docs = [doc for doc, score in results if score > 0.7]
                        if relevant_docs:
                            context = "\n\n".join([doc.page_content for doc in relevant_docs])
                            
                            if self.ollama_available:
                                from langchain_community.llms import Ollama
                                llm = Ollama(model="tinyllama")
                                prompt = f"""Based on the following water regulation documents, please answer the question.
                                If the answer cannot be found in the documents, say so.

                                Documents:
                                {context}

                                Question: {question}

                                Answer:"""
                                response = llm.invoke(prompt)
                                return response, "kb"
                            else:
                                return f"📚 From Knowledge Base:\n\n{context[:500]}...", "kb"
                except Exception as e:
                    print(f"KB error: {e}")

        
            if self.user_kb:
                try:
                    docs = self.user_kb.similarity_search(question, k=3)
                    if docs:
                        context = "\n\n".join(d.page_content for d in docs)
                        if self.ollama_available:
                            from langchain_community.llms import Ollama
                            llm = Ollama(model="tinyllama")
                            prompt = f"""Answer the question using only the context below.
                            
                            Context: {context}
                            
                            Question: {question}
                            
                            Answer:"""
                            return llm.invoke(prompt), "rag"
                        else:
                            return f"📄 From Uploaded PDF:\n\n{context[:500]}...", "rag"
                except Exception as e:
                    print(f"User KB error: {e}")

            
            if self.ollama_available:
                from langchain_community.llms import Ollama
                llm = Ollama(model="tinyllama")
                prompt = f"""You are AquaGuard, a helpful water allocation assistant. 
                Answer the following question in a friendly, conversational way.
                
                Question: {question}
                
                Answer:"""
                return llm.invoke(prompt), "llm"
            else:
                return "I'm here to help with water allocation requests. You can ask me about water regulations or submit a request in the format: `Request: Region: id, Population: pop, Sector: sec, Volume: vol, Cycle: cyc`", "offline"
                
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}", "error"
    
    def render_chat(self):
        
        for msg in self.water_alloc.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "source" in msg:
                    source_icons = {
                        "kb": "📚 *Source: Knowledge Base*",
                        "rag": "📄 *Source: Uploaded PDF*",
                        "rejected": "❌ *Request Rejected*",
                        "approved": "✅ *Request Approved*",
                        "reduced": "⚠️ *Request Reduced*",
                        "llm": "🤖 *Source: AI Assistant*",
                        "offline": "💻 *Offline Mode*",
                        "error": "⚠️ *Error*"
                    }
                    icon_text = source_icons.get(msg["source"], "💬 Response")
                    st.caption(icon_text)

        
        prompt = st.chat_input("Submit request or ask a question...")
        
        if prompt:
            
            self.water_alloc.messages.append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)

        
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    answer, source = self.hybrid_query(prompt)
                    
                    
                    if source in ["approved", "reduced", "rejected"]:
                        if source == "approved":
                            st.success(answer)
                        elif source == "reduced":
                            st.warning(answer)
                        else:
                            st.error(answer)
                    else:
                        st.markdown(answer)

            
            self.water_alloc.messages.append({
                "role": "assistant",
                "content": answer if source in ["approved", "reduced", "rejected", "error"] else answer,
                "source": source
            })
            
            st.rerun()
