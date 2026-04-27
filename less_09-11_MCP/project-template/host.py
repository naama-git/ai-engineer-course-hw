import os
os.environ['PYTHONHTTPSVERIFY'] = '0'
import certifi
import ssl

import truststore
truststore.inject_into_ssl()

os.environ['SSL_CERT_FILE'] = certifi.where()
os.environ['REQUESTS_CA_BUNDLE'] = certifi.where()

ssl._create_default_https_context = ssl._create_unverified_context

import asyncio
from contextlib import AsyncExitStack
from typing import Any
from google import genai
from google.genai import types
from client import MCPClient
from dotenv import load_dotenv

load_dotenv()

class ChatHost:
    def __init__(self):
        self.mcp_clients: list[MCPClient] = [MCPClient("./weather_Israel.py")]
        self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
        self.clients_connected = False
        self.exit_stack = AsyncExitStack()

        
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        self.model = os.environ["GEMINI_MODEL"]

        with open("system_prompt.txt", "r", encoding="utf-8") as f:
            self.system_prompt = f.read()

    async def connect_mcp_clients(self):
        """Connect all configured MCP clients once."""
        if self.clients_connected:
            return

        for client in self.mcp_clients:
            if client.session is None:
                await client.connect_to_server()

        if not self.mcp_clients:
            raise RuntimeError("No MCP clients are connected")

        self.clients_connected = True


    async def get_available_tools(self) -> list[dict[str, Any]]:
        """Collect tools from all MCP clients and map them back to their owner."""
        await self.connect_mcp_clients()
        self.tool_clients = {}
        google_tools = []

        for client in self.mcp_clients:
            if client.session is None:
                print(f"Warning: MCP client {client.client_name} is not connected, skipping")
                continue

            try:
                response = await client.session.list_tools()
                for tool in response.tools:
                    exposed_name = f"{client.client_name}__{tool.name}"
                    if exposed_name in self.tool_clients:
                        raise RuntimeError(f"Duplicate tool name detected: {exposed_name}")

                    self.tool_clients[exposed_name] = (client, tool.name)

                    def sanitize(obj):
                        if isinstance(obj, dict):
                            new_dict = {}
                            for k, v in obj.items():
                                if k in ['title', 'default', '$schema', 'definitions', 'examples']:
                                    continue
                                
                                if k == 'type':
                                    if v == 'number':
                                        new_dict[k] = 'NUMBER'
                                    elif isinstance(v, list):
                                        new_dict[k] = v[0]
                                    else:
                                        new_dict[k] = v
                                else:
                                    new_dict[k] = sanitize(v)
                            return new_dict
                        elif isinstance(obj, list):
                            return [sanitize(item) for item in obj]
                        return obj
                    params = sanitize(tool.inputSchema)
        
                    formatted_parameters = {
                        "type": "OBJECT",
                        "properties": params.get("properties", {}),
                        "required": params.get("required", [])
                    }

                    tool_def = {
                    "name": exposed_name,
                    "description": f"[{client.client_name}] {tool.description}",
                    "parameters": formatted_parameters
                }
                google_tools.append(tool_def)

            except Exception as e:
                print(f"Warning: Failed to get tools from {client.client_name}: {str(e)}")
                continue

        if not google_tools:
            raise RuntimeError("No tools available from any MCP client")

        return google_tools


    async def process_query(self, query: str) -> str:
        """Process a query using Gemini and available tools"""
        tools_list = await self.get_available_tools() 
        
        config = types.GenerateContentConfig(
        tools=[{"function_declarations": tools_list}],
        system_instruction=self.system_prompt
        )
        
        chat = self.client.chats.create(model=self.model, config=config)
        
        response = chat.send_message(query)
        final_text = []

        while response.function_calls:
            print(f"🤖 Gemini calls: {[c.name for c in response.function_calls]}")
            tool_results = []
            for call in response.function_calls:
                tool_name = call.name
                tool_args = call.args
                
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                
                client, original_tool_name = self.tool_clients[tool_name]
                result = await client.session.call_tool(original_tool_name, tool_args)
                
                tool_results.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={"result": result.content}
                    )
                )

            response = chat.send_message(tool_results)
        
        final_text.append(response.text)
        return "\n".join(final_text)
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'q' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'q':
                    break
                
                response = await self.process_query(query)
                print("\n" + response)
                
            except Exception as e:
                print(f"\nchat_loop Error: {str(e)}")
                
    async def cleanup(self):
        """Clean up resources"""
        for client in reversed(self.mcp_clients):
            await client.cleanup()
        await self.exit_stack.aclose()
        
        
async def main():
    host = ChatHost()
    try:
        await host.chat_loop()
    finally:
        await host.cleanup()
        
if __name__ == "__main__":
    asyncio.run(main())
