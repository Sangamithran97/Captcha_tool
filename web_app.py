import os
import asyncio
from flask import Flask, render_template, jsonify, request
from fastmcp import Client
from fastmcp.client import StdioTransport

app = Flask(__name__)

# Create a persistent transport and client
transport = StdioTransport("python3", ["mcp_server.py"])
client = Client(transport=transport)

# Start the client once at startup
loop = asyncio.get_event_loop()
loop.run_until_complete(client.__aenter__())

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate")
def generate():
    async def run_tool():
        result = await client.call_tool("generate_captcha")
        return result

    try:
        result = loop.run_until_complete(run_tool())
        print("🔍 MCP Response:", result)

        if hasattr(result, "structured_content") and isinstance(result.structured_content, dict):
            image_data = result.structured_content.get("image")
            captcha_id = result.structured_content.get("id")
            if image_data and captcha_id:
                return jsonify({"image": image_data, "id": captcha_id})
            else:
                return jsonify({"error": "Missing image or ID in structured_content"})
        else:
            return jsonify({"error": "No structured_content found in response"})
    except Exception as e:
        print(f"❌ Error generating captcha: {e}")
        return jsonify({"error": str(e)})

@app.route("/verify", methods=["POST"])
def verify():
    async def run_tool(cid, user_input):
        result = await client.call_tool("verify_captcha", {
            "captcha_id": cid,
            "user_input": user_input
        })
        return result

    try:
        data = request.get_json()
        cid = data.get("id")
        user_input = data.get("input")
        result = loop.run_until_complete(run_tool(cid, user_input))

        if hasattr(result, "structured_content") and isinstance(result.structured_content, dict):
            return jsonify({"result": result.structured_content.get("result", "Wrong")})
        else:
            return jsonify({"result": "Wrong"})
    except Exception as e:
        print(f"❌ Error verifying captcha: {e}")
        return jsonify({"result": "Wrong"})

@app.route("/break", methods=["POST"])
def break_captcha():
    async def run_tool(image_b64):
        result = await client.call_tool("break_captcha", {
            "captcha_image_base64": image_b64
        })
        return result

    try:
        data = request.get_json()
        image_b64 = data.get("image")
        if not image_b64:
            return jsonify({"error": "Missing image"})

        result = loop.run_until_complete(run_tool(image_b64))

        if hasattr(result, "structured_content") and isinstance(result.structured_content, dict):
            return jsonify(result.structured_content)
        else:
            return jsonify({"guess": result})
    except Exception as e:
        print(f"❌ Error breaking captcha: {e}")
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    print("🚀 Starting Flask + MCP app...")
    app.run(debug=True)
