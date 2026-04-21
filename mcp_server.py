import os, io, base64, random, string, uuid
from fastmcp import FastMCP
from PIL import Image, ImageDraw, ImageFont
import pytesseract
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
GENAI_KEY = os.getenv("GOOGLE_API_KEY")
if not GENAI_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env")

genai.configure(api_key=GENAI_KEY)

mcp = FastMCP("Captcha Tools")
CAPTCHA_STORE = {}
RECENT_CAPTCHAS = set()

def generate_random_text(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def get_unique_text():
    model = genai.GenerativeModel("gemini-2.0-flash")
    prompt = (
        "Generate a truly random 6-character alphanumeric string using both uppercase and lowercase letters. "
        "Avoid repeating previous outputs. Do not use dictionary words or common sequences. "
        "Only return the string, no explanation."
    )
    for _ in range(5):
        resp = model.generate_content(prompt)
        text = ''.join(filter(str.isalnum, resp.text.upper()))[:6]
        if text not in RECENT_CAPTCHAS:
            RECENT_CAPTCHAS.add(text)
            return text
    return generate_random_text(6).upper()

def text_to_image_base64(text: str, w=600, h=200) -> str:
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)

    try:
        font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
        font = ImageFont.truetype(font_path, 130)
    except:
        font = ImageFont.load_default()

    for _ in range(4):
        points = [(random.randint(0, w), random.randint(0, h)) for _ in range(3)]
        color = tuple(random.randint(100, 200) for _ in range(3))
        d.line(points, fill=color, width=3)

    for _ in range(200):
        x, y = random.randint(0, w), random.randint(0, h)
        color = tuple(random.randint(150, 200) for _ in range(3))
        d.point((x, y), fill=color)

    spacing = (w - 60) // len(text)
    for i, ch in enumerate(text):
        x = 30 + i * spacing + random.randint(-10, 10)
        y = 10 + random.randint(-10, 10)
        color = tuple(random.randint(0, 150) for _ in range(3))
        angle = random.randint(-25, 25)

        char_img = Image.new("RGBA", (200, 200), (255, 255, 255, 0))
        char_draw = ImageDraw.Draw(char_img)
        char_draw.text((20, 20), ch, font=font, fill=color)
        rotated = char_img.rotate(angle, expand=1)
        img.paste(rotated, (x, y), rotated)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

@mcp.tool(description="Generate a CAPTCHA image (returns ID, text, and base64 image).")
async def generate_captcha() -> dict:
    print("[SERVER] Generating new captcha...")
    try:
        text = get_unique_text()
    except Exception:
        text = generate_random_text(6).upper()

    cid = str(uuid.uuid4())
    CAPTCHA_STORE[cid] = text
    img_b64 = text_to_image_base64(text)
    print(f"[SERVER] CAPTCHA generated: {cid} ({text})")
    return {"id": cid, "text": text, "image": img_b64}

@mcp.tool(description="Verify a CAPTCHA input by ID.")
async def verify_captcha(captcha_id: str, user_input: str) -> str:
    print(f"[SERVER] Verifying captcha {captcha_id}...")
    stored = CAPTCHA_STORE.get(captcha_id)
    if not stored:
        return "Wrong"
    ok = user_input.strip().upper() == stored.strip().upper()
    if ok:
        del CAPTCHA_STORE[captcha_id]  # Only delete if correct
    return "Correct" if ok else "Wrong"

@mcp.tool(description="Use Gemini to break CAPTCHA image, fallback to OCR if needed. Returns guess and source.")
async def break_captcha(captcha_image_base64: str) -> dict:
    print("[SERVER] Attempting to break captcha via Gemini...")
    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        img_bytes = base64.b64decode(captcha_image_base64.split(",", 1)[1])
        img = Image.open(io.BytesIO(img_bytes))

        prompt = (
            "Read the CAPTCHA image and return the most likely 6-character alphanumeric string. "
            "If unsure, return your best guess. Only return the string."
        )
        resp = model.generate_content([prompt, img])
        gemini_guess = ''.join(filter(str.isalnum, resp.text.upper()))[:6]

        if gemini_guess and len(gemini_guess) >= 4:
            print(f"[SERVER] Gemini guessed: {gemini_guess}")
            return {"guess": gemini_guess, "source": "Gemini"}
        else:
            print("[SERVER] Gemini failed or uncertain, falling back to OCR...")
            img_gray = img.convert("L")
            ocr_text = pytesseract.image_to_string(img_gray)
            ocr_guess = ''.join(filter(str.isalnum, ocr_text)).upper()[:6]
            print(f"[SERVER] OCR guessed: {ocr_guess}")
            return {"guess": ocr_guess or "Error", "source": "OCR"}

    except Exception as e:
        print(f"[SERVER] CAPTCHA break failed: {e}")
        return {"guess": "Error", "source": "Error"}

if __name__ == "__main__":
    print("🚀 Starting Captcha MCP Server via stdio...")
    mcp.run()
