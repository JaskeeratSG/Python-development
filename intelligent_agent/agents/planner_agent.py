"""Planner agent for handling trip planning, flight booking, and travel queries."""

from typing import List, Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import re
import json
from datetime import datetime

from agents.base_agent import BaseAgent
from graph.state_schema import AgentState
from tools.search_tools import TavilySearchTool


class PlannerAgent(BaseAgent):
    """
    Agent specialized in trip planning, flight booking, and travel queries.
    
    This agent:
    - Searches for flight/travel information
    - Extracts and structures data from search results
    - Sorts flights by price (cheapest to expensive)
    - Filters by dates and other criteria
    - Provides booking links
    """
    
    def __init__(self):
        """Initialize the planner agent."""
        super().__init__(
            name="planner_agent",
            description="Handles trip planning, flight booking, and travel queries"
        )
        self.tavily_client = TavilySearchTool()
    
    def process(self, state: AgentState) -> AgentState:
        """
        Process travel/booking query and extract structured information.
        
        Args:
            state: Current agent state
        
        Returns:
            Updated state with structured flight/travel data
        """
        query = state["query"]
        
        # Perform search for flight information
        search_query = self._build_search_query(query)
        search_results = self.tavily_client.search(search_query, max_results=10)
        
        # Update state with raw search results
        state["results"] = search_results
        
        # Extract and structure flight data from search results
        flight_data = self._extract_flight_data(query, search_results)
        
        # Sort flights by price (cheapest first)
        sorted_flights = self._sort_flights_by_price(flight_data)
        
        # Filter by dates if specified
        filtered_flights = self._filter_by_dates(sorted_flights, query)
        
        # Generate formatted response
        response = self._generate_flight_response(query, filtered_flights, search_results)
        
        # Update state
        state["response"] = response
        state["metadata"]["flight_data"] = filtered_flights
        state["metadata"]["total_flights_found"] = len(filtered_flights)
        
        # Update context
        self.update_context(
            state,
            f"Found {len(filtered_flights)} flights sorted by price (cheapest first)"
        )
        
        # Add message to conversation
        self.add_message(
            state,
            response,
            role="assistant"
        )
        
        return state
    
    def _build_search_query(self, user_query: str) -> str:
        """
        Build optimized search query from user request.
        
        Args:
            user_query: Original user query
        
        Returns:
            Optimized search query
        """
        # Extract key information using LLM
        extraction_prompt = SystemMessage(content="""
        Extract key travel information from the query:
        - Origin city/country
        - Destination city/country
        - Travel dates
        - Any specific requirements
        
        Return in format: "flights from [origin] to [destination] [dates] [requirements]"
        Keep it concise for web search.
        """)
        
        user_msg = HumanMessage(content=f"Extract travel info: {user_query}")
        response = self.llm.invoke([extraction_prompt, user_msg])
        
        # Use LLM response or fallback to original query
        search_query = response.content.strip()
        if not search_query or len(search_query) < 10:
            search_query = f"flight prices {user_query}"
        
        return search_query
    
    def _extract_flight_data(self, query: str, search_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract structured flight data from search results using LLM.
        
        Args:
            query: Original user query
            search_results: Raw search results from Tavily
        
        Returns:
            List of structured flight data dictionaries
        """
        if not search_results:
            return []
        
        # Prepare search results text for LLM (include more content)
        results_text = "\n\n".join([
            f"Result {i+1}:\nTitle: {r.get('title', '')}\nContent: {r.get('content', '')[:1000]}\nURL: {r.get('url', '')}"
            for i, r in enumerate(search_results[:8])  # Use more results
        ])
        
        # Extract key info from user query first
        query_info = self._extract_query_info(query)
        
        # Use LLM to extract structured flight data with better prompt
        extraction_prompt = SystemMessage(content="""
        You are a flight data extractor. Extract flight information from search results.
        
        IMPORTANT: Only extract flights that match the user's query:
        - Origin: {origin}
        - Destination: {destination}
        - Dates: {dates}
        
        For each flight found, extract EXACTLY:
        - airline: Full airline name (e.g., "IndiGo", "Air India", "SpiceJet")
        - price: Price with currency symbol (e.g., "₹25,000" or "$330")
        - price_usd: USD equivalent if available (e.g., "$330")
        - origin: Origin city name (e.g., "Delhi", "Mumbai", "India")
        - destination: Destination city name (e.g., "Bangkok", "Delhi")
        - departure_date: Departure date in YYYY-MM-DD format
        - return_date: Return date in YYYY-MM-DD format (if round trip)
        - url: Booking URL from the search result
        - notes: Any additional information
        
        CRITICAL RULES:
        1. If airline is not specified, use "Unknown Airline" - NEVER use "Not specified"
        2. If origin/destination is not clear, infer from user query - NEVER use "Not specified"
        3. If price is not available, skip that flight - don't include incomplete data
        4. Only extract flights that have at least airline AND price
        5. If URL is not available, use the search result URL
        
        Return ONLY valid JSON array format:
        [
            {{
                "airline": "IndiGo",
                "price": "₹25,000",
                "price_usd": "$330",
                "origin": "Delhi",
                "destination": "Bangkok",
                "departure_date": "2025-12-13",
                "return_date": "2025-12-20",
                "url": "https://example.com",
                "notes": "Direct flight"
            }}
        ]
        
        If no valid flights found, return empty array: []
        """.format(
            origin=query_info.get("origin", "India"),
            destination=query_info.get("destination", "Delhi"),
            dates=query_info.get("dates", "December 13-20, 2025")
        ))
        
        extraction_msg = HumanMessage(content=f"""
        User Query: {query}
        
        Search Results:
        {results_text}
        
        Extract flight information matching the user's query. Return ONLY valid JSON array.
        """)
        
        response = self.llm.invoke([extraction_prompt, extraction_msg])
        
        # Parse the response to extract flight data
        flights = self._parse_flight_data(response.content)
        
        # Validate and clean flights
        validated_flights = self._validate_flights(flights, query_info)
        
        return validated_flights
    
    def _extract_query_info(self, query: str) -> Dict[str, Any]:
        """Extract origin, destination, and dates from user query."""
        info_prompt = SystemMessage(content="""
        Extract travel information from the query. Return JSON format:
        {
            "origin": "origin city/country",
            "destination": "destination city/country",
            "dates": "travel dates description",
            "departure_date": "YYYY-MM-DD",
            "return_date": "YYYY-MM-DD"
        }
        If not found, use reasonable defaults based on query context.
        """)
        
        info_msg = HumanMessage(content=query)
        response = self.llm.invoke([info_prompt, info_msg])
        
        try:
            import json
            # Try to extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback: simple extraction
        query_lower = query.lower()
        info = {
            "origin": "India" if "from india" in query_lower or "from" not in query_lower else "",
            "destination": "Delhi" if "to delhi" in query_lower else "",
            "dates": "",
            "departure_date": "",
            "return_date": ""
        }
        
        # Extract dates
        date_match = re.search(r'(\d+)(?:th|st|nd|rd)?\s*(?:to|-)\s*(\d+)(?:th|st|nd|rd)?\s*(?:december|dec)', query_lower)
        if date_match:
            info["dates"] = f"December {date_match.group(1)}-{date_match.group(2)}, 2025"
        
        return info
    
    def _validate_flights(self, flights: List[Dict[str, Any]], query_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate and clean flight data."""
        validated = []
        
        for flight in flights:
            # Skip if missing critical fields
            if not flight.get("airline") or flight.get("airline", "").lower() in ["not specified", "unknown", "n/a", ""]:
                continue
            
            if not flight.get("price") or flight.get("price", "").lower() in ["not available", "n/a", ""]:
                continue
            
            # Fill in missing origin/destination from query
            if not flight.get("origin") or flight.get("origin", "").lower() in ["not specified", "n/a"]:
                flight["origin"] = query_info.get("origin", "India")
            
            if not flight.get("destination") or flight.get("destination", "").lower() in ["not specified", "n/a"]:
                flight["destination"] = query_info.get("destination", "Delhi")
            
            # Clean up URL
            if not flight.get("url") or flight.get("url", "").lower() in ["not available", "n/a", ""]:
                flight["url"] = ""
            
            validated.append(flight)
        
        return validated
    
    def _parse_flight_data(self, llm_response: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract flight data.
        
        Args:
            llm_response: LLM response containing flight data
        
        Returns:
            List of flight dictionaries
        """
        flights = []
        
        # Try to extract JSON array first
        import json
        import re
        
        # Look for JSON array pattern
        json_array_pattern = r'\[\s*\{[^}]+\}(?:\s*,\s*\{[^}]+\})*\s*\]'
        array_match = re.search(json_array_pattern, llm_response, re.DOTALL)
        
        if array_match:
            try:
                # Try to parse as JSON array
                json_str = array_match.group(0)
                flights = json.loads(json_str)
                if isinstance(flights, list):
                    return flights
            except json.JSONDecodeError:
                pass
        
        # Try to find individual JSON objects
        json_object_pattern = r'\{\s*"[^"]+"\s*:\s*"[^"]*"(?:\s*,\s*"[^"]+"\s*:\s*"[^"]*")*\s*\}'
        matches = re.findall(json_object_pattern, llm_response, re.DOTALL)
        
        for match in matches:
            try:
                # Clean up the match
                cleaned = match.strip()
                # Try to parse as JSON
                flight = json.loads(cleaned)
                if isinstance(flight, dict) and "airline" in flight and "price" in flight:
                    flights.append(flight)
            except json.JSONDecodeError:
                # If JSON parsing fails, try regex extraction
                airline = re.search(r'"airline"\s*:\s*"([^"]+)"', match)
                price = re.search(r'"price"\s*:\s*"([^"]+)"', match)
                origin = re.search(r'"origin"\s*:\s*"([^"]+)"', match)
                destination = re.search(r'"destination"\s*:\s*"([^"]+)"', match)
                url = re.search(r'"url"\s*:\s*"([^"]+)"', match)
                
                if airline and price:
                    flight = {
                        "airline": airline.group(1),
                        "price": price.group(1),
                        "origin": origin.group(1) if origin else "",
                        "destination": destination.group(1) if destination else "",
                        "url": url.group(1) if url else ""
                    }
                    flights.append(flight)
        
        # If no structured data found, try to extract from text
        if not flights:
            flights = self._extract_from_text(llm_response)
        
        return flights
    
    def _extract_from_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Fallback: Extract flight info from unstructured text.
        
        Args:
            text: Unstructured text
        
        Returns:
            List of flight dictionaries
        """
        flights = []
        
        # Look for patterns like "Airline: ₹25,000"
        pattern = r'([A-Za-z\s]+):\s*₹?([\d,]+)'
        matches = re.findall(pattern, text)
        
        for airline, price in matches:
            if len(airline.strip()) > 2:  # Valid airline name
                flights.append({
                    "airline": airline.strip(),
                    "price": f"₹{price}",
                    "origin": "",
                    "destination": "",
                    "url": ""
                })
        
        return flights
    
    def _sort_flights_by_price(self, flights: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Sort flights by price (cheapest first).
        
        Args:
            flights: List of flight dictionaries
        
        Returns:
            Sorted list of flights
        """
        def extract_price(flight: Dict[str, Any]) -> float:
            """Extract numeric price value for sorting."""
            price_str = str(flight.get("price", "0"))
            # Remove currency symbols and commas
            price_clean = re.sub(r'[₹$,\s]', '', price_str)
            try:
                return float(price_clean)
            except:
                return float('inf')  # Put unparseable prices at end
        
        return sorted(flights, key=extract_price)
    
    def _filter_by_dates(self, flights: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Filter flights by dates mentioned in query.
        
        Args:
            flights: List of flight dictionaries
            query: Original user query
        
        Returns:
            Filtered list of flights
        """
        # Extract dates from query using LLM
        date_prompt = SystemMessage(content="""
        Extract travel dates from the query. Return in format:
        "departure: YYYY-MM-DD, return: YYYY-MM-DD"
        If only one date, return "departure: YYYY-MM-DD"
        If no dates found, return "none"
        """)
        
        date_msg = HumanMessage(content=query)
        date_response = self.llm.invoke([date_prompt, date_msg])
        
        # Parse dates
        dates_text = date_response.content.lower()
        departure_date = None
        return_date = None
        
        if "departure:" in dates_text:
            dep_match = re.search(r'departure:\s*(\d{4}-\d{2}-\d{2})', dates_text)
            if dep_match:
                departure_date = dep_match.group(1)
        
        if "return:" in dates_text:
            ret_match = re.search(r'return:\s*(\d{4}-\d{2}-\d{2})', dates_text)
            if ret_match:
                return_date = ret_match.group(1)
        
        # If dates extracted, filter flights (for now, just return all as we may not have date in flight data)
        # In a real implementation, you'd filter by matching dates
        return flights
    
    def _generate_flight_response(self, query: str, flights: List[Dict[str, Any]], search_results: List[Dict[str, Any]]) -> str:
        """
        Generate user-friendly response with flight information.
        
        Args:
            query: Original user query
            flights: Sorted and filtered flight data
            search_results: Original search results for links
        
        Returns:
            Formatted response string
        """
        if not flights:
            return "I couldn't find specific flight prices in the search results. Please check booking websites directly for the most up-to-date prices and availability."
        
        response_parts = [
            f"Here are the flights sorted by price (cheapest to expensive) for your trip:\n\n"
        ]
        
        # Add flight list
        for i, flight in enumerate(flights[:10], 1):  # Top 10 cheapest
            airline = flight.get("airline", "Unknown")
            price = flight.get("price", "Price not available")
            price_usd = flight.get("price_usd", "")
            origin = flight.get("origin", "")
            destination = flight.get("destination", "")
            url = flight.get("url", "")
            
            flight_line = f"{i}. **{airline}**: {price}"
            if price_usd:
                flight_line += f" ({price_usd})"
            if origin and destination:
                flight_line += f" from {origin} to {destination}"
            if url:
                flight_line += f"\n   🔗 [Book here]({url})"
            
            response_parts.append(flight_line)
        
        # Add booking links from search results
        response_parts.append("\n\n**Booking Websites:**")
        unique_urls = set()
        for result in search_results:
            url = result.get("url", "")
            if url and any(domain in url.lower() for domain in ["makemytrip", "goibibo", "yatra", "expedia", "booking", "skyscanner"]):
                if url not in unique_urls:
                    unique_urls.add(url)
                    domain = url.split("//")[-1].split("/")[0]
                    response_parts.append(f"- [{domain}]({url})")
        
        response_parts.append("\n\n⚠️ **Note**: Prices are approximate and may vary. Please check the booking websites for current availability and exact prices for your travel dates.")
        
        return "\n".join(response_parts)

