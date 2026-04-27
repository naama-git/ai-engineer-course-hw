import asyncio
from contextlib import AsyncExitStack
from typing import Any

import httpx

import google.generativeai as genai
import os
from client import MCPClient
from dotenv import load_dotenv

load_dotenv()


class ChatHost:
    def __init__(self):
        self.mcp_clients: list[MCPClient] = [MCPClient("./weather_USA.py")]
        self.tool_clients: dict[str, tuple[MCPClient, str]] = {}
        self.clients_connected = False
        self.exit_stack = AsyncExitStack()
        genai.configure(api_key=os.environ["GEMINI_API_KEY"], 
                    transport="rest")
        # For Netfree
        transport = httpx.HTTPTransport(verify=False)
        self.model = genai.GenerativeModel(os.environ["GEMINI_MODEL"])

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
                    tool_def = {
                    "name": exposed_name,
                    "description": f"[{client.client_name}] {tool.description}",
                    "parameters": tool.inputSchema # שים לב: שינוי מ-input_schema ל-parameters
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
        
        chat = self.model.start_chat(history=[])
        
        response = await chat.send_message_async(query, tools=tools_list)
        final_text = []

        while True:
            if not response.candidates[0].content.parts or not any(p.function_call for p in response.candidates[0].content.parts):
                final_text.append(response.text)
                break

            tool_results = []
            for part in response.candidates[0].content.parts:
                if fn := part.function_call:
                    tool_name = fn.name
                    tool_args = dict(fn.args)
                    
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                    
                    client, original_tool_name = self.tool_clients[tool_name]
                    result = await client.session.call_tool(original_tool_name, tool_args)

                    tool_results.append(
                        genai.types.Part.from_function_response(
                            name=tool_name,
                            response={"result": result.content}
                        )
                    )

            response = await chat.send_message_async(tool_results)

        return "\n".join(final_text)
    
    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
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
