
Read the 2025 State of Containers and Serverless Report!
Product
Customers
Pricing
Solutions
DataDog
About
Blog
Login
Datadog Docs

Search documentation...

Essentials

Getting Started
Glossary
Standard Attributes
Guides
Agent
Integrations
Developers
OpenTelemetry
Administrator's Guide
API
Partners
Datadog Mobile App
DDSQL Reference
CoScreen
CoTerm
Remote Configuration
Cloudcraft (Standalone)
In The App

Dashboards
Notebooks
DDSQL Editor
Reference Tables
Sheets
Monitors and Alerting
Watchdog
Metrics
Bits AI
Internal Developer Portal
Error Tracking
Change Tracking
Service Management

Service Level Objectives
Incident Management
On-Call
Status Pages
Event Management
Case Management
Actions & Remediations

Agents
Action Interface
Workflow Automation
App Builder
Datastores
Forms
Action Catalog
Infrastructure

Cloudcraft
Resource Catalog
Universal Service Monitoring
End User Device Monitoring
Hosts
Containers
Processes
Serverless
Network Monitoring
Storage Management
Cloud Cost

Cloud Cost
Application Performance

APM
Continuous Profiler
Database Monitoring
Data Streams Monitoring
Data Jobs Monitoring
Data Observability
Digital Experience

Real User Monitoring
Synthetic Testing and Monitoring
Continuous Testing
Product Analytics
Software Delivery

CI Visibility
CD Visibility
Deployment Gates
Test Optimization
Code Coverage
PR Gates
DORA Metrics
Feature Flags
Security

Security Overview
Cloud SIEM
Code Security
Cloud Security
App and API Protection
Workload Protection
Sensitive Data Scanner
AI Observability

LLM Observability
Quickstart
Instrumentation
Automatic
SDK Reference
HTTP API
OpenTelemetry
Monitoring
Evaluations
Experiments
Data Security and RBAC
Terms and Concepts
Guides
Log Management

Observability Pipelines
Log Management
CloudPrem
Administration

Account Management
Data Security
Help
LLM Observability SDK Reference
Docs >  LLM Observability >  LLM Observability Instrumentation >  LLM Observability SDK Reference
Overview
Datadog’s LLM Observability SDKs provide automatic instrumentation as well as manual instrumentation APIs to provide observability and insights into your LLM applications.

Setup
Requirements
A Datadog API key.
Python
Node.js
Java
The latest ddtrace package is installed (Python 3.7+ required):
pip install ddtrace
Command-line setup
Python
Node.js
Java
Enable LLM Observability by running your application using the ddtrace-run command and specifying the required environment variables.

Note: ddtrace-run automatically turns on all LLM Observability integrations.

DD_SITE=<YOUR_DATADOG_SITE> DD_API_KEY=<YOUR_API_KEY> DD_LLMOBS_ENABLED=1 \
DD_LLMOBS_ML_APP=<YOUR_ML_APP_NAME> ddtrace-run <YOUR_APP_STARTUP_COMMAND>
Environment variables for command-line setup
DD_SITE
required - string
Destination Datadog site for LLM data submission. Your site is us5.datadoghq.com.
DD_LLMOBS_ENABLED
required - integer or string
Toggle to enable submitting data to LLM Observability. Should be set to 1 or true.
DD_LLMOBS_ML_APP
optional - string
The name of your LLM application, service, or project, under which all traces and spans are grouped. This helps distinguish between different applications or experiments. See Application naming guidelines for allowed characters and other constraints. To override this value for a given root span, see Tracing multiple applications. If not provided, this defaults to the value of DD_SERVICE, or the value of a propagated DD_LLMOBS_ML_APP from an upstream service.
Note: Before version ddtrace==3.14.0, this is a required field.
DD_LLMOBS_AGENTLESS_ENABLED
optional - integer or string - default: false
Only required if you are not using the Datadog Agent, in which case this should be set to 1 or true.
DD_API_KEY
optional - string
Your Datadog API key. Only required if you are not using the Datadog Agent.
In-code setup
Instead of using command-line setup, you can also enable LLM Observability programmatically.

Python
Node.js
Use the LLMObs.enable() function to enable LLM Observability.

