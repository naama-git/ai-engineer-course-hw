
import json
import os
import traceback
from dotenv import load_dotenv
from groq import Groq
import gradio as gr
import re

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

def read_markdown_file(prommpt_nm):
    """פונקציה לקריאת קובץ ה-Markdown"""
    try:
        with open(f'./prompts/prom{prommpt_nm}.md', 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "return: Error in my content. please try again later."


def agent(query):
    systemPrompt = read_markdown_file(3)
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": systemPrompt},
                {"role": "user", "content": query},
            ],
            model="llama-3.3-70b-versatile", 
            temperature=0
        )
        raw_content = chat_completion.choices[0].message.content
        print(f"\n--- Raw Response from Groq ---\n{raw_content}")
        
        # fixed_content = raw_content.replace("\\", "\\\\")
        data = json.loads(raw_content)
        
        command = data.get("command", "No command found")
        
        formatted_response = f"### 💻 Suggested Command:\n```bash\n{command}\n```"
        return formatted_response

    except json.JSONDecodeError:
        try:
            
            clean_content = re.sub(r'```json|```', '', raw_content).strip()
            data = json.loads(clean_content)
        except Exception:
            return "Error: Could not parse JSON even after cleanup."
    except Exception as e:
        return f"Error: {str(e)}"


with gr.Blocks(theme=gr.themes.Soft()) as demo:
    # gr.Markdown("# אפליקציית Groq עם System Prompt מקובץ MD")
    
    with gr.Row():
        input_text = gr.Textbox(label="What your question about CLI command?", placeholder="type here...", lines=3)
    
    submit_btn = gr.Button("send", variant="primary")
    output_text = gr.Markdown(label="response: ")

   
    submit_btn.click(fn=agent, inputs=input_text, outputs=output_text)


if __name__ == "__main__":
    demo.launch()
