
from langchain_community.chat_message_histories import PostgresChatMessageHistory
# from langchain.memory import ConversationSummaryMemory
from langchain_openai import ChatOpenAI
from app.core.config import settings
from .function_registry import FunctionRegistry
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from app.core.logging import logger
import json
# import asyncio
from langchain.memory import ConversationSummaryBufferMemory

class ChatService:
    def __init__(self, session_id: str):
        if not session_id:
            raise ValueError("Session ID cannot be empty")
        self.session_id = session_id
        self.history = PostgresChatMessageHistory(
            connection_string=settings.DATABASE_URL,
            session_id=session_id
        )
        
        self.summary_llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini", 
            temperature=0
        )
        
        self.memory = ConversationSummaryBufferMemory(
            llm=self.summary_llm,
            chat_memory=self.history,
            return_messages=True,
            memory_key="chat_history",
            max_token_limit=1000,
            # moving_summary_buffer=True,
            summary_message_limit=5  # Summarize after 5 messages
        )
        
        self.llm = ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model="gpt-4o-mini",
            temperature=0.7
        )

    async def get_context_messages(self, limit: int = 10):
        """Get recent messages with summary context"""
        try:
            messages = self.memory.chat_memory.messages or []
            # Use buffer instead of moving_summary_buffer
            summary = self.memory.buffer
            
            if summary and len(messages) > limit:
                summary_message = SystemMessage(content=f"Previous conversation summary: {summary}")
                recent_messages = messages[-limit:] if messages else []
                return [summary_message] + recent_messages
            
            return messages[-limit:] if messages else []
        except Exception as e:
            logger.error(f"Error getting context messages: {str(e)}")
            return []

    async def process_message(self, message: str):
        try:
            # Store user message and update summary
            self.memory.save_context(
                {"input": message},
                {"output": ""}  # Will be updated with AI response later
            )

            # Get existing functions
            logger.info(f"Processing message: {message}")
            functions = FunctionRegistry.get_function_descriptions()
            
            messages = [
                SystemMessage(content="You are a helpful assistant. Use available functions when needed. Be concise."),
                # *recent_messages,
                *self.memory.chat_memory.messages,
                HumanMessage(content=message)
            ]
            
            logger.info(f"Sending messages to LLM with context and summary")
            response = await self.llm.ainvoke(
                messages,
                functions=functions,
                function_call="auto"
            )
            if response is None:  # Add validation
                raise ValueError("LLM returned None response")
            logger.info(f"LLM Response: {response}")
            
            if response.additional_kwargs.get('function_call'):
                try:
                    function_call = response.additional_kwargs['function_call']
                    function_name = function_call['name']
                    function_args = json.loads(function_call['arguments'])
                    
                    logger.info(f"Executing function {function_name} with args: {function_args}")
                    result = await FunctionRegistry.execute_function(function_name, **function_args)
                    logger.info(f"Function result: {result}")
                    
                    # Update memory with function result
                    self.memory.save_context(
                        {"input": message},
                        {"output": f"Function {function_name} result: {result}"}
                    )
                    
                    return {
                        "message": str(result),
                        "function_call": {
                            "name": function_name,
                            "result": result
                        }
                    }
                except Exception as e:
                    error_msg = f"Error executing function: {str(e)}"
                    logger.error(error_msg)
                    await self.memory.save_context(
                        {"input": message},
                        {"output": error_msg}
                    )
                    return {"message": error_msg, "function_call": None}
            
            # Handle normal response
            self.memory.save_context(
                {"input": message},
                {"output": response.content}
            )
            return {
                "message": response.content,
                "function_call": None
            }
            
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)