Do not use this setup method with the ddtrace-run command.
from ddtrace.llmobs import LLMObs
LLMObs.enable(
  ml_app="<YOUR_ML_APP_NAME>",
  api_key="<YOUR_DATADOG_API_KEY>",
  site="<YOUR_DATADOG_SITE>",
  agentless_enabled=True,
)
Parameters
ml_app
optional - string
The name of your LLM application, service, or project, under which all traces and spans are grouped. This helps distinguish between different applications or experiments. See Application naming guidelines for allowed characters and other constraints. To override this value for a given trace, see Tracing multiple applications. If not provided, this defaults to the value of DD_LLMOBS_ML_APP.
integrations_enabled - default: true
optional - boolean
A flag to enable automatically tracing LLM calls for Datadog’s supported LLM integrations. If not provided, all supported LLM integrations are enabled by default. To avoid using the LLM integrations, set this value to false.
agentless_enabled
optional - boolean - default: false
Only required if you are not using the Datadog Agent, in which case this should be set to True. This configures the ddtrace library to not send any data that requires the Datadog Agent. If not provided, this defaults to the value of DD_LLMOBS_AGENTLESS_ENABLED.
site
optional - string
The Datadog site to submit your LLM data. Your site is us5.datadoghq.com. If not provided, this defaults to the value of DD_SITE.
api_key
optional - string
Your Datadog API key. Only required if you are not using the Datadog Agent. If not provided, this defaults to the value of DD_API_KEY.
env
optional - string
The name of your application’s environment (examples: prod, pre-prod, staging). If not provided, this defaults to the value of DD_ENV.
service
optional - string
The name of the service used for your application. If not provided, this defaults to the value of DD_SERVICE.
AWS Lambda Setup
After installing the SDK and running your application you should expect to see some data in LLM Observability from auto-instrumentation. Manual instrumentation can be used to capture custom built frameworks or operations from libraries that are not yet supported.

Manual instrumentation
Python
Node.js
Java
To capture an LLM operation a function decorator can be used to easily instrument workflows:

from ddtrace.llmobs.decorators import workflow

@workflow
def handle_user_request():
    ...
or a context-manager based approach to capture fine-grained operations:

from ddtrace.llmobs import LLMObs

with LLMObs.llm(model="gpt-4o"):
    call_llm()
    LLMObs.annotate(
        metrics={
            "input_tokens": ...,
            "output_tokens": ...,
        },
    )
For a list of available span kinds, see the Span Kinds documentation. For more granular tracing of operations within functions, see Tracing spans using inline methods.

LLM calls
If you are using any LLM providers or frameworks that are supported by Datadog's LLM integrations, you do not need to manually start an LLM span to trace these operations.
Python
Node.js
Java
To trace an LLM call, use the function decorator ddtrace.llmobs.decorators.llm().

Arguments
model_name
required - string
The name of the invoked LLM.
name
optional - string
The name of the operation. If not provided, name defaults to the name of the traced function.
model_provider
optional - string - default: "custom"
The name of the model provider.
Note: To display the estimated cost in US dollars, set model_provider to one of the following values: openai, azure_openai, or anthropic.
session_id
optional - string
The ID of the underlying user session. See Tracking user sessions for more information.
ml_app
optional - string
The name of the ML application that the operation belongs to. See Tracing multiple applications for more information.
Example
from ddtrace.llmobs.decorators import llm

@llm(model_name="claude", name="invoke_llm", model_provider="anthropic")
def llm_call():
    completion = ... # user application logic to invoke LLM
    return completion
Workflows
Python
Node.js
Java
To trace a workflow span, use the function decorator ddtrace.llmobs.decorators.workflow().

Arguments
Example
from ddtrace.llmobs.decorators import workflow

@workflow
def process_message():
    ... # user application logic
    return
Agents
Python
Node.js
Java
To trace an agent execution, use the function decorator ddtrace.llmobs.decorators.agent().

Arguments
Example
from ddtrace.llmobs.decorators import agent

@agent
def react_agent():
    ... # user application logic
    return
Tool calls
Python
Node.js
Java
To trace a tool call, use the function decorator ddtrace.llmobs.decorators.tool().

Arguments
Example
from ddtrace.llmobs.decorators import tool

@tool
def call_weather_api():
    ... # user application logic
    return
