from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, Dict, Any, Type
import boto3, json


class NoInputSchema(BaseModel):
    """Schema for tools that take no arguments"""
    pass


class LambdaListFunctionsTool(BaseTool):
    name: str = "lambda_list_functions"
    description: str = "List all Lambda functions"
    args_schema: Type[BaseModel] = NoInputSchema
    _lambda: Any = PrivateAttr()

    def __init__(self, region_name: str = "eu-west-3"):
        super().__init__()
        self._lambda = boto3.client("lambda", region_name=region_name)

    def _run(self) -> str:
        try:
            response = self._lambda.list_functions()
            functions = [{
                "FunctionName": f["FunctionName"],
                "Runtime": f.get("Runtime"),
                "LastModified": f.get("LastModified")
            } for f in response.get("Functions", [])]
            return json.dumps(functions, indent=2)
        except Exception as e:
            return f"Error listing Lambda functions: {str(e)}"


class LambdaInvokeInput(BaseModel):
    function_name: str = Field(..., description="Name of the Lambda function")
    payload: Optional[Dict[str, Any]] = Field(None, description="Optional JSON payload")

class LambdaInvokeFunctionTool(BaseTool):
    name: str = "lambda_invoke_function"
    description: str = "Invoke a Lambda function with optional payload"
    args_schema: Type[BaseModel] = LambdaInvokeInput
    _lambda_client: Any = PrivateAttr()

    def __init__(self, region_name: str = "eu-west-3"):
        super().__init__()
        self._lambda_client = boto3.client("lambda", region_name=region_name)

    def _run(self, function_name: str, payload: Optional[Dict[str, Any]] = None) -> str:
        try:
            kwargs = {"FunctionName": function_name}
            if payload:
                kwargs["Payload"] = json.dumps(payload)
            response = self._lambda_client.invoke(**kwargs)
            result = {
                "StatusCode": response.get("StatusCode"),
                "ExecutedVersion": response.get("ExecutedVersion", "N/A")
            }
            if "Payload" in response:
                payload_content = response["Payload"].read().decode("utf-8")
                result["Payload"] = json.loads(payload_content) if payload_content else None
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error invoking Lambda: {str(e)}"

