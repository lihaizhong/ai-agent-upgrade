import os
from dotenv import load_dotenv
from daytona import Daytona
from langchain_daytona import DaytonaSandbox

load_dotenv(verbose=True)

os.environ["LANGSMITH_TRACING"] = os.getenv("LANGSMITH_TRACING") or "true"
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY") or "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"

sandbox = Daytona().create()
backend = DaytonaSandbox(sandbox=sandbox)

result = backend.execute("echo ready")

print(result)
