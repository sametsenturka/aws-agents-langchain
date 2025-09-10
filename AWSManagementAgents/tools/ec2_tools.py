from langchain.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, Dict, List, Type, Any
import boto3, json


class EC2ListInstancesInput(BaseModel):
    filters: Optional[Dict[str, List[str]]] = Field(
        default=None, description="Optional filters for EC2 instances"
    )

class EC2ListInstancesTool(BaseTool):
    name: str = "ec2_list_instances"
    description: str = "List all EC2 instances with their details"
    args_schema: Type[BaseModel] = EC2ListInstancesInput
    _ec2: Any = PrivateAttr()

    def __init__(self, region_name: str = "eu-north-1"):
        super().__init__()
        self._ec2 = boto3.client("ec2", region_name=region_name)

    def _run(self, filters: Optional[Dict[str, List[str]]] = None) -> str:
        try:
            kwargs = {}
            if filters:
                kwargs["Filters"] = [{'Name': k, 'Values': v} for k, v in filters.items()]
            response = self._ec2.describe_instances(**kwargs)
            instances = []
            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instances.append({
                        "InstanceId": instance["InstanceId"],
                        "State": instance["State"]["Name"],
                        "InstanceType": instance["InstanceType"],
                        "LaunchTime": instance["LaunchTime"].strftime("%Y-%m-%d %H:%M:%S"),
                        "Tags": {tag["Key"]: tag["Value"] for tag in instance.get("Tags", [])}
                    })
            return json.dumps(instances, indent=2)
        except Exception as e:
            return f"Error: {str(e)}"


class EC2StartInstanceInput(BaseModel):
    instance_id: str = Field(..., description="ID of the EC2 instance to start")

class EC2StartInstanceTool(BaseTool):
    name: str = "ec2_start_instance"
    description: str = "Start an EC2 instance"
    args_schema: Type[BaseModel] = EC2StartInstanceInput
    _ec2: Any = PrivateAttr()

    def __init__(self, region_name: str = "eu-north-1"):
        super().__init__()
        self._ec2 = boto3.client("ec2", region_name=region_name)

    def _run(self, instance_id: str) -> str:
        try:
            response = self._ec2.start_instances(InstanceIds=[instance_id])
            return json.dumps(response, default=str, indent=2)
        except Exception as e:
            return f"Error starting instance: {str(e)}"


class EC2StopInstanceInput(BaseModel):
    instance_id: str = Field(..., description="ID of the EC2 instance to stop")

class EC2StopInstanceTool(BaseTool):
    name: str = "ec2_stop_instance"
    description: str = "Stop an EC2 instance"
    args_schema: Type[BaseModel] = EC2StopInstanceInput
    _ec2: Any = PrivateAttr()

    def __init__(self, region_name: str = "eu-north-1"):
        super().__init__()
        self._ec2 = boto3.client("ec2", region_name=region_name)

    def _run(self, instance_id: str) -> str:
        try:
            response = self._ec2.stop_instances(InstanceIds=[instance_id])
            return json.dumps(response, default=str, indent=2)
        except Exception as e:
            return f"Error stopping instance: {str(e)}"


