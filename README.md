# LLM Chatbot with Tool Calling

This project is a sophisticated LLM chatbot that demonstrates the power of "Tool Calling" with the Google Generative AI library. The chatbot can fetch live weather data from the OpenWeatherMap API and stock prices from the Alpha Vantage API to answer user queries with real-time information.

## Features

- **Advanced Tool Calling**: The chatbot intelligently uses external tools to gather real-time information.
- **Multiple Data Sources**: Supports both weather information and stock price data.
- **Robust Error Handling**: Comprehensive error handling for API calls, network issues, and invalid inputs.
- **Extensible Architecture**: Easily add new tools to the `tools.py` module to extend the chatbot's capabilities.
- **Secure Configuration**: API keys are managed securely using a `.env` file.
- **Type Hints**: Full type hinting for better code maintainability and developer experience.

## Project Structure

```
.
├── .env
├── .env_template
├── main.py
├── README.md
├── requirements.txt
├── streamlit_app.py
├── tools.py
└── .gitignore
```

- **`main.py`**: The main entry point for the command-line chatbot. It handles the chat loop, user input, and orchestrates the interaction with the Gemini model and the tools.
- **`streamlit_app.py`**: A web-based version of the chatbot built with Streamlit, providing a user-friendly interface.
- **`tools.py`**: Contains the Python functions that the LLM can call. Each function has a detailed docstring explaining its purpose, arguments, and return value.
- **`requirements.txt`**: Lists the necessary Python dependencies for the project.
- **`.env`**: A file to store your API keys. You will need to create this file and add your own keys.
- **`.env_template`**: Template showing the required environment variables.
- **`.gitignore`**: Excludes sensitive files and environment-specific files from version control.
- **`README.md`**: This file, providing setup and usage instructions.

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create a Virtual Environment

It is highly recommended to use a virtual environment to manage the project's dependencies.

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Get API Keys

- **Gemini API Key:**
  - Go to the [Google AI Studio](https://aistudio.google.com/app/apikey) to get your API key.

- **OpenWeatherMap API Key:**
  - Sign up for a free account on [OpenWeatherMap](https://openweathermap.org/api).
  - Go to your account's "API keys" tab to find your key.

- **Alpha Vantage API Key (Optional):**
  - Sign up for a free account on [Alpha Vantage](https://www.alphavantage.co/support/#api-key).
  - You'll receive a free API key instantly via email.

### 5. Configure Environment Variables

Create a file named `.env` in the root of the project directory and add your API keys as follows:

```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
WEATHER_API_KEY=YOUR_WEATHER_API_KEY
ALPHA_VANTAGE_API_KEY=YOUR_ALPHA_VANTAGE_API_KEY
```

Replace `YOUR_GEMINI_API_KEY`, `YOUR_WEATHER_API_KEY`, and `YOUR_ALPHA_VANTAGE_API_KEY` with your actual API keys.

> **Note**: If you don't want to use the stock price feature, you can leave the `ALPHA_VANTAGE_API_KEY` unset or remove it. The chatbot will still work with weather data.

## Usage

### Command-Line Version

To run the command-line chatbot, execute the `main.py` script:

```bash
python main.py
```

The chatbot will initialize, and you can start asking it about the weather or stock prices. For example:

```
You: What's the weather like in London?
Chatbot: The weather in London is currently clear sky with a temperature of 15.6°C.

You: What is the stock price for AAPL?
Chatbot: The current stock price for AAPL is $175.42 USD.
```

To exit the chatbot, simply type `exit`, `quit`, or `bye`.

### Streamlit Web App

To run the Streamlit web application, execute:

```bash
streamlit run streamlit_app.py
```

This will open a web interface in your browser where you can interact with the chatbot through a user-friendly UI. The web app features:

- Real-time chat interface with message history
- Tool usage indicators showing when external APIs are called
- Error handling with user-friendly messages
- Responsive design that works on desktop and mobile
- Sidebar with instructions and configuration information

The web app provides the same functionality as the command-line version but with a more accessible interface.

## How It Works

The project includes both a command-line version (`main.py`) and a web-based version (`streamlit_app.py`), both implementing the same core functionality:

1. **Initialization**: The application initializes the Gemini model and provides it with the `get_weather` and `get_stock_price` functions from the `tools.py` module as tools it can use.
2. **User Input**: The user provides a query about weather or stock prices.
3. **Model Inference**: The user's message is sent to the Gemini model.
4. **Tool Calling**: If the model determines that it needs to use one of the tools to answer the user's query, it will issue a "function call".
5. **Tool Execution**: The application catches this function call, executes the corresponding Python function (`get_weather` or `get_stock_price`), and captures the output.
6. **Response Generation**: The output from the tool is sent back to the model, which then uses that information to generate a natural language response for the user.
7. **Output**: The final response is displayed to the user (either in console or web interface).

## Extending the Chatbot

Adding new tools to the chatbot is straightforward:

1. Define a new function in `tools.py` with a detailed docstring explaining when and how it should be used.
2. Import the function in `main.py`.
3. Add the function to the tools list when initializing the model.

For example:
```python
def get_news(topic: str) -> Dict[str, Any]:
    """
    Fetches the latest news headlines for a given topic.

    This function should be used when the user asks for recent news about a specific topic.

    Args:
        topic: The topic for which to fetch news headlines.

    Returns:
        A dictionary containing news information.
    """
    # Implementation here
```

Then add it to the model initialization:
```python
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    tools=[get_weather, get_stock_price, get_news]
)
```

## Error Handling

The chatbot includes comprehensive error handling:

- **API Key Issues**: Checks for missing or invalid API keys
- **Network Errors**: Handles connection problems and timeouts
- **Invalid Inputs**: Manages incorrect city names or stock symbols
- **API Limitations**: Responds appropriately to rate limits
- **General Exceptions**: Catches unexpected errors gracefully

## Security Considerations

- API keys are loaded from environment variables and never hardcoded
- The `.env` file is excluded from version control via `.gitignore`
- All external API calls are validated and sanitized
- Error messages avoid exposing sensitive information

## License

This project is open source and available under the MIT License.