Tasks
Python
Node.js
Java
To trace a task span, use the function decorator LLMObs.task().

Arguments
Example
from ddtrace.llmobs.decorators import task

@task
def sanitize_input():
    ... # user application logic
    return
Embeddings
Python
Node.js
To trace an embedding operation, use the function decorator LLMObs.embedding().

Note: Annotating an embedding span’s input requires different formatting than other span types. See Annotating a span for more details on how to specify embedding inputs.

Arguments
Example
from ddtrace.llmobs.decorators import embedding

@embedding(model_name="text-embedding-3", model_provider="openai")
def perform_embedding():
    ... # user application logic
    return
Retrievals
Python
Node.js
To trace a retrieval span, use the function decorator ddtrace.llmobs.decorators.retrieval().

Note: Annotating a retrieval span’s output requires different formatting than other span types. See Annotating a span for more details on how to specify retrieval outputs.

Arguments
Example
from ddtrace.llmobs.decorators import retrieval

@retrieval
def get_relevant_docs(question):
    context_documents = ... # user application logic
    LLMObs.annotate(
        input_data=question,
        output_data = [
            {"id": doc.id, "score": doc.score, "text": doc.text, "name": doc.name} for doc in context_documents
        ]
    )
    return
Nesting spans
Starting a new span before the current span is finished automatically traces a parent-child relationship between the two spans. The parent span represents the larger operation, while the child span represents a smaller nested sub-operation within it.

Python
Node.js
Java
from ddtrace.llmobs.decorators import task, workflow

@workflow
def extract_data(document):
    preprocess_document(document)
    ... # performs data extraction on the document
    return

@task
def preprocess_document(document):
    ... # preprocesses a document for data extraction
    return
Enriching spans
Python
Node.js
Java
The SDK provides the method LLMObs.annotate() to enrich spans with inputs, outputs, and metadata.

The LLMObs.annotate() method accepts the following arguments:

Arguments
Example
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import embedding, llm, retrieval, workflow

@llm(model_name="model_name", model_provider="model_provider")
def llm_call(prompt):
    resp = ... # llm call here
    LLMObs.annotate(
        span=None,
        input_data=[{"role": "user", "content": "Hello world!"}],
        output_data=[{"role": "assistant", "content": "How can I help?"}],
        metadata={"temperature": 0, "max_tokens": 200},
        metrics={"input_tokens": 4, "output_tokens": 6, "total_tokens": 10},
        tags={"host": "host_name"},
    )
    return resp

@workflow
def extract_data(document):
    resp = llm_call(document)
    LLMObs.annotate(
        input_data=document,
        output_data=resp,
        tags={"host": "host_name"},
    )
    return resp

@embedding(model_name="text-embedding-3", model_provider="openai")
def perform_embedding():
    ... # user application logic
    LLMObs.annotate(
        span=None,
        input_data={"text": "Hello world!"},
        output_data=[0.0023064255, -0.009327292, ...],
        metrics={"input_tokens": 4},
        tags={"host": "host_name"},
    )
    return

@retrieval(name="get_relevant_docs")
def similarity_search():
    ... # user application logic
    LLMObs.annotate(
        span=None,
        input_data="Hello world!",
        output_data=[{"text": "Hello world is ...", "name": "Hello, World! program", "id": "document_id", "score": 0.9893}],
        tags={"host": "host_name"},
    )
    return
Annotating auto-instrumented spans
Python
Node.js
The SDK’s LLMObs.annotation_context() method returns a context manager that can be used to modify all auto-instrumented spans started while the annotation context is active.

The LLMObs.annotation_context() method accepts the following arguments:

Arguments
Example
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow

@workflow
def rag_workflow(user_question):
    context_str = retrieve_documents(user_question).join(" ")

    with LLMObs.annotation_context(
        prompt = Prompt(
            id="chatbot_prompt",
            version="1.0.0",
            template="Please answer the question using the provided context: {{question}}\n\nContext:\n{{context}}",
            variables={
                "question": user_question,
                "context": context_str,
            }
        ),
        tags = {
            "retrieval_strategy": "semantic_similarity"
        },
        name = "augmented_generation"
    ):
        completion = openai_client.chat.completions.create(...)
    return completion.choices[0].message.content
