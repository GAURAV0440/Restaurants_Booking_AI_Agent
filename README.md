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

streamlit run frontend/app.py


#### Terminal Interface

python main.py

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

### Prompt Engineering Approach

The system prompt is designed to:
Control the full booking workflow step-by-step
Ask for missing details one at a time (restaurant ID → name → phone → date → time → guests)
Prevent hallucinations by forcing the agent to rely ONLY on JSON data
Ensure tool usage is always correct (search, recommend, availability check, booking, update, cancel)
Confirm user intent before final reservation
Provide friendly, consistent replies across all journeys

### Key design principles:

Slot-based conversation control
Tool calling over natural language reasoning
User detail validation
Fail-safe recovery prompts

### Example Conversations
1. Search Restaurants

User: Show me Italian restaurants
Agent: Calls search_restaurants, returns all Italian restaurants with IDs.

2. Book a Table

User: Book a table at an Italian restaurant
Agent:

Asks for restaurant ID

Asks for name

Asks for phone number

Asks for date

Asks for time

Asks for guests

Calls check_availability

Calls create_reservation

3. Modify Booking

User: Change my reservation to 8 PM
Agent: Requests reservation ID → calls update_reservation

4. Cancel Reservation

User: Cancel my booking
Agent: Requests reservation ID → calls cancel_reservation


### Business Strategy Summary
Problems GoodFoods Faces
Slow manual booking process
Overloaded staff during peak hours
Long customer wait times
No centralized analytics
High no-show rates
AI Agent Benefits
30-second booking flow
Automated seat availability checks
40% reduction in staff load
25% fewer no-shows
15–20% better table utilization
Instant, consistent customer experience
### Metrics to Track
Success rate of bookings
Tool call accuracy
Customer satisfaction
Utilization of each branch

### Assumptions
JSON files act as temporary DB (restaurants + reservations)
All restaurant data is correct and up-to-date
User provides correct name and phone number
Restaurant availability is per-time-slot
English-only communication (for now)

### Limitations
JSON-based storage → not scalable
No real-time POS or seat-sync system
No ML-based personalization
No payment or deposit workflow
Fuzzy name matching is basic

### Future Enhancements
Move to PostgreSQL / Firebase
WhatsApp & SMS reminders for no-show reduction
ML-based recommendation engine
Integrate with restaurant POS systems
Multi-language conversation support
User profile system
Analytics dashboard for managers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- Built with [Groq](https://groq.com/) for fast AI processing
- [Streamlit](https://streamlit.io/) for the web interface
- Comprehensive restaurant database with 60+ establishments


**Made with ❤️ for food lovers and restaurant enthusiasts!**
