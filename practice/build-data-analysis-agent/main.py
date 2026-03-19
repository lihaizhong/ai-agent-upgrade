import os

from daytona import Daytona
from dotenv import load_dotenv
from langchain_daytona import DaytonaSandbox

load_dotenv(verbose=True)

os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING") or ""
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY") or ""

sandbox = Daytona().create()
backend = DaytonaSandbox(sandbox=sandbox)

result = backend.execute("echo ready")

print(result)