Prompt tracking
Attach structured prompt metadata to the LLM span so you can reproduce results, audit changes, and compare prompt performance across versions. When using templates, LLM Observability also provides version tracking based on template content changes.

Python
Use LLMObs.annotation_context(prompt=...) to attach prompt metadata before the LLM call. For more details on span annotation, see Annotating a span.

Arguments
Arguments
Prompt structure
Example: single-template prompt
from ddtrace.llmobs import LLMObs

def answer_question(text):
    # Attach prompt metadata to the upcoming LLM span using LLMObs.annotation_context()
    with LLMObs.annotation_context(prompt={
        "id": "translation-template",
        "version": "1.0.0",
        "chat_template": [{"role": "user", "content": "Translate to {{lang}}: {{text}}"}],
        "variables": {"lang": "fr", "text": text},
        "tags": {"team": "nlp"}
    }):
        # Example provider call (replace with your client)
        completion = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Translate to fr: {text}"}]
        )
    return completion
Example: LangChain prompt templates
When you use LangChain’s prompt templating with auto-instrumentation, assign templates to variables with meaningful names. Auto-instrumentation uses these names to identify prompts.

# "translation_template" will be used to identify the template in Datadog
translation_template = PromptTemplate.from_template("Translate {text} to {language}")
chain = translation_template | llm
Notes
Annotating a prompt is only available on LLM spans.
Place the annotation immediately before the provider call so it applies to the correct LLM span.
Use a unique prompt id to distinguish different prompts within your application.
Keep templates static by using placeholder syntax (like {{variable_name}}) and define dynamic content in the variables section.
For multiple auto-instrumented LLM calls within a block, use LLMObs.annotation_context(prompt=...) to apply the same prompt metadata across calls. See Annotating auto-instrumented spans.
Version tracking
LLM Observability provides automatic versioning for your prompts when no explicit version is specified. When you provide a template or chat_template in your prompt metadata without a version tag, the system automatically generates a version by computing a hash of the template content. If you do provide a version tag, LLM Observability uses your specified version label instead of auto-generating one.

The versioning system works as follows:

Auto versioning: When no version tag is provided, LLM Observability computes a hash of the template or chat_template content to automatically generate a numerical version identifier
Manual versioning: When a version tag is provided, LLM Observability uses your specified version label exactly as provided
Version history: Both auto-generated and manual versions are maintained in the version history to track prompt evolution over time
This gives you the flexibility to either rely on automatic version management based on template content changes, or maintain full control over versioning with your own version labels.

Cost monitoring
Attach token metrics (for automatic cost tracking) or cost metrics (for manual cost tracking) to your LLM/embedding spans. Token metrics allow Datadog to calculate costs using provider pricing, while cost metrics let you supply your own pricing when using custom or unsupported models. For more details, see Costs.

If you’re using automatic instrumentation, token and cost metrics appear on your spans automatically. If you’re instrumenting manually, follow the guidance below.

Python
Use case: Using a common model provider
Datadog supports common model providers such as OpenAI, Azure OpenAI, Anthropic, and Google Gemini. When using these providers, you only need to annotate your LLM request with model_name, model_provider, and token usage. Datadog automatically calculates the estimated cost based on the provider’s pricing.

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm

@llm(model_name="gpt-5.1", model_provider="openai")
def llm_call(prompt):
    resp = ... # llm call here
    # Annotate token metrics
    LLMObs.annotate(
        metrics={
          "input_tokens": 50, 
          "output_tokens": 120, 
          "total_tokens": 170,
          "non_cached_input_tokens": 13,  # optional
          "cache_read_input_tokens": 22,  # optional
          "cache_write_input_tokens": 15, # optional
        },
    )
    return resp
Use case: Using a custom model
For custom or unsupported models, you must annotate the span manually with the cost data.

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm

@llm(model_name="custom_model", model_provider="model_provider")
def llm_call(prompt):
    resp = ... # llm call here
    # Annotate cost metrics
    LLMObs.annotate(
        metrics={
          "input_cost": 3, 
          "output_cost": 7, 
          "total_cost": 10,
          "non_cached_input_cost": 1,    # optional
          "cache_read_input_cost": 0.6,  # optional
          "cache_write_input_cost": 1.4, # optional
        },
    )
    return resp
