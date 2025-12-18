import os
import google.generativeai as genai
from dotenv import load_dotenv
from tools import get_weather, get_stock_price
from typing import Dict, Any, List
import json

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file. Please add it.")

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
    """
    The main function for the chatbot. It handles the chat loop, user input,
    and the integration with the Gemini model for function calling.
    """
    # Create the generative model with tools
    model = genai.GenerativeModel(
        model_name="gemini-1.5-pro-latest",
        tools=[get_weather, get_stock_price]
    )

    # Start a chat session
    chat = model.start_chat()

    print("LLM Chatbot with Tool Calling initialized!")
    print("I can help you with:")
    print("- Weather information (ask about weather in any city)")
    print("- Stock prices (ask about stock prices for companies)")
    print("Type 'exit' or 'quit' to end the conversation.\n")

    while True:
        # Get user input
        user_input = input("You: ").strip()

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("Chatbot: Goodbye! Have a great day!")
            break

        if not user_input:
            print("Chatbot: Please enter a message.")
            continue

        try:
            # Send the user's message to the model
            response = chat.send_message(user_input)

            # Print the initial response from the model
            print(f"\nChatbot: ", end="")

            # Process the response
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'text') and part.text:
                        print(part.text, end="")

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

                        print(f"\n[Calling tool: {function_name} with args: {args_dict}]")

                        # Call the tool function
                        tool_result = call_tool(function_name, args_dict)

                        print(f"[Tool result: {tool_result}]")

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

                        # Print the final response from the model after processing tool result
                        if second_response.candidates and second_response.candidates[0].content.parts:
                            print("\nChatbot: ", end="")
                            for part in second_response.candidates[0].content.parts:
                                if hasattr(part, 'text') and part.text:
                                    print(part.text, end="")

                        print("\n")  # Extra newline for readability
                        continue  # Skip the normal response printing since we handled it above

            print("\n")  # Extra newline for readability

        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again.\n")


if __name__ == "__main__":
    main()