Note: Run the following three commands if you have completed lab 1, and would like to use the MCP server created in that lab. You do not need to run these two commands if you already are using the public MCP server link provided to you during a live event.

Give the Cloud Run service identity permission to call the remote MCP server

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/run.invoker"
Save the MCP server URL from Lab 1 to an environment variable.

echo -e "\nMCP_SERVER_URL=https://zoo-mcp-server-${PROJECT_NUMBER}.europe-west1.run.app/mcp" >> .env
If you are using a public MCP server link, run the following, and replace PROJECT_NUMBER with what is provided.


echo -e "\nMCP_SERVER_URL=https://zoo-mcp-server-${PROJECT_NUMBER}.europe-west1.run.app/mcp" >> .env


Skip to main content
Build and deploy an ADK agent that uses an MCP server on Cloud Run
access_time
52 mins remaining

English
Introduction
Why deploy to Cloud Run?
Setup and Requirements
Before you begin
Create the project folder
Create Agent Workflow
Prepare the application for deployment
Deploy the agent using the ADK CLI
Test the deployed agent
Clean up environment
Congratulations
Survey
6. Create Agent Workflow
Create init.py file
Create the init.py file. This file tells Python that the zoo_guide_agent directory is a package.


cloudshell edit __init__.py
The above command opens up the code editor. Add the following code to __init__.py:


from . import agent
Create main agent.py file
Create the main agent.py file. This command creates the Python file and pastes in the complete code for your multi-agent system.


cloudshell edit agent.py
Step 1: Imports and Initial Setup
This first block brings in all the necessary libraries from the ADK and Google Cloud. It also sets up logging and loads the environment variables from your .env file, which is crucial for accessing your model and server URL.

Add the following code to your agent.py file:


import os
import logging
import google.cloud.logging
from dotenv import load_dotenv

from google.adk import Agent
from google.adk.agents import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StreamableHTTPConnectionParams
from google.adk.tools.tool_context import ToolContext
from google.adk.tools.langchain_tool import LangchainTool

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

import google.auth
import google.auth.transport.requests
import google.oauth2.id_token

# --- Setup Logging and Environment ---

cloud_logging_client = google.cloud.logging.Client()
cloud_logging_client.setup_logging()

load_dotenv()

model_name = os.getenv("MODEL")
Step 2: Defining the Tools (The Agent's Capabilities)
3eb9c6772576b906.jpeg

An agent is only as good as the tools it can use. In this section, we define all the capabilities our agent will have, including a custom function to save data, an MCP Tool that connects to our secure MCP server along with a Wikipedia Tool.

Add the following code to the bottom of agent.py:


# Greet user and save their prompt

def add_prompt_to_state(
    tool_context: ToolContext, prompt: str
) -> dict[str, str]:
    """Saves the user's initial prompt to the state."""
    tool_context.state["PROMPT"] = prompt
    logging.info(f"[State updated] Added to PROMPT: {prompt}")
    return {"status": "success"}


# Configuring the MCP Tool to connect to the Zoo MCP server

mcp_server_url = os.getenv("MCP_SERVER_URL")
if not mcp_server_url:
    raise ValueError("The environment variable MCP_SERVER_URL is not set.")

def get_id_token():
    """Get an ID token to authenticate with the MCP server."""
    target_url = os.getenv("MCP_SERVER_URL")
    audience = target_url.split('/mcp/')[0]
    request = google.auth.transport.requests.Request()
    id_token = google.oauth2.id_token.fetch_id_token(request, audience)
    return id_token

"""
# Use this code if you are using the public MCP Server and comment out the code below defining mcp_tools
mcp_tools = MCPToolset(
    connection_params=StreamableHTTPConnectionParams(
        url=mcp_server_url
    )
)
"""

mcp_tools = MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=mcp_server_url,
                headers={
                    "Authorization": f"Bearer {get_id_token()}",
                },
            ),
        )

# Configuring the Wikipedia Tool
wikipedia_tool = LangchainTool(
    tool=WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())
)
The Three Tools Explained

add_prompt_to_state 📝
This tool remembers what a zoo visitor asks. When a visitor asks, "Where are the lions?", this tool saves that specific question into the agent's memory so the other agents in the workflow know what to research.