Evaluations
The LLM Observability SDK provides methods to export and submit your evaluations to Datadog.

Evaluations must be joined to a single span. You can identify the target span using either of these two methods:

Tag-based joining - Join an evaluation using a unique key-value tag pair that is set on a single span. The evaluation will fail to join if the tag key-value pair matches multiple spans or no spans.
Direct span reference - Join an evaluation using the span’s unique trace ID and span ID combination.
Exporting a span
Python
Node.js
LLMObs.export_span() can be used to extract the span context from a span. This method is helpful for associating your evaluation with the corresponding span.

Arguments
The LLMObs.export_span() method accepts the following argument:

span
optional - Span
The span to extract the span context (span and trace IDs) from. If not provided (as when using function decorators), the SDK exports the current active span.
Example
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm

@llm(model_name="claude", name="invoke_llm", model_provider="anthropic")
def llm_call():
    completion = ... # user application logic to invoke LLM
    span_context = LLMObs.export_span(span=None)
    return completion
Submitting evaluations
Python
Node.js
Java
LLMObs.submit_evaluation() can be used to submit your custom evaluation associated with a given span.

LLMObs.submit_evaluation_for is deprecated and will be removed in the next major version of ddtrace (4.0). To migrate, rename your LLMObs.submit_evaluation_for calls with LLMObs.submit_evaluation.
Note: Custom evaluations are evaluators that you implement and host yourself. These differ from out-of-the-box evaluations, which are automatically computed by Datadog using built-in evaluators. To configure out-of-the-box evaluations for your application, use the LLM Observability > Settings > Evaluations page in Datadog.

The LLMObs.submit_evaluation() method accepts the following arguments:

Arguments
Example
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import llm

@llm(model_name="claude", name="invoke_llm", model_provider="anthropic")
def llm_call():
    completion = ... # user application logic to invoke LLM

    # joining an evaluation to a span via a tag key-value pair
    msg_id = get_msg_id()
    LLMObs.annotate(
        tags = {'msg_id': msg_id}
    )

    LLMObs.submit_evaluation(
        span_with_tag_value = {
            "tag_key": "msg_id",
            "tag_value": msg_id
        },
        ml_app = "chatbot",
        label="harmfulness",
        metric_type="score",
        value=10,
        tags={"evaluation_provider": "ragas"},
        assessment="fail",
        reasoning="Malicious intent was detected in the user instructions."
    )

    # joining an evaluation to a span via span ID and trace ID
    span_context = LLMObs.export_span(span=None)
    LLMObs.submit_evaluation(
        span_context = span_context,
        ml_app = "chatbot",
        label="harmfulness",
        metric_type="score",
        value=10,
        tags={"evaluation_provider": "ragas"},
        assessment="fail",
        reasoning="Malicious intent was detected in the user instructions."
    )
    return completion
Span processing
To modify input and output data on spans, you can configure a processor function. The processor function has access to span tags to enable conditional input/output modification. Processor functions can either return the modified span to emit it, or return None/null to prevent the span from being emitted entirely. This is useful for filtering out spans that contain sensitive data or meet certain criteria.

Python
Node.js
Example
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs import LLMObsSpan

def redact_processor(span: LLMObsSpan) -> LLMObsSpan:
    if span.get_tag("no_output") == "true":
        for message in span.output:
            message["content"] = ""
    return span


# If using LLMObs.enable()
LLMObs.enable(
  ...
  span_processor=redact_processor,
)
# else when using `ddtrace-run`
LLMObs.register_processor(redact_processor)

with LLMObs.llm("invoke_llm_with_no_output"):
    LLMObs.annotate(tags={"no_output": "true"})
Example: conditional modification with auto-instrumentation
When using auto instrumentation, the span is not always contextually accessible. To conditionally modify the inputs and outputs on auto-instrumented spans, annotation_context() can be used in addition to a span processor.

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs import LLMObsSpan

def redact_processor(span: LLMObsSpan) -> LLMObsSpan:
    if span.get_tag("no_input") == "true":
        for message in span.input:
            message["content"] = ""
    return span

LLMObs.register_processor(redact_processor)


def call_openai():
    with LLMObs.annotation_context(tags={"no_input": "true"}):
        # make call to openai
        ...
