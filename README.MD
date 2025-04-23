

# University Admissions Counseling Chatbot System

This project utilizes the OpenAI Agents SDK to build a multi-agent chatbot system that supports prospective students in exploring university admissions information. The system consists of multiple specialized agents working together to deliver accurate guidance on academic programs, admission requirements, and application processes.



## System Architecture

The multi-agent system includes:


### Agent Setup

```python
product_agent = Agent(
    name="product",
    instructions=PRODUCT_INSTRUCTION,
    tools=[rag]
)

shop_information_agent = Agent(
    name="shop_information",
    instructions=SHOP_INFORMATION_INSTRUCTION,
    tools=[get_shop_information]
)

manager_agent = Agent(
    name="manager",
    instructions=MANAGER_INSTRUCTION,
    handoffs=[
        handoff(
            product_agent,
            input_filter=custom_input_filter,
        ),
        shop_information_agent
    ]
)
```

## Installation & Setup

### Prerequisites
Ensure you have Python installed and then install the required dependencies:

```sh
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

### Setting Up RAG Data
Run the following command to set up data for retrieval-augmented generation (RAG):

```sh
python setup.py
```

### Running the Server
Start the server using:

```sh
python serve.py
```

## API Usage

### Endpoint
**URL:** `http://127.0.0.1:5001/chat`  
**Method:** `POST`

curl -X POST http://127.0.0.1:5001/chat \
-H "Content-Type: application/json" \
-d '{"message": "What are the admission requirements for the Computer Science program?"}'

### Testing with cURL
Run the following command to test the server:

## License
This project is licensed under [MIT License](LICENSE).

---

With this README, your project is now more structured and easier to understand for new users!

