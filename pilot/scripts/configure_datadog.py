import os
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v1.api.monitors_api import MonitorsApi
from datadog_api_client.v1.model.monitor import Monitor
from datadog_api_client.v1.model.monitor_type import MonitorType
from datadog_api_client.v1.model.monitor_options import MonitorOptions
from datadog_api_client.v1.model.monitor_thresholds import MonitorThresholds
from datadog_api_client.v1.api.dashboards_api import DashboardsApi
from datadog_api_client.v1.model.dashboard import Dashboard
from datadog_api_client.v1.model.dashboard_layout_type import DashboardLayoutType
from datadog_api_client.v1.model.widget import Widget
from datadog_api_client.v1.model.widget_definition import WidgetDefinition
from datadog_api_client.v1.model.query_value_widget_definition import QueryValueWidgetDefinition
from datadog_api_client.v1.model.query_value_widget_definition_type import QueryValueWidgetDefinitionType
from datadog_api_client.v1.model.query_value_widget_request import QueryValueWidgetRequest
from datadog_api_client.v1.model.timeseries_widget_definition import TimeseriesWidgetDefinition
from datadog_api_client.v1.model.timeseries_widget_definition_type import TimeseriesWidgetDefinitionType
from datadog_api_client.v1.model.timeseries_widget_request import TimeseriesWidgetRequest
from datadog_api_client.v1.model.widget_layout import WidgetLayout
from datadog_api_client.v1.model.widget_display_type import WidgetDisplayType
from datadog_api_client.v1.model.widget_style import WidgetStyle
from datadog_api_client.v1.model.widget_request_style import WidgetRequestStyle
from datadog_api_client.v1.model.widget_line_type import WidgetLineType
from datadog_api_client.v1.model.widget_line_width import WidgetLineWidth
from datadog_api_client.v2.api.case_management_api import CaseManagementApi
from datadog_api_client.v2.model.project_create import ProjectCreate
from datadog_api_client.v2.model.project_create_attributes import ProjectCreateAttributes
from datadog_api_client.v2.model.project_create_request import ProjectCreateRequest
from datadog_api_client.v2.model.project_resource_type import ProjectResourceType


def configure_datadog():
    print("🚀 Starting Datadog Configuration...")
    
    # Ensure keys are present
    if not os.environ.get("DD_API_KEY") or not os.environ.get("DD_APP_KEY"):
        print("❌ Error: DD_API_KEY and DD_APP_KEY must be set in environment.")
        return

    configuration = Configuration()
    with ApiClient(configuration) as api_client:
        monitors_api = MonitorsApi(api_client)
        dashboards_api = DashboardsApi(api_client)
        case_api = CaseManagementApi(api_client)

        # --- Case Management ---
        print("\n💼 Configuring Case Management...")
        project_id = ensure_project(case_api, "Alora Investigations")

        # --- Monitors ---
        print("\n🔍 Configuring Monitors...")
        
        # 1. High Latency Alert
        ensure_monitor(
            monitors_api,
            name="[Alora] High Latency Alert",
            query="avg(last_5m):p95:trace.fastapi.request.duration{service:pilot,resource:analyze,env:production} > 5",
            message=f"Latency on /analyze is critical (>5s). Check Vertex AI Quota or Cloud Run Scaling. @pagerduty-primary {{#is_alert}} @case-ALORA {{/is_alert}}",
            tags=["service:pilot", "env:production", "severity:sev-2", "managed_by:automation"],
            options=MonitorOptions(
                thresholds=MonitorThresholds(critical=5.0, warning=3.0)
            )
        )

        # 2. Security Attack Detected
        ensure_monitor(
            monitors_api,
            name="[Alora] Security Attack Detected",
            query="sum(last_5m):trace.pilot.security_block.count{service:pilot,env:production} > 10",
            message="High rate of Model Armor blocks detected. Potential Jailbreak attempt. Initiating Incident Response. {{#is_alert}} @webhook-datadog-incident @case-ALORA {{/is_alert}}",
            tags=["service:pilot", "security", "env:production", "severity:sev-3", "managed_by:automation"],
            options=MonitorOptions(
                thresholds=MonitorThresholds(critical=10.0),
                renotify_interval=60
            )
        )

        # 3. Container Memory Critical
        ensure_monitor(
            monitors_api,
            name="[Alora] Container Memory Critical",
            query="avg(last_5m):run.container.memory.utilization{service:pilot,env:production} > 0.9",
            message="Memory utilization is >90%. Service may crash (OOM). Check SessionSummarizerAgent context window. {{#is_alert}} @case-ALORA {{/is_alert}}",
            tags=["service:pilot", "infra", "env:production", "severity:sev-1", "managed_by:automation"],
            options=MonitorOptions(
                thresholds=MonitorThresholds(critical=0.9, warning=0.8)
            )
        )

        # 4. High Error Rate (NEW)
        ensure_monitor(
            monitors_api,
            name="[Alora] High Error Rate (>5%)",
            query="sum(last_5m):trace.fastapi.request.hits{service:pilot,env:production,error:true}.as_count() / sum(last_5m):trace.fastapi.request.hits{service:pilot,env:production}.as_count() > 0.05",
            message="Error rate is >5%. Immediate investigation required. Logs may indicate logic failure or unhandled exceptions. {{#is_alert}} @case-ALORA {{/is_alert}}",
            tags=["service:pilot", "quality", "env:production", "severity:sev-1", "managed_by:automation"],
            options=MonitorOptions(
                thresholds=MonitorThresholds(critical=0.05, warning=0.02)
            )
        )

        # 5. LLM Token Cost Spike (NEW)
        ensure_monitor(
            monitors_api,
            name="[Alora] High LLM Token Usage",
            query="sum(last_1h):llm.usage.total_tokens{app:alora,env:production} > 1000000",
            message="Token usage exceeded 1M in 1 hour. Verify efficient context usage in agents. {{#is_alert}} @case-ALORA {{/is_alert}}",
            tags=["service:pilot", "cost", "env:production", "severity:sev-4", "managed_by:automation"],
            options=MonitorOptions(
                thresholds=MonitorThresholds(critical=1000000.0, warning=800000.0)
            )
        )

        # --- Dashboards ---
        print("\n📊 Configuring Dashboards...")
        
        create_executive_dashboard(dashboards_api)

    print("\n✅ Datadog Configuration Complete!")