Example: preventing spans from being emitted
from ddtrace.llmobs import LLMObs
from ddtrace.llmobs import LLMObsSpan
from typing import Optional

def filter_processor(span: LLMObsSpan) -> Optional[LLMObsSpan]:
    # Skip spans that are marked as internal or contain sensitive data
    if span.get_tag("internal") == "true" or span.get_tag("sensitive") == "true":
        return None  # This span will not be emitted

    # Process and return the span normally
    return span

LLMObs.register_processor(filter_processor)

# This span will be filtered out and not sent to Datadog
with LLMObs.workflow("internal_workflow"):
    LLMObs.annotate(tags={"internal": "true"})
    # ... workflow logic
Tracking user sessions
Session tracking allows you to associate multiple interactions with a given user.

Python
Node.js
Java
When starting a root span for a new trace or span in a new process, specify the session_id argument with the string ID of the underlying user session, which is submitted as a tag on the span. Optionally, you can also specify the user_handle, user_name, and user_id tags.

from ddtrace.llmobs.decorators import workflow

@workflow(session_id="<SESSION_ID>")
def process_user_message():
    LLMObs.annotate(
        ...
        tags = {"user_handle": "poodle@dog.com", "user_id": "1234", "user_name": "poodle"}
    )
    return
Session tracking tags
Tag	Description
session_id	The ID representing a single user session, for example, a chat session.
user_handle	The handle for the user of the chat session.
user_name	The name for the user of the chat session.
user_id	The ID for the user of the chat session.
Distributed tracing
The SDK supports tracing across distributed services or hosts. Distributed tracing works by propagating span information across web requests.

Python
Node.js
The ddtrace library provides some out-of-the-box integrations that support distributed tracing for popular web framework and HTTP libraries. If your application makes requests using these supported libraries, you can enable distributed tracing by running:

from ddtrace import patch
patch(<INTEGRATION_NAME>=True)
If your application does not use any of these supported libraries, you can enable distributed tracing by manually propagating span information to and from HTTP headers. The SDK provides the helper methods LLMObs.inject_distributed_headers() and LLMObs.activate_distributed_headers() to inject and activate tracing contexts in request headers.

Injecting distributed headers
The LLMObs.inject_distributed_headers() method takes a span and injects its context into the HTTP headers to be included in the request. This method accepts the following arguments:

request_headers
required - dictionary
The HTTP headers to extend with tracing context attributes.
span
optional - Span - default: The current active span.
The span to inject its context into the provided request headers. Any spans (including those with function decorators), this defaults to the current active span.
Activating distributed headers
The LLMObs.activate_distributed_headers() method takes HTTP headers and extracts tracing context attributes to activate in the new service.

Note: You must call LLMObs.activate_distributed_headers() before starting any spans in your downstream service. Spans started prior (including function decorator spans) do not get captured in the distributed trace.

This method accepts the following argument:

request_headers
required - dictionary
The HTTP headers to extract tracing context attributes.
Example
client.py

from ddtrace.llmobs import LLMObs
from ddtrace.llmobs.decorators import workflow

@workflow
def client_send_request():
    request_headers = {}
    request_headers = LLMObs.inject_distributed_headers(request_headers)
    send_request("<method>", request_headers)  # arbitrary HTTP call
server.py

from ddtrace.llmobs import LLMObs

def server_process_request(request):
    LLMObs.activate_distributed_headers(request.headers)
    with LLMObs.task(name="process_request") as span:
        pass  # arbitrary server work
Advanced tracing
Python
Node.js
Tracing spans using inline methods
For each span kind, the ddtrace.llmobs.LLMObs class provides a corresponding inline method to automatically trace the operation a given code block entails. These methods have the same argument signature as their function decorator counterparts, with the addition that name defaults to the span kind (llm, workflow, etc.) if not provided. These methods can be used as context managers to automatically finish the span after the enclosed code block is completed.

Example
from ddtrace.llmobs import LLMObs

def process_message():
    with LLMObs.workflow(name="process_message", session_id="<SESSION_ID>", ml_app="<ML_APP>") as workflow_span:
        ... # user application logic
    return
Persisting a span across contexts
To manually start and stop a span across different contexts or scopes:

