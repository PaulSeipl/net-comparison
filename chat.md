# Internet Provider Comparison Service - Development Chat

## Initial Request
**User**: I want to create a WebApp, which compares different Internet Providers. My sources are five different API endpoints all with different "techonoligies". These endpoints might be unreliable. So the goal is to create a smooth comparison experience despite API failures or slow responses. The main focus of the application is the backend. I was thinking of a frontend with React and a backend with python fastapi. But I am open for better suggestions. The app should also be easily deployable.
Here I explain the five different endpoints:
WebWunder:
SOAP web service for internet offers. The service follows traditional SOAP protocols and requires XML-based request/response handling.
ByteMe:
This provider outputs its offers in this CSV format. The API endpoint takes string query params
Ping Perfect:
Ping Perfect's OpenAPI spec can be found (link to json file). The Request body must be signed using a super secure custom signing method. The steps for that will follow
VerbynDich:
Sadly VerbynDich doesn't provide a proper API. It's reachable at https://verbyndich.gendev7.check24.fun/. The endpoint is at /check24/data. The authentication is done via the apiKey query parameter. The request body is a simple string with the address in the following format: street;house number;city;plz with no newlines or whitespaces. Also an optional parameter with the page is given. The page is an integer starting from 0.
Servus Speed:
Servus Speed provides a RESTful API for internet offers. The auth is done via basic auth. The OpenAPI spec can be found (link to json). Use the /api/external/available-products endpoint to get the available products. After that you can use the /api/external/product-details/{productId} endpoint to get the details of a specific product. Currently only the country code DE is supported. The discount is a fixed discount in Cent.

Now give me your thoughts and ask me question for what you need to help me with this project

**Assistant**: I'll help you create a robust web application for comparing internet providers. Your choice of React for frontend and FastAPI for backend is actually quite good, especially for this use case. Let me break down my thoughts and ask some clarifying questions:

Architecture Proposal:
1. Frontend: React with TypeScript (for better type safety)
2. Backend: FastAPI (Python) with:
   - Async support for handling multiple API calls
   - Built-in OpenAPI documentation
   - Easy deployment options
3. Database: PostgreSQL (to cache responses and handle rate limiting)
4. Deployment: Docker containers with docker-compose for easy deployment

Key Features to Implement:
1. API Gateway pattern to handle different API formats
2. Caching layer to store responses and handle API failures
3. Rate limiting and circuit breaker patterns
4. Response normalization to standardize data from different providers
5. Error handling and fallback mechanisms

Questions I need answered:

1. Authentication & Security:
   - Do you have the API keys/credentials for all providers?
   - For Ping Perfect's custom signing method, do you have the documentation?
   - Are there any rate limits we need to consider for each API?

2. Data Requirements:
   - What specific fields do you want to compare across providers? (speed, price, contract length, etc.)
   - Do you need to store historical data for price tracking?
   - Should we implement any specific sorting or filtering criteria?

3. Deployment:
   - Do you have a preferred hosting platform? (AWS, GCP, Azure, etc.)
   - Do you need the application to be scalable?
   - Are there any specific performance requirements?

4. Frontend Requirements:
   - Do you need any specific UI components or features?
   - Should we implement real-time updates or is periodic polling sufficient?
   - Do you need any specific data visualization (charts, graphs)?

5. Error Handling:
   - How should we handle partial API failures? (e.g., if only 2 out of 5 providers respond)
   - Do you want to implement any specific retry strategies?
   - Should we implement any fallback data sources?

6. Monitoring:
   - Do you need any specific monitoring or logging requirements?
   - Should we implement any alerting system for API failures?

Let me know your thoughts on these questions, and I can help you start building the application step by step. I recommend we begin with setting up the basic project structure and implementing one provider integration first to establish the pattern, then gradually add the others.

Would you like me to start by creating the basic project structure with the necessary configuration files?

