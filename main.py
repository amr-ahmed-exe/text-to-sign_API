import collections
import collections.abc
collections.Iterable = collections.abc.Iterable

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse          # ← جديد
from fastapi.middleware.cors import CORSMiddleware
import os, argparse, sys, json, math

sys.path.append("./")
from onmt.opts import translate_opts
from onmt.translate.translator import build_translator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── تنظيف NaN ──
def clean_nan(obj):
    if isinstance(obj, float):
        return 0.0 if not math.isfinite(obj) else obj
    if isinstance(obj, dict):
        return {k: clean_nan(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clean_nan(i) for i in obj]
    return obj

# ── تحميل الـ gloss keypoints database ──
print("Loading gloss keypoints database... ⏳")
with open("gloss_keypoints.json", "r") as f:
    raw = f.read()
raw = raw.replace(": NaN", ": 0.0").replace(":NaN", ":0.0")
GLOSS_DB = clean_nan(json.loads(raw))
print(f"✅ Loaded {len(GLOSS_DB)} glosses!")

print("Loading fingerspelling keypoints... ⏳")
with open("fingerspelling_keypoints.json", "r") as f:
    raw2 = f.read()
raw2 = raw2.replace(": NaN", ": 0.0").replace(":NaN", ":0.0")
finger_db = clean_nan(json.loads(raw2))
GLOSS_DB.update(finger_db)

print("Loading numbers keypoints... ⏳")
with open("numbers_keypoints.json", "r") as f:
    raw3 = f.read()
raw3 = raw3.replace(": NaN", ": 0.0").replace(":NaN", ":0.0")
number_db = clean_nan(json.loads(raw3))
GLOSS_DB.update(number_db)

print(f"✅ Total glosses + letters + numbers: {len(GLOSS_DB)}")

# ── تحميل الـ AI model ──
print("Loading SignTranslate ASL Model... ⏳")
parser = argparse.ArgumentParser()
translate_opts(parser)
opt = parser.parse_args([
    '-model', 'models/asl_transformer_step_12500.pt',
    '-src', 'dummy.txt',
    '-replace_unk',
    '-beam_size', '4',
    '-gpu', '-1'
])
translator = build_translator(opt, report_score=False)
print("✅ Model loaded successfully!")

# ── Endpoint ──
@app.websocket("/ws/translate")
async def translate_to_3d(websocket: WebSocket):
    await websocket.accept()
    print("🔌 Client connected to WebSocket")
    try:
        while True:
            data = await websocket.receive_json()
            text = data.get("text", "")
            print(f"📥 Text='{text}'")

            words = text.strip().upper().split()
            result = []
            for word in words:
                if word in GLOSS_DB:
                    result.append({
                        "gloss": word,
                        "type": "word",
                        "pose":       GLOSS_DB[word]["pose"],
                        "right_hand": GLOSS_DB[word]["right_hand"],
                        "left_hand":  GLOSS_DB[word]["left_hand"],
                    })
                else:
                    print(f"⚠️ Word not found: {word}, falling back to fingerspelling...")
                    for char in word:
                        if char in GLOSS_DB:
                            result.append({
                                "gloss": f"[{char}]",
                                "type": "letter",
                                "pose": GLOSS_DB[char]["pose"],
                                "right_hand": GLOSS_DB[char]["right_hand"],
                                "left_hand": GLOSS_DB[char]["left_hand"],
                            })
                        else:
                            print(f"⚠️ Character not found in DB: {char}")

            # ── Debug Info ──
            for item in result[:1]:
                pose_nonzero = [p for p in item['pose'] if p['x'] != 0 or p['y'] != 0]
                rhand_nonzero = [p for p in item['right_hand'] if p['x'] != 0 or p['y'] != 0]
                print(f"Gloss: {item['gloss']}, Type: {item.get('type')}")
                print(f"  pose non-zero points: {len(pose_nonzero)}")
                print(f"  right_hand non-zero points: {len(rhand_nonzero)}")

            print(f"📤 Sending {len(result)} frames/glosses")
            await websocket.send_json({"glosses": result})

    except WebSocketDisconnect:
        print("🔌 Client disconnected")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        try:
            await websocket.send_json({"error": str(e)})
        except:
            pass

@app.get("/")
def read_root():
    return {"message": "Server is running! 🚀"}
# trigger reload