How: It's a Python function that writes the visitor's prompt into the shared tool_context.state dictionary. This tool context represents the agent's short-term memory for a single conversation. Data saved to the state by one agent can be read by the next agent in the workflow.

MCPToolset 🦁
This is used to connect the tour guide agent to the zoo MCP server created in Lab 1. This server has special tools for looking up specific information about our animals, like their name, age, and enclosure.

How: It securely connects to the zoo's private server URL. It uses get_id_token to automatically get a secure "keycard" (a service account ID token) to prove its identity and gain access.

LangchainTool 🌍
This gives the tour guide agent general world knowledge. When a visitor asks a question that isn't in the zoo's database, like "What do lions eat in the wild?", this tool lets the agent look up the answer on Wikipedia.

How: It acts as an adapter, allowing our agent to use the pre-built WikipediaQueryRun tool from the LangChain library.

Resources:

MCP Toolset
Function Tools
State
Step 3: Defining the Specialist Agents
b8a9504b21920969.jpeg
Next we will define the researcher agent and response formatter agent. The researcher agent is the "brain" of our operation. This agent takes the user's prompt from the shared State, examines its powerful tools (the Zoo's MCP Server Tool and the Wikipedia Tool), and decides which ones to use to find the answer.

The response formatter agent's role is presentation. It doesn't use any tools to find new information. Instead, it takes the raw data gathered by the Researcher agent (passed via the State) and uses the LLM's language skills to transform it into a friendly, conversational response.

Add the following code to the bottom of agent.py:


# 1. Researcher Agent
comprehensive_researcher = Agent(
    name="comprehensive_researcher",
    model=model_name,
    description="The primary researcher that can access both internal zoo data and external knowledge from Wikipedia.",
    instruction="""
    You are a helpful research assistant. Your goal is to fully answer the user's PROMPT.
    You have access to two tools:
    1. A tool for getting specific data about animals AT OUR ZOO (names, ages, locations).
    2. A tool for searching Wikipedia for general knowledge (facts, lifespan, diet, habitat).

    First, analyze the user's PROMPT.
    - If the prompt can be answered by only one tool, use that tool.
    - If the prompt is complex and requires information from both the zoo's database AND Wikipedia,
      you MUST use both tools to gather all necessary information.
    - Synthesize the results from the tool(s) you use into preliminary data outputs.

    PROMPT:
    {{ PROMPT }}
    """,
    tools=[
        mcp_tools,
        wikipedia_tool
    ],
    output_key="research_data" # A key to store the combined findings
)

# 2. Response Formatter Agent
response_formatter = Agent(
    name="response_formatter",
    model=model_name,
    description="Synthesizes all information into a friendly, readable response.",
    instruction="""
    You are the friendly voice of the Zoo Tour Guide. Your task is to take the
    RESEARCH_DATA and present it to the user in a complete and helpful answer.

    - First, present the specific information from the zoo (like names, ages, and where to find them).
    - Then, add the interesting general facts from the research.
    - If some information is missing, just present the information you have.
    - Be conversational and engaging.

    RESEARCH_DATA:
    {{ research_data }}
    """
)
Step 4: The Workflow Agent
The workflow agent acts as the ‘back-office' manager for the zoo tour. It takes the research request and ensures the two agents we defined above perform their jobs in the correct order: first research, then formatting. This creates a predictable and reliable process for answering a visitor's question.

How: It's a SequentialAgent, a special type of agent that doesn't think for itself. Its only job is to run a list of sub_agents (the researcher and formatter) in a fixed sequence, automatically passing the shared memory from one to the next.

Add this block of code to the bottom of agent.py:


tour_guide_workflow = SequentialAgent(
    name="tour_guide_workflow",
    description="The main workflow for handling a user's request about an animal.",
    sub_agents=[
        comprehensive_researcher, # Step 1: Gather all data
        response_formatter,       # Step 2: Format the final response
    ]
)
Final Step: Assemble the Main Workflow 1000b9d20f4e134b.jpeg
This Agent is designated as the root_agent, which the ADK framework uses as the starting point for all new conversations. Its primary role is to orchestrate the overall process. It acts as the initial controller, managing the first turn of the conversation.

Add this final block of code to the bottom of agent.py:


