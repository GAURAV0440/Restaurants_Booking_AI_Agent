# 🍽️ Restaurant Booking AI Agent

An intelligent restaurant reservation system powered by AI that helps users find and book tables at restaurants across 40+ cuisines worldwide.

## ✨ Features

- **Multi-Cuisine Support**: Search across 40+ international cuisines including Italian, Indian, Japanese, Chinese, Mexican, Turkish, Thai, and many more
- **Intelligent Search**: Natural language processing for restaurant discovery
- **Comprehensive Booking Flow**: Step-by-step reservation process with validation
- **Real-time Availability**: Check table availability before booking
- **Fuzzy Name Matching**: Find restaurants even with partial or approximate names
- **Phone Number Validation**: International phone number format support
- **Error Handling**: Robust error recovery and fallback systems
- **Web Interface**: User-friendly Streamlit frontend
- **Session Management**: Clean booking sessions with no memory leakage

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Groq API key

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/GAURAV0440/Restaurants_Booking_AI_Agent.git
   cd Restaurants_Booking_AI_Agent
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

### Running the Application

#### Web Interface (Streamlit)
```bash
streamlit run frontend/app.py
```

#### Terminal Interface
```bash
python main.py
```

## 🏗️ Project Structure

```
restaurant-agent/
├── agent/
│   ├── __init__.py
│   ├── llm.py              # Core AI agent logic
│   ├── prompts.py          # System prompts and behavior rules
│   ├── router.py           # Tool execution handler
│   ├── tools.py            # Restaurant operations
│   └── tools_schema.py     # Tool definitions
├── data/
│   ├── restaurants.json    # Restaurant database (60 restaurants)
│   └── reservations.json   # Booking records
├── frontend/
│   └── app.py             # Streamlit web interface
├── main.py                # Terminal interface
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🛠️ How It Works

### 1. Restaurant Search
```
User: "Show me Italian restaurants"
Agent: [Displays list of Italian restaurants with details]
```

### 2. Booking Process
1. **Restaurant Selection**: Choose from search results
2. **Name Collection**: Provide full name
3. **Phone Number**: International format (+country-code)
4. **Date Selection**: DD-MM-YYYY format
5. **Time Selection**: Preferred dining time
6. **Availability Check**: Real-time table availability
7. **Confirmation**: Final booking confirmation
8. **Reservation Creation**: Booking confirmed with details

### 3. Supported Cuisines

Italian • Indian • Chinese • Japanese • Mexican • Thai • French • Korean • Greek • Turkish • Vietnamese • Brazilian • Lebanese • Ethiopian • German • American • Spanish • Mediterranean • Moroccan • Caribbean • Russian • Persian • African • Nepalese • Indonesian • Cuban • Swedish • Austrian • Irish • Polish • Syrian • Ukrainian • Continental • Steakhouse • Vegetarian • Barbecue • Seafood • Fast Food • Desserts • Healthy • Mughlai

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key for AI processing

### Customization
- **Add Restaurants**: Edit `data/restaurants.json`
- **Modify Prompts**: Update `agent/prompts.py`
- **Extend Tools**: Add functions to `agent/tools.py`

## 📊 API Tools

The agent uses several tools for restaurant operations:

- `search_restaurants`: Find restaurants by cuisine/location
- `find_restaurant_by_name`: Locate specific restaurants
- `check_availability`: Verify table availability
- `create_reservation`: Complete booking process
- `cancel_reservation`: Cancel existing bookings
- `update_reservation`: Modify booking details

## 🔒 Error Handling

- **Malformed Requests**: Automatic fallback detection
- **API Failures**: Graceful error recovery
- **Invalid Data**: Comprehensive validation
- **Session Issues**: Clean state management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Groq](https://groq.com/) for fast AI processing
- [Streamlit](https://streamlit.io/) for the web interface
- Comprehensive restaurant database with 60+ establishments


**Made with ❤️ for food lovers and restaurant enthusiasts!**