Start a span manually using the same methods (for example, the LLMObs.workflow method for a workflow span), but as a plain function call rather than as a context manager.
Pass the span object as an argument to other functions.
Stop the span manually with the span.finish() method. Note: the span must be manually finished, otherwise it is not submitted.
Example
from ddtrace.llmobs import LLMObs

def process_message():
    workflow_span = LLMObs.workflow(name="process_message")
    ... # user application logic
    separate_task(workflow_span)
    return

def separate_task(workflow_span):
    ... # user application logic
    workflow_span.finish()
    return
Force flushing in serverless environments
LLMObs.flush() is a blocking function that submits all buffered LLM Observability data to the Datadog backend. This can be useful in serverless environments to prevent an application from exiting until all LLM Observability traces are submitted.

Tracing multiple applications
The SDK supports tracing multiple LLM applications from the same service.

You can configure an environment variable DD_LLMOBS_ML_APP to the name of your LLM application, which all generated spans are grouped into by default.

To override this configuration and use a different LLM application name for a given root span, pass the ml_app argument with the string name of the underlying LLM application when starting a root span for a new trace or a span in a new process.

from ddtrace.llmobs.decorators import workflow

@workflow(name="process_message", ml_app="<NON_DEFAULT_ML_APP_NAME>")
def process_message():
    ... # user application logic
    return
Application naming guidelines
Your application name (the value of DD_LLMOBS_ML_APP) must follow these guidelines:

Must be a lowercase Unicode string
Can be up to 193 characters long
Cannot contain contiguous or trailing underscores
Can contain the following characters:
Alphanumerics
Underscores
Minuses
Colons
Periods
Slashes
Further Reading
Additional helpful documentation, links, and articles:

Track, compare, and optimize your LLM prompts with Datadog LLM Observability
BLOG
more
Language

Datadog Site

Site help
edit Edit
On this Page

Overview
Setup
Manual instrumentation
Nesting spans
Enriching spans
Prompt tracking
Cost monitoring
Evaluations
Span processing
Tracking user sessions
Distributed tracing
Advanced tracing
Application naming guidelines
Further Reading
Can't find something?
Our friendly, knowledgeable solutions engineers are here to help!

Download mobile app

Product

Infrastructure Monitoring
Network Monitoring
Container Monitoring
Serverless
Cloud Cost Management
Cloudcraft
Kubernetes Autoscaling
Application Performance Monitoring
Software Catalog
Universal Service Monitoring
Data Streams Monitoring
Data Jobs Monitoring
Database Monitoring
Continuous Profiler
Dynamic Instrumentation
Log Management
Sensitive Data Scanner
Audit Trail
Observability Pipelines
Cloud Security
Cloud Security Posture Management
Workload Protection
Cloud Infrastructure Entitlement Management
Vulnerability Management
Compliance
App and API Protection
Software Composition Analysis
Code Security
Static Code Analysis (SAST)
Runtime Code Analysis (IAST)
IaC Security
Cloud SIEM
Browser Real User Monitoring
Mobile Real User Monitoring
Product Analytics
Session Replay
Synthetic Monitoring
Mobile App Testing
Continuous Testing
Error Tracking
CloudPrem
Internal Developer Portal
CI Visibility
Test Optimization
Feature Flags
Service Level Objectives
Incident Response
Event Management
Case Management
Bits AI Agents
Bits AI SRE
Metrics
Watchdog
LLM Observability
AI Integrations
Workflow Automation
App Builder
CoScreen
Teams
Dashboards
Notebooks
Mobile App
Fleet Automation
Access Control
OpenTelemetry
Alerts
integrations
IDE Plugins
API
Marketplace
Security Labs Research
Open Source Projects
Storage Management
DORA Metrics
Secret Scanning
resources

Pricing
Documentation
Support
Services & Enablement
Product Preview Program
Certification
Open Source
Events and Webinars
Security
Privacy Center
Knowledge Center
Learning Resources
About

Contact Us
Partners
Press
Leadership
Careers
Legal
Investor Relations
Analyst Reports
ESG Report
Vendor Help
Trust Hub
Blog

The Monitor
Engineering
AI
Security Labs
 
English
© Datadog 2026
Terms
 | 
Privacy
 | 
Cookies

Feedback