root_agent = Agent(
    name="greeter",
    model=model_name,
    description="The main entry point for the Zoo Tour Guide.",
    instruction="""
    - Let the user know you will help them learn about the animals we have in the zoo.
    - When the user responds, use the 'add_prompt_to_state' tool to save their response.
    After using the tool, transfer control to the 'tour_guide_workflow' agent.
    """,
    tools=[add_prompt_to_state],
    sub_agents=[tour_guide_workflow]
)
Your agent.py file is now complete! By building it this way, you can see how each component—tools, worker agents, and manager agents—has a specific role in creating the final, intelligent system. Next up, deployment!

Back
Next
bug_report Report a mistake

7. Prepare the application for deployment
With your local environment ready, the next step is to prepare your Google Cloud project for the deployment. This involves a final check of your agent's file structure to ensure it's compatible with the deployment command. More importantly, you configure a critical IAM permission that allows your deployed Cloud Run service to act on your behalf and call the Vertex AI models. Completing this step ensures the cloud environment is ready to run your agent successfully.

Load the variables into your shell session by running the source command.


source .env
Grant the service account the Vertex AI User role, which gives it permission to make predictions and call Google's models.


# Grant the "Vertex AI User" role to your service account
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/aiplatform.user"

Skip to main content
Build and deploy an ADK agent that uses an MCP server on Cloud Run
access_time
22 mins remaining

English
Introduction
Why deploy to Cloud Run?
Setup and Requirements
Before you begin
Create the project folder
Create Agent Workflow
Prepare the application for deployment
Deploy the agent using the ADK CLI
Test the deployed agent
Clean up environment
Congratulations
Survey
8. Deploy the agent using the ADK CLI
With your local code ready and your Google Cloud project prepared, it's time to deploy the agent. You will use the adk deploy cloud_run command, a convenient tool that automates the entire deployment workflow. This single command packages your code, builds a container image, pushes it to Artifact Registry, and launches the service on Cloud Run, making it accessible on the web.

Deploy
Run the following commands to deploy your agent. The uvx command allows you to run command line tools published as Python packages without requiring a global installation of those tools.

Note: This deploy command below will take a few minutes to finish running.


# Run the deployment command
uvx --from google-adk \
adk deploy cloud_run \
  --project=$PROJECT_ID \
  --region=europe-west1 \
  --service_name=zoo-tour-guide \
  --with_ui \
  . \
  -- \
  --labels=dev-tutorial=codelab-adk
Accept Prompts
You may be prompted with the following:


Deploying from source requires an Artifact Registry Docker repository to store built containers. A repository named [cloud-run-source-deploy] in region 
[europe-west1] will be created.

Do you want to continue (Y/n)?
Type Y and hit ENTER.

You may be prompted with the following:


Allow unauthenticated invocations to [your-service-name] (y/N)?.
For this lab we want to allow unauthenticated invocations for easy testing, type y and hit Enter.

Note: Anyone with the URL will have access to this agent, so this is best for testing.

