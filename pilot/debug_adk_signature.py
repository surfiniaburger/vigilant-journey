import inspect
from google.adk.sessions import DatabaseSessionService

print("Inspecting DatabaseSessionService via inspect module:")
print(f"get_session signature: {inspect.signature(DatabaseSessionService.get_session)}")
print(f"delete_session signature: {inspect.signature(DatabaseSessionService.delete_session)}")
