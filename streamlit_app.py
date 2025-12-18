import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from tools import get_weather, get_stock_price
from typing import Dict, Any
import os

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found in .env file. Please add it.")
    st.stop()

genai.configure(api_key=api_key)

def call_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calls the appropriate tool function based on the tool name.

    Args:
        tool_name: Name of the tool to call (e.g., 'get_weather', 'get_stock_price')
        args: Arguments to pass to the tool function

    Returns:
        Result from the tool function
    """
    if tool_name == "get_weather":
        return get_weather(args.get("city"))
    elif tool_name == "get_stock_price":
        return get_stock_price(args.get("symbol"))
    else:
        return {
            "error": f"Unknown tool: {tool_name}. Available tools: get_weather, get_stock_price"
        }

def main():
    st.set_page_config(
        page_title="LLM Chatbot with Tool Calling",
        page_icon="🤖",
        layout="wide"
    )

    st.title("🤖 LLM Chatbot with Tool Calling")
    st.caption("Powered by Google Gemini and external APIs")

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Sidebar with instructions
    with st.sidebar:
        st.header("📚 Instructions")
        st.write("""
        This chatbot can help you with:
        - Weather information (ask about weather in any city)
        - Stock prices (ask about stock prices for companies)

        Examples:
        - "What's the weather like in London?"
        - "What is the stock price for AAPL?"
        - "Show me the weather in New York"
        """)

        st.divider()

        st.header("⚙️ Configuration")
        st.write("Make sure your API keys are properly configured in the .env file.")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about weather, stock prices, or anything else..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                # Create the generative model with tools
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    tools=[get_weather, get_stock_price]
                )

                # Start a chat session with the history
                chat = model.start_chat(history=st.session_state.chat_history[:-1])  # Exclude current user message

                # Send the user's message to the model
                response = chat.send_message(prompt)

                # Process the response
                if response.candidates and response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if hasattr(part, 'text') and part.text:
                            full_response += part.text
                            message_placeholder.markdown(full_response + "▌")

                        # Check if the model wants to call a tool
                        elif hasattr(part, 'function_call'):
                            # Extract function name and arguments
                            function_call = part.function_call
                            function_name = function_call.name

                            # Convert proto to dict for arguments
                            args_dict = {}
                            if function_call.args:
                                # Convert protobuf Struct to regular dict
                                for key, value in function_call.args.items():
                                    args_dict[key] = value

                            # Show tool call in chat
                            tool_call_msg = f"🔍 Calling tool: {function_name} with args: {args_dict}"
                            full_response += f"\n{tool_call_msg}\n"
                            message_placeholder.markdown(full_response + "▌")

                            # Call the tool function
                            tool_result = call_tool(function_name, args_dict)

                            # Show tool result
                            tool_result_msg = f"📊 Tool result: {tool_result}"
                            full_response += f"\n{tool_result_msg}\n"
                            message_placeholder.markdown(full_response + "▌")

                            # Send the tool's response back to the model
                            second_response = chat.send_message(
                                genai.protos.Content(
                                    parts=[
                                        genai.protos.Part(
                                            function_response=genai.protos.FunctionResponse(
                                                name=function_name,
                                                response=tool_result
                                            )
                                        )
                                    ]
                                )
                            )

                            # Process the final response from the model after processing tool result
                            if second_response.candidates and second_response.candidates[0].content.parts:
                                for part in second_response.candidates[0].content.parts:
                                    if hasattr(part, 'text') and part.text:
                                        full_response += part.text
                                        message_placeholder.markdown(full_response + "▌")

                # Remove the cursor
                message_placeholder.markdown(full_response)

            except Exception as e:
                error_msg = f"An error occurred: {str(e)}"
                full_response = error_msg
                message_placeholder.error(error_msg)

        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.session_state.chat_history.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()