Get the Deployment Link
Upon successful execution, the command will provide the URL of the deployed Cloud Run service. (It will look something like https://zoo-tour-guide-123456789.europe-west1.run.app). Copy this URL for the next task.

Back
Next
bug_report Report a mistake


Skip to main content
Build and deploy an ADK agent that uses an MCP server on Cloud Run
access_time
12 mins remaining

English
Introduction
Why deploy to Cloud Run?
Setup and Requirements
Before you begin
Create the project folder
Create Agent Workflow
Prepare the application for deployment
Deploy the agent using the ADK CLI
Test the deployed agent
Clean up environment
Congratulations
Survey
9. Test the deployed agent
With your agent now live on Cloud Run, you'll perform a test to confirm that the deployment was successful and the agent is working as expected. You'll use the public Service URL (something like https://zoo-tour-guide-123456789.europe-west1.run.app/) to access the ADK's web interface and interact with the agent.

Open the public Cloud Run Service URL in your web browser. Because you used the --with_ui flag, you should see the ADK developer UI.

Toggle on Token Streaming in the upper right.

You can now interact with the Zoo agent.

Type hello and hit enter to begin a new conversation.

Observe the result. The agent should respond quickly with its greeting:


"Hello! I'm your Zoo Tour Guide. I can help you learn about the amazing animals we have here. What would you like to know or explore today?"
Ask the agent questions like:


Where can I find the polar bears in the zoo and what is their diet?
3244d2f6c3b03088.png e135694253b1be41.png

Agent Flow Explained
Your system operates as an intelligent, multi-agent team. The process is managed by a clear sequence to ensure a smooth and efficient flow from a user's question to the final, detailed answer.

1. The Zoo Greeter (The Welcome Desk)

The entire process begins with the greeter agent.

Its Job: To start the conversation. Its instruction is to greet the user and ask what animal they would like to learn about.

Its Tool: When the user replies, the Greeter uses its add_prompt_to_state tool to capture their exact words (e.g., "tell me about the lions") and save them in the system's memory.

The Handoff: After saving the prompt, it immediately passes control to its sub-agent, the tour_guide_workflow.

2. The Comprehensive Researcher (The Super-Researcher)

This is the first step in the main workflow and the "brain" of the operation. Instead of a large team, you now have a single, highly-skilled agent that can access all the available information.

Its Job: To analyze the user's question and form an intelligent plan. It uses the language model's powerful tool use capability to decide if it needs:

Internal data from the zoo's records (via the MCP Server).
General knowledge from the web (via the Wikipedia API).
Or, for complex questions, both.
Its Action: It executes the necessary tool(s) to gather all the required raw data. For example, if asked "How old are our lions and what do they eat in the wild?", it will call the MCP server for the ages and the Wikipedia tool for the diet information.

3. The Response Formatter (The Presenter)

Once the Comprehensive Researcher has gathered all the facts, this is the final agent to run.

Its Job: To act as the friendly voice of the Zoo Tour Guide. It takes the raw data (which could be from one or both sources) and polishes it.

Its Action: It synthesizes all the information into a single, cohesive, and engaging answer. Following its instructions, it first presents the specific zoo information and then adds the interesting general facts.

The Final Result: The text generated by this agent is the complete, detailed answer that the user sees in the chat window.

If you interested in learning more about building Agents, check out the following resources:

ADK docs
Building Custom Tools For ADK Agents
Back
Next
bug_report Report a mistake




Here is the transcription and a detailed summary of the video clip:

**Transcription**

"This is what happened when I gave my AI agent's memory. We built an AI agent that teaches Python. Here's the final flow. The agent asks your name, searches memory for past progress, runs a new quiz personalized to you, and afterward, it automatically saves the session to memory bank. When you return, the agent greets you by name, recalls your score, and builds on what you last learned. No lost context. This combo of short-term session state plus long-term memory service makes agents more human-like and effective tutors for our use case. We've gone from forgetful agents to scratchpad sessions to persistent state to long-term memory and finally to a full working system. So now you have the recipe for building AI agents that actually remember."

**Summary**

The video explains the process and benefits of creating an AI agent with memory, specifically an agent designed to teach Python. The final workflow of this AI agent is as follows:

1.  **Get Username:** The agent begins by asking for the user's name.
2.  **Search Memory:** It then searches its memory for the user's past quiz scores and progress to establish a baseline.
3.  **Start Personalized Quiz:** The agent initiates a new quiz that is personalized to the user's previous performance. It waits for the user's response to each question and allows them to submit their answers.
4.  **Add Session to Memory:** Once the quiz is complete, the entire session is automatically saved to a "memory bank."

This system ensures that when a user returns, there is no lost context. The AI agent greets them by name, recalls their previous scores, and builds upon what they last learned. The speaker highlights that the combination of "short-term session state" and a "long-term memory service" makes the AI agents more human-like and effective as tutors.

The video concludes by summarizing the evolution of their AI development, starting from "forgetful agents" and progressing through "scratchpad sessions" and "persistent state" to finally achieve "long-term memory" in a fully functional system. The speaker states that this provides the recipe for building AI agents that can truly remember user interactions.



export SERVICE_NAME='galatic-streamhub' # Or your preferred service name
export LOCATION='us-central1'         # Or your preferred region
export PROJECT_ID='silver-455021' # Replace with your Project ID


    gcloud run deploy $SERVICE_NAME \
      --source . \
      --region $LOCATION \
      --project $PROJECT_ID \
      --memory 4G \
      --allow-unauthenticated

GOOGLE_APPLICATION_CREDENTIALS="./pilot-local-dev-sa-key.json" uv run uvicorn main:app --reload

GOOGLE_APPLICATION_CREDENTIALS="./pilot-local-dev-sa-key.json" uv run pytest