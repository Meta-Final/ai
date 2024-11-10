import gradio as gr
import requests
import json
from datetime import datetime
from uuid import UUID


# Configuration
# development purpose only
BASE_URL = "http://localhost:8000"
HEADERS = {"Authorization": ""}

def format_post_data(title, content):
    return {
        "posts": [
            {
                "postId": title,
                "pages": [
                    {
                        "pageId": 0,
                        "elements": [
                            {
                                "content": content,
                                "type": 0,
                                "imageData": "",
                                "position": {
                                    "x": 185.49,
                                    "y": 4.76,
                                    "z": 0.0
                                },
                                "scale": {
                                    "x": 0.34,
                                    "y": 0.34,
                                    "z": 0.34
                                },
                                "fontSize": 105,
                                "fontFace": "SUIT-Light SDF",
                                "isUnderlined": False,
                                "isStrikethrough": False
                            },
                            {
                                "content": "",
                                "type": 1,
                                "imageData": ""
                            }
                        ]
                    }
                ]
            }
        ]
    }

def set_auth_token(user_id):
    # Get test token for development
    # response = requests.post(f"{BASE_URL}/api/v1/auth/test-token", json={"user_id": "test-user"})
    try:
        # Using query parameter instead of JSON body
        response = requests.post(f"{BASE_URL}/api/v1/auth/test-token?user_id={user_id}")
        if response.ok:
            token = response.json()["access_token"]
            HEADERS["Authorization"] = f"Bearer {token}"
            # return "✅ Authentication Success - Token: " + token[:10] + "..."
            return f"✅ Authentication Success - Token: {token}"
        return f"❌ Auth Failed: {response.text}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def create_article(title, content):
    try:
        json_data = format_post_data(title, content)
        response = requests.post(
            f"{BASE_URL}/api/v1/articles/create",
            headers=HEADERS,
            json={"json_data": json_data}
        )
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"

def update_article(article_id, title, content):
    try:
        json_data = format_post_data(title, content)
        response = requests.post(
            f"{BASE_URL}/api/v1/articles/update",
            headers=HEADERS,
            json={
                "article_id": article_id,
                "json_data": json_data
            }
        )
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"

def get_article(article_id: str):
    try:
        # Validate and convert string to UUID
        # article_uuid = article_id
        
        response = requests.post(
            f"{BASE_URL}/api/v1/articles/get",
            headers=HEADERS,
            json={"article_id": article_id}  # Convert UUID to string for JSON
        )
        print('article_id :', article_id)
        
        if response.status_code == 500:
            return f"❌ Server Error: {response.json()['detail']}"
        elif not response.ok:
            return f"❌ Error: {response.status_code} - {response.text}"
            
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    except ValueError:
        return "❌ Error: Invalid UUID format"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def delete_article(article_id):
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/articles/delete",
            headers=HEADERS,
            json={"article_id": article_id}
        )
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"

def search_articles(query, limit):
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/articles/search",
            headers=HEADERS,
            json={"query": query, "limit": limit}
        )
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"

def chat_message(session_id, message):
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/chat/message",
            headers=HEADERS,
            json={"session_id": session_id, "message": message}
        )
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"

def get_chat_history(session_id):
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/chat/history/{session_id}",
            headers=HEADERS
        )
        return json.dumps(response.json(), indent=2, ensure_ascii=False)
    except Exception as e:
        return f"Error: {str(e)}"
    
def update_token(new_token):
    HEADERS["Authorization"] = f"Bearer {new_token}"
    return f"✅ Token Updated: {new_token}"

# Create Gradio interface
with gr.Blocks() as app:
    gr.Markdown("# API Testing Interface")
    
    with gr.Tab("Authentication"):
        user_id_input = gr.Textbox(
            label="User ID",
            placeholder="Enter your user ID"
        )
        auth_status = gr.Textbox(
            label="Auth Status",
            value="Not authenticated",
            interactive=False
        )
        auth_button = gr.Button("Authenticate", variant="primary")
        auth_button.click(
            fn=set_auth_token,
            inputs=[user_id_input],
            outputs=auth_status
        )
        
    with gr.Tab("Token Editor"):
        with gr.Row():
            with gr.Column():
                current_token_display = gr.Textbox(
                    label="Current Token",
                    value=HEADERS["Authorization"],
                    interactive=False
                )
                load_token_button = gr.Button("Load Token", variant="secondary")
            new_token_input = gr.Textbox(
                label="New Token",
                placeholder="Enter new token"
            )
        update_token_status = gr.Textbox(
            label="Update Status",
            value="",
            interactive=False
        )
        update_token_button = gr.Button("Update Token", variant="primary")
        load_token_button.click(
            fn=lambda: HEADERS["Authorization"],
            inputs=[],
            outputs=current_token_display
        )
        update_token_button.click(
            fn=update_token,
            inputs=[new_token_input],
            outputs=update_token_status
        )
    
    with gr.Tab("Create Article"):
        gr.Interface(
            fn=create_article,
            inputs=[
                gr.Textbox(label="Title"),
                gr.Textbox(label="Content", lines=5)
            ],
            outputs="text",
            title="Create Article"
        )
    
    with gr.Tab("Update Article"):
        gr.Interface(
            fn=update_article,
            inputs=[
                gr.Textbox(label="Article ID"),
                gr.Textbox(label="New Title"),
                gr.Textbox(label="New Content", lines=5)
            ],
            outputs="text",
            title="Update Article"
        )
    
    with gr.Tab("Get Article"):
        gr.Interface(
            fn=get_article,
            inputs=gr.Textbox(
                label="Article ID (UUID format)",
                placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
            ),
            outputs=gr.Textbox(label="Result", lines=10),
            title="Get Article"
        )
    
    with gr.Tab("Delete Article"):
        gr.Interface(
            fn=delete_article,
            inputs=gr.Textbox(label="Article ID"),
            outputs="text",
            title="Delete Article"
        )
    
    with gr.Tab("Search Articles"):
        gr.Interface(
            fn=search_articles,
            inputs=[
                gr.Textbox(label="Search Query"),
                gr.Slider(minimum=1, maximum=100, step=1, label="Limit", value=10)
            ],
            outputs="text",
            title="Search Articles"
        )
    
    with gr.Tab("Chat"):
        with gr.Row():
            with gr.Column():
                session_id = gr.Textbox(label="Session ID")
                message = gr.Textbox(label="Message")
                send_btn = gr.Button("Send Message")
                chat_output = gr.Textbox(label="Response")
                
            with gr.Column():
                history_btn = gr.Button("Get History")
                history_output = gr.Textbox(label="Chat History")
                
        send_btn.click(
            fn=chat_message,
            inputs=[session_id, message],
            outputs=chat_output
        )
        
        history_btn.click(
            fn=get_chat_history,
            inputs=session_id,
            outputs=history_output
        )

if __name__ == "__main__":
    app.launch()