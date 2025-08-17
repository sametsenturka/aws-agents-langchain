import os
from dotenv import load_dotenv

from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from tools.ec2_tools import EC2ListInstancesTool
from tools.ec2_tools import EC2StartInstanceTool
from tools.ec2_tools import EC2StopInstanceTool

from tools.s3_tools import S3UploadFileTool
from tools.s3_tools import S3DownloadFileTool
from tools.s3_tools import S3ListBucketsTool

from tools.lambda_tools import LambdaInvokeFunctionTool
from tools.lambda_tools import LambdaListFunctionsTool


load_dotenv()

class AWSAgent:
    def __init__(self, region_name="eu-north-1"):
        self.region_name = region_name
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = [
            EC2ListInstancesTool(region_name),
            EC2StartInstanceTool(region_name),
            EC2StopInstanceTool(region_name),
            S3ListBucketsTool(region_name),
            S3UploadFileTool(region_name),
            S3DownloadFileTool(region_name),
            LambdaListFunctionsTool(region_name),
            LambdaInvokeFunctionTool(region_name)
        ]

        self.agent = self._create_agent()

    def _create_agent(self) -> AgentExecutor:

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Cloud Management AI Agent. 
        You have access to the following AWS services and actions:

        - **EC2**: list, start, stop instances
        - **S3**: list buckets, upload files, download files
        - **Lambda**: list functions, invoke functions

        Guidelines:
        - If the user request is ambiguous, always ask for clarification before acting.
        - Provide clear, helpful, and concise responses.
        - When describing actions, explain what you are doing in plain language.
        - Only use the available tools for execution.
        """),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])

        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(agent=agent, tools=self.tools, verbose=True)

    def execute_command(self, command: str) -> str:
        return self.agent.invoke({"input": command})["output"]