def ensure_project(api_instance, name):
    """Ensure a Case Management Project exists."""
    # Note: Search/List API for projects is limited in this client version generation.
    # We will try to create it, and handle 409 (Conflict) if it implies duplication,
    # or just assume specific key if relevant. 
    # v2 API allows creating projects. Ideally we store the ID.
    # For now, we will attempt creation with a unique key based on name hash or static.
    
    # We'll use a static key for idempotency
    key = "ALORA" 
    
    body = ProjectCreateRequest(
        data=ProjectCreate(
            attributes=ProjectCreateAttributes(
                key=key,
                name=name,
            ),
            type=ProjectResourceType.PROJECT,
        ),
    )
    
    try:
        resp = api_instance.create_project(body=body)
        print(f"   ➕ Created Project: {name} (ID: {resp.data.id})")
        return resp.data.id
    except Exception as e:
        # If error mentions "already exists" or 409, we assume it's good.
        print(f"   ℹ️  Project creation note (may already exist): {e}")
        return None


def ensure_monitor(api_instance, name, query, message, tags, options):
    """Check if monitor exists by name, update it if so, else create it."""
    # Search for existing monitor
    # Note: 'name' search is not perfect, but good enough for this script.
    # A better way is to store IDs, but this is stateless.
    existing = None
    
    # List monitors with specific tags to narrow down
    try:
        monitors = api_instance.list_monitors(tags="managed_by:automation")
        for m in monitors:
            if m.name == name:
                existing = m
                break
    except Exception as e:
        print(f"⚠️  Error searching monitors: {e}")

    body = Monitor(
        type=MonitorType.QUERY_ALERT,
        name=name,
        query=query,
        message=message,
        tags=tags,
        options=options
    )

    if existing:
        print(f"   🔄 Updating monitor: {name} (ID: {existing.id})")
        try:
            api_instance.update_monitor(existing.id, body)
            print("      ✅ Updated.")
        except Exception as e:
            print(f"      ❌ Failed to update: {e}")
    else:
        print(f"   ➕ Creating monitor: {name}")
        try:
            api_instance.create_monitor(body)
            print("      ✅ Created.")
        except Exception as e:
            print(f"      ❌ Failed to create: {e}")


