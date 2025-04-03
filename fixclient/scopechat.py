import json
import os
from datetime import datetime
import anthropic
import maricon

# Default prompt template for trader simulation
DEFAULT_PROMPT = """You are an experienced financial trader. You're conversing with another trader or market participant who may ask you questions about market conditions, trading strategies, or specific orders.

Respond in a realistic way, using trader lingo and being somewhat brief in your responses. You can discuss market trends, trading ideas, and respond to questions about specific symbols.

Current market conditions:
- SPY is trending higher with strong momentum
- AAPL had a recent earnings beat
- TSLA is volatile due to recent news
- Interest rates are expected to remain stable

IMPORTANT: When the user asks you to execute an order (buy or sell), you should indicate this with a special tag at the end of your message. For example:
- If they ask "buy 100 AAPL at market", respond normally but end with: [ORDER:BUY,AAPL,100,MKT]
- If they ask "sell 50 TSLA at 250", respond normally but end with: [ORDER:SELL,TSLA,50,250]
- The format is always [ORDER:SIDE,SYMBOL,QUANTITY,PRICE] where PRICE can be a number or MKT for market orders

If you do not make a transaction as a result of the chat, you will submit another trade on a random US symbol, estimating the price."""

class ScopeChat:
    def __init__(self):
        self.chat_history = {}  # Store chat history by scope_id
        self.api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        self.client = anthropic.Anthropic(api_key=maricon.anthropic_key)
        self.order_handler = None  # Will be set by external code to handle order submission
    
    def set_order_handler(self, handler_function):
        """Set the function that will handle order submissions"""
        self.order_handler = handler_function
    
    def send_message(self, scope_id, message, custom_prompt=None):
        """Send a message to a simulated trader and get a response"""
        # Initialize chat history for this scope_id if it doesn't exist
        if scope_id not in self.chat_history:
            self.chat_history[scope_id] = []
        
        # Add user message to history
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_history[scope_id].append({
            "role": "user",
            "content": message,
            "timestamp": timestamp
        })
        
        # Prepare the prompt for Claude
        prompt = custom_prompt if custom_prompt else DEFAULT_PROMPT
        
        # Build conversation history for Claude
        messages = [{"role": "system", "content": prompt}]
        for chat in self.chat_history[scope_id]:
            messages.append({
                "role": chat["role"],
                "content": chat["content"]
            })
        
        # If API key is not set, return a mock response
        if not self.client:
            response = f"[MOCK TRADER RESPONSE] This is a simulated response as no API key is set. Regarding: {message}"
        else:
            # Make API request to Claude using the Anthropic client
            try:
                response = self._call_claude_api(messages)
            except Exception as e:
                response = f"Error: Could not get response from trader simulation. {str(e)}"
        
        # Check if the response contains an order instruction
        order_result = None
        if "[ORDER:" in response and "]" in response:
            order_result = self._process_order_instruction(response, scope_id)
            # Clean the response by removing the order tag
            response = response.split("[ORDER:")[0].strip()
        
        # Add assistant response to history
        self.chat_history[scope_id].append({
            "role": "assistant",
            "content": response,
            "timestamp": timestamp
        })
        
        result = {
            "response": response,
            "timestamp": timestamp,
            "scope_id": scope_id
        }
        
        # Add order result if an order was processed
        if order_result:
            result["order_result"] = order_result
        
        return result
    
    def _process_order_instruction(self, response, scope_id):
        """Process an order instruction from the AI response"""
        try:
            # Extract the order instruction
            order_tag = response[response.find("[ORDER:"):response.find("]")+1]
            order_parts = order_tag.replace("[ORDER:", "").replace("]", "").split(",")
            
            if len(order_parts) != 4:
                return {"status": "ERROR", "message": "Invalid order format"}
            
            side, symbol, quantity, price = order_parts
            
            # Convert side to the format expected by the order system
            side_value = "1" if side.upper() == "BUY" else "2"
            
            # Handle market orders
            if price.upper() == "MKT":
                price = "0"  # Use 0 as a placeholder for market orders
            
            # If we have an order handler, use it to submit the order
            if self.order_handler:
                order_result = self.order_handler(side_value, symbol, quantity, price, f"{scope_id}")
                return order_result
            else:
                return {
                    "status": "ERROR", 
                    "message": "Order handler not configured"
                }
        except Exception as e:
            return {"status": "ERROR", "message": f"Failed to process order: {str(e)}"}
    
    def _call_claude_api(self, messages):
        """Call the Claude API with the conversation history using the Anthropic client"""
        try:
            # Extract system message
            system_message = None
            conversation_messages = []
            
            for message in messages:
                if message["role"] == "system":
                    system_message = message["content"]
                else:
                    conversation_messages.append(message)
            
            response = self.client.messages.create(
                model="claude-3-7-sonnet-latest",
                system=system_message,
                messages=conversation_messages,
                max_tokens=500
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"API Error: {str(e)}")
    
    def get_chat_history(self, scope_id):
        """Get the chat history for a specific scope_id"""
        return self.chat_history.get(scope_id, [])
    
    def clear_chat(self, scope_id):
        """Clear the chat history for a specific scope_id"""
        if scope_id in self.chat_history:
            self.chat_history[scope_id] = []
        return {"status": "Chat cleared", "scope_id": scope_id}

# Create a singleton instance
scope_chat = ScopeChat() 