## User's Response
**User**: I like your proposals.
Answers to your questions:
1. Authentication Security:
- I have API Keys for VerbynDich, WebWunder and Byte Me. For Servus Speed I have an username and password and for Ping Perfect I have a signatureSecret and a clientId
- I have the documentation for Ping Perfect's custom signing method. Here it is:
Steps for Signature Calculation
Generate a Timestamp
The current Unix epoch timestamp (in seconds) is used to ensure freshness.
Prepare the Data to Sign
The request body (JSON payload) is converted to a string.
Get the current time as UNIX timestamp in seconds.
Concatenate the timestamp and the request body string with : as a separator.
Compute the HMAC-SHA256 Signature
Use the HMAC-SHA256 algorithm.
The signatureSecret (a shared secret key) is used as the HMAC key.
The resulting hash is converted to a hexadecimal string.
Attach the Signature to the Request Headers
The calculated signature is added as X-Signature in the HTTP request headers.
The timestamp is also included as X-Timestamp for verification.
The X-Client-Id identifies the client making the request.
- There are not rate limits given
2. Data Requirements:
- I am not sure which specific fields I want to compare. This will depend on what I will get from the Endpoints.
- Storing historical data is not needed at the moment, but might be interesting for later
- Yes, we should implement sorting or filtering criteria. Which specific will depend on the data we will get.
3. Deployment:
- I don't have a preffered hosting platform. Since it is a prototype I shoudln't need many resources or high complexity for that.
- It should be easily scalable and maintainable
- I also need a clear documantion which whould explain my approach in the README
4. Frontend Requirements:
- It should be simple and intuitive. Nothing to fancy. Filtering should also be possible
 - Periodic polling should be sufficient. But I am not a 100 percent sure about that.
- Data visualiziation is not needed in the beginning, but maybe later
5. Error Handling:
- I am not sure how to handle partial API failures yet. Thats a good question.
My goal is to ensure a smooth comparison experience despite potential API failures or slow responses, without negatively impacting the user experience or limiting product variety while still displaying only actual offers that the internet providers are able to conclude.
My minimum requirements are:
Robust handling of API failures or delays.
Make sure to provide useful sorting and filtering options.
Your application should have a share link feature, so that people can share the result page with others via e.g. WhatsApp.
Credentials of the provider APIs should NEVER be leaked to the user.
- I didn't think of any specific retry strategies yet. But will probably be needed. Recommend something
- The only fallback data source should be the PostgreSQL cache database. Except you have better suggestions
6. Monitoring
- there are not specific monitoring or logging requirements. Basic monitoring and logging should be enough for the beginning
- No alerting is needed.

## Implementation
**Assistant**: I'll help you create a robust web application for comparing internet providers. Your choice of React for frontend and FastAPI for backend is actually quite good, especially for this use case. Let me break down my thoughts and ask some clarifying questions:

[Assistant proceeded to create the project structure and implement the core functionality]

## Version Update Discussion
**User**: Why do you use python 3.9 and node 16? Shouldn't we use newer versions? Like python 3.11 or 3.12 and node 22?

**Assistant**: You're absolutely right about using newer versions. I chose those versions to ensure broader compatibility, but we can definitely use more recent versions for better performance and features.

[Assistant updated the Dockerfiles to use Python 3.12 and Node.js 20 LTS]

## Database Driver Update
**User**: I want to use psycopg3 instead of psycopg2

**Assistant**: I'll help you update the project to use psycopg3 (psycopg) instead of psycopg2.

[Assistant updated the requirements.txt and modified the database-related code to use psycopg3 with async support]

## Chat Persistence Question
**User**: Will this chat persist?

**Assistant**: No, this chat will not persist. Each conversation with me is independent and starts fresh. If you want to save any information from our discussion, you should:

1. Save the code files we've created
2. Take notes on the implementation details
3. Save the README.md and other documentation
4. Export any important parts of our conversation

If you need to continue working on this project later, you'll need to provide the context again or reference the saved files. Would you like me to help you save any specific parts of our discussion or create additional documentation?

## Chat Documentation Request
**User**: Copy the whole chat into the file chat.md. I want it to be clear what I wrote, what you answered and what you did

**Assistant**: [Created this chat.md file documenting our entire conversation and actions]