def create_executive_dashboard(api_instance):
    """Create or Update the 'Alora Pilot - Executive Health' dashboard."""
    title = "Alora Pilot - Executive Health 🏥"
    description = "Unified view of AI Health, Security, and Infrastructure."
    
    # Search for dashboard
    existing_id = None
    try:
        # filter_title is not supported in v2.x generated client list_dashboards
        # Rely on the manual fallback search below or try list_dashboards()
        raise Exception("Skipping filter_title")
    except Exception as e:
        # Fallback if filter_title is creating issues or try manual filter
        print(f"⚠️  Searching dashboards manually...")
        try:
             # Try listing all and filtering manually
             all_dash = api_instance.list_dashboards()
             for d in all_dash.dashboards:
                 if d.title == title:
                     existing_id = d.id
                     break
        except Exception as inner_e:
             print(f"    Failed manual search: {inner_e}")

    # Define Widgets
    widgets = [
        # --- Row 1: LLM & Business Logic ---
        # 1. Topic Distribution (Pie)
        Widget(
            definition=TimeseriesWidgetDefinition(
                title="LLM Input Topics 🏷️",
                requests=[
                     TimeseriesWidgetRequest(
                        q="count:trace.input_topic{ml_app:alora} by {input_topic}.as_count()",
                        display_type="bars",
                    )
                ],
                type=TimeseriesWidgetDefinitionType.TIMESERIES,
            ),
            layout=WidgetLayout(x=0, y=0, width=4, height=2)
        ),
        # 2. LLM Token Usage (Area)
        Widget(
            definition=TimeseriesWidgetDefinition(
                title="LLM Token Usage 💰",
                requests=[
                    TimeseriesWidgetRequest(
                        q="sum:llm.usage.total_tokens{ml_app:alora} by {model}.as_count()",
                        display_type="area",
                    )
                ],
                type=TimeseriesWidgetDefinitionType.TIMESERIES,
            ),
            layout=WidgetLayout(x=4, y=0, width=4, height=2)
        ),
        # 3. Estimated Cost (Query Value)
        Widget(
            definition=QueryValueWidgetDefinition(
                title="Est. Total Cost ($) 💵",
                requests=[
                    QueryValueWidgetRequest(
                        q="sum:metrics.estimated_total_cost{ml_app:alora}",
                        aggregator="sum",
                        conditional_formats=[
                            {"comparator": ">", "value": 1.0, "palette": "white_on_yellow"},
                            {"comparator": ">", "value": 5.0, "palette": "white_on_red"}
                        ]
                    )
                ],
                autoscale=True,
                type=QueryValueWidgetDefinitionType.QUERY_VALUE, 
            ),
            layout=WidgetLayout(x=8, y=0, width=4, height=2)
        ),

        # --- Row 2: Operational Health ---
        # 4. Response Latency
        Widget(
            definition=QueryValueWidgetDefinition(
                title="Backend Latency (p95)",
                requests=[
                    QueryValueWidgetRequest(
                        q="p95:trace.fastapi.request.duration{service:pilot} by {env}",
                        aggregator="avg",
                        conditional_formats=[
                            {"comparator": ">", "value": 5.0, "palette": "white_on_red"},
                            {"comparator": ">", "value": 3.0, "palette": "white_on_yellow"}
                        ]
                    )
                ],
                autoscale=True,
                type=QueryValueWidgetDefinitionType.QUERY_VALUE, 
            ),
            layout=WidgetLayout(x=0, y=2, width=4, height=2)
        ),
        # 5. Security Blocks
        Widget(
            definition=TimeseriesWidgetDefinition(
                title="Model Armor Security Blocks �️",
                requests=[
                    TimeseriesWidgetRequest(
                        q="sum:trace.pilot.security_block.count{service:pilot}.as_count()",
                        display_type="bars",
                        style=WidgetRequestStyle(palette="warm", line_type="solid", line_width="normal")
                    )
                ],
                show_legend=True,
                type=TimeseriesWidgetDefinitionType.TIMESERIES,
            ),
            layout=WidgetLayout(x=4, y=2, width=4, height=2)
        ),
        # 6. Infrastructure
        Widget(
            definition=TimeseriesWidgetDefinition(
                title="Container Health (CPU/Mem)",
                requests=[
                    TimeseriesWidgetRequest(
                        q="avg:run.container.memory.utilization{service:pilot} * 100",
                    ),
                    TimeseriesWidgetRequest(
                        q="avg:run.container.cpu.utilization{service:pilot} * 100",
                    )
                ],
                type=TimeseriesWidgetDefinitionType.TIMESERIES,
            ),
            layout=WidgetLayout(x=8, y=2, width=4, height=2)
        )
    ]

    body = Dashboard(
        title=title,
        description=description,
        widgets=widgets,
        layout_type=DashboardLayoutType.ORDERED
    )

    if existing_id:
        print(f"   🔄 Updating Dashboard: {title} (ID: {existing_id})")
        try:
             api_instance.update_dashboard(existing_id, body)
             print("      ✅ Updated.")
        except Exception as e:
             print(f"      ❌ Failed to update: {e}")
    else:
        print(f"   ➕ Creating Dashboard: {title}")
        try:
             api_instance.create_dashboard(body)
             print("      ✅ Created.")
        except Exception as e:
             print(f"      ❌ Failed to create: {e}")


if __name__ == "__main__":
    configure_datadog()
