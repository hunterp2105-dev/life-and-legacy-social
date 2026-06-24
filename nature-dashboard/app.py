import streamlit as st
import requests
import time
import io
import os
from datetime import datetime
import zoneinfo
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

try:
    import anthropic as _anthropic_lib
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    from moviepy import VideoFileClip, AudioFileClip
    MOVIEPY_AVAILABLE = True
except Exception:
    MOVIEPY_AVAILABLE = False

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

st.set_page_config(
    page_title="Content Studio",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

tz = zoneinfo.ZoneInfo("US/Central")

st.session_state.blotato_key = "blt_+mNIJaPmkuHIM72ExycUmnTu01aIjLpbCH9g5dIpW9w="

if "posts" not in st.session_state:
    st.session_state.posts = {1: {}, 2: {}, 3: {}}

BASE_URL       = "https://backend.blotato.com/v2"
IMAGE_TEMPLATE = "/base/v2/images-with-text/0ddb8655-c3da-43da-9f7d-be1915ca7818/v1"
VIDEO_TEMPLATE = "/base/v2/ai-story-video/5903fe43-514d-40ee-a060-0d6628c5f8fd/v1"

# ====================== CSS ======================
st.markdown("""
<style>
    .main {background-color: #050507;}
    .stApp {
        background: linear-gradient(135deg, #0a0a0f 0%, #1a1625 100%);
    }
    h1 {
        font-family: 'Helvetica Neue', Arial, sans-serif;
        font-weight: 700;
        letter-spacing: -2.5px;
        font-size: 44px;
        color: #f1f5f9;
        text-align: center;
        margin-bottom: 6px;
    }
    .stRadio > div { background-color: transparent !important; }
    .stRadio label { color: #e0e7ff !important; }
    .stRadio [data-baseweb="radio"] span { border-color: #6366f1 !important; }
    .stRadio [data-baseweb="radio"] span[aria-checked="true"] {
        background-color: #6366f1 !important;
        border-color: #6366f1 !important;
    }
    .stTabs [data-baseweb="tab"] { color: #cbd5e1 !important; }
    .stTabs [aria-selected="true"] {
        color: #a5b4fc !important;
        border-bottom: 3px solid #818cf8 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #818cf8 !important;
    }
    .stTextArea textarea {
        background-color: #1e2937 !important;
        color: #e2e8f0 !important;
        border: 1px solid #475569 !important;
    }
    .stButton>button {
        background: linear-gradient(90deg, #6366f1, #8b5cf6);
        color: white;
        border-radius: 16px;
        height: 58px;
        font-weight: 600;
        font-size: 16px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
    }
    .preview-box {
        background: #0f172a;
        border: 2px dashed #475569;
        border-radius: 20px;
        padding: 60px 20px;
        text-align: center;
        min-height: 340px;
        color: #64748b;
    }
    .preset-label {
        font-size: 13px;
        color: #94a3b8;
        text-align: center;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.title("✨ Content Studio")
st.caption("Generate • Approve • Schedule across Instagram, TikTok & X")
st.divider()

tab1, tab2, tab3 = st.tabs(["✍️ Create 3 Posts", "⏰ Schedule", "🎬 Media Editor"])

suggested_quotes = [
    "The legacy we leave is the life we lived.",
    "Your story matters.",
    "Growth happens outside your comfort zone.",
    "Stay patient. Trust the process.",
    "The best view comes after the hardest climb.",
    "Not all those who wander are lost.",
    "In the end, we only regret the chances we didn't take.",
    "Do something today that your future self will thank you for.",
    "The quiet moments are where life is truly lived.",
    "Be the reason someone smiles today.",
    "You are exactly where you need to be.",
    "Nature does not hurry, yet everything is accomplished.",
    "The earth has music for those who listen.",
    "A walk in nature walks the soul back home.",
    "Every sunset is an opportunity to reset.",
    "Custom Quote"
]

video_prompt_ideas = [
    "Write a strong hook caption for this video",
    "Create an engaging Reel / TikTok caption with call to action",
    "Write a trending style caption for this video",
    "Create a storytelling caption that explains the video",
    "Make a motivational video caption",
    "Write a funny and relatable video caption",
    "Create a high energy hype caption",
    "Write a call-to-action focused caption",
    "Make an educational / value-packed caption",
    "Create a question style caption to boost comments",
    "Write a behind the scenes personal caption",
    "Make a luxurious / aesthetic video caption",
    "Write a viral style short caption",
    "Create a voiceover-style narration caption",
    "Write a caption that builds suspense or curiosity",
]

# ====================== CREATE TAB ======================
with tab1:
    st.subheader("Today's Posts")

    for i in range(1, 4):
        with st.container(border=True):
            st.markdown(f"### Post {i}")

            mode = st.radio("Creation Method",
                            ["🎨 Generate New with Blotato",
                             "📤 Upload Raw Media (My Own Creation)"],
                            horizontal=True, key=f"mode_{i}")

            prompt = ""
            media_type = "📸 Photo"

            if mode == "🎨 Generate New with Blotato":
                quote_choice = st.selectbox("Suggested Quote", suggested_quotes, key=f"quote_choice_{i}")
                if quote_choice == "Custom Quote":
                    prompt = st.text_area("Write your own quote",
                                          value=st.session_state.get("selected_prompt", ""),
                                          height=80, key=f"custom_{i}")
                else:
                    prompt = quote_choice
                    st.caption(f'Using: *"{prompt}"*')
                media_type = st.radio("Media Type", ["📸 Photo", "🎥 Video"], horizontal=True, key=f"type_{i}")
                use_brand_kit = st.toggle("Use Brand Kit", value=True, key=f"brandkit_{i}",
                                          help="Turn off to skip brand kit processing — faster generation")

            else:
                raw = st.file_uploader("Upload your image or video",
                                       type=["png", "jpg", "jpeg", "mp4", "mov"], key=f"raw_{i}")
                prompt = ""
                if raw:
                    if raw.type.startswith("image"):
                        st.subheader("Quick Ideas")
                        quote_ideas = [
                            "Write a beautiful and emotional caption for this photo",
                            "Create a short powerful quote for this image",
                            "Write a deep meaningful quote about life",
                            "Make a luxurious and aesthetic caption",
                            "Create a motivational and inspiring quote",
                            "Write a relatable everyday caption",
                            "Make a dreamy and poetic caption",
                            "Create a confident and bold statement",
                            "Write a gratitude and positive vibe caption",
                            "Make a storytelling caption that sparks curiosity",
                            "Write a fun and witty caption",
                            "Create a romantic love-themed caption",
                            "Make a self-love and empowerment quote",
                            "Write a minimalist short caption",
                            "Create a nostalgic throwback caption",
                            "Make a savage/roast style caption",
                            "Write a spiritual / mindful caption",
                        ]
                        selected_idea = st.selectbox("Choose Quote Style:", quote_ideas, key=f"quote_select_{i}")
                        custom = st.text_area("Custom instructions (optional)", height=80,
                                              placeholder="Add extra details here...", key=f"custom_img_{i}")
                        final_prompt = custom.strip() if custom.strip() else selected_idea

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            quote_overlay = st.text_area("Quote to Overlay",
                                                         value=final_prompt,
                                                         height=70, key=f"quote_{i}")
                        with col2:
                            font_size = st.slider("Text Size", 40, 140, 72, key=f"size_{i}")
                        text_color = st.color_picker("Text Color", "#ffffff", key=f"color_{i}")
                        position_y = st.slider("Vertical Position (%)", 10, 90, 75, key=f"pos_{i}")
                        try:
                            img = Image.open(raw).convert("RGBA")
                            draw = ImageDraw.Draw(img)
                            try:
                                font = ImageFont.truetype("arial.ttf", font_size)
                            except:
                                try:
                                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
                                except:
                                    font = ImageFont.load_default()
                            text_width = draw.textlength(quote_overlay, font=font)
                            x = (img.width - text_width) // 2
                            y = int(img.height * (position_y / 100))
                            draw.text((x + 3, y + 3), quote_overlay, font=font, fill="#00000099")
                            draw.text((x, y), quote_overlay, font=font, fill=text_color)
                            st.image(img, use_container_width=True, caption="Live Preview — Your Quote Overlay")
                            buf = io.BytesIO()
                            img.convert("RGB").save(buf, format="JPEG")
                            st.session_state.posts[i]["raw_file"] = {
                                "bytes": buf.getvalue(),
                                "name": raw.name,
                                "type": "image/jpeg"
                            }
                        except:
                            st.image(raw, use_container_width=True)
                            st.error("Could not apply text overlay")
                        prompt = quote_overlay
                    else:
                        st.video(raw)
                        st.session_state.posts[i]["raw_file"] = {
                            "bytes": raw.getvalue(),
                            "name": raw.name,
                            "type": raw.type
                        }
                        st.subheader("🎬 Video Prompts")
                        selected_idea = st.selectbox("Choose Video Prompt:", video_prompt_ideas, key=f"video_prompt_select_{i}")
                        custom = st.text_area("Custom instructions (optional)", height=80,
                                              placeholder="Add extra details here...", key=f"custom_vid_{i}")
                        final_prompt = custom.strip() if custom.strip() else selected_idea
                        prompt = st.text_area("Caption / Quote",
                                              value=final_prompt,
                                              height=80,
                                              key=f"quote_raw_{i}")

            # ====================== GENERATE ======================
            if mode == "🎨 Generate New with Blotato":
                if st.button(f"Generate Post {i}", type="primary", use_container_width=True, key=f"gen_{i}"):
                    if not st.session_state.blotato_key:
                        st.error("API key missing.")
                    else:
                        headers = {
                            "blotato-api-key": st.session_state.blotato_key,
                            "Content-Type": "application/json"
                        }
                        template = VIDEO_TEMPLATE if media_type == "🎥 Video" else IMAGE_TEMPLATE
                        if media_type == "🎥 Video":
                            formatted_prompt = f"Warm cinematic nature video — lush forests, golden fields, flowing rivers, slow fluid camera movements, rich earthy tones, soft piano music. Narrate or display: '{prompt}'. Tone: gentle, peaceful, emotionally warm."
                        else:
                            formatted_prompt = f"Cinematic nature photo — warm golden light, rich earthy tones, beautiful landscape. Bold white text overlay: '{prompt}'"

                        def start_creation(use_prompt):
                            r = requests.post(
                                f"{BASE_URL}/videos/from-templates",
                                json={"templateId": template, "prompt": use_prompt,
                                      "inputs": {}, "title": f"Life & Legacy Post {i}",
                                      "useBrandKit": use_brand_kit},
                                headers=headers
                            )
                            r.raise_for_status()
                            return r.json().get("item", {}).get("id")

                        def poll_creation(cid, progress_bar, start_t, max_ticks=60):
                            for tick in range(max_ticks):
                                time.sleep(5)
                                elapsed = int(time.time() - start_t)
                                pct = min(5 + int((tick / max_ticks) * 90), 95)
                                progress_bar.progress(pct, text=f"⏳ Generating… {elapsed}s elapsed")
                                it = requests.get(
                                    f"{BASE_URL}/videos/creations/{cid}", headers=headers
                                ).json().get("item", {})
                                if it.get("status") == "done":
                                    urls = it.get("imageUrls") or []
                                    return urls[0] if urls else it.get("mediaUrl")
                                if it.get("status") == "creation-from-template-failed":
                                    return "FAILED"
                            return "TIMEOUT"

                        try:
                            bar = st.progress(2, text="🚀 Submitting to Blotato…")
                            start_t = time.time()
                            cid = start_creation(formatted_prompt)
                            if not cid:
                                st.error("Failed to start generation — no creation ID returned.")
                                st.stop()

                            bar.progress(5, text="⏳ Generation started…")
                            media_url = poll_creation(cid, bar, start_t)

                            if media_url == "FAILED":
                                bar.progress(5, text="⚠️ Failed — retrying with shorter prompt…")
                                cid2 = start_creation(formatted_prompt[:150])
                                if cid2:
                                    media_url = poll_creation(cid2, bar, time.time())

                            if media_url in (None, "FAILED", "TIMEOUT"):
                                bar.empty()
                                st.error("Generation failed after retry. Try a different prompt or media type.")
                            else:
                                bar.progress(100, text="✅ Done!")
                                st.session_state.posts[i] = {
                                    "media_url": media_url,
                                    "caption": prompt[:300],
                                    "type": media_type,
                                    "approved": False
                                }
                                st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")

            # ====================== PREVIEW ======================
            st.markdown("**Preview**")
            post = st.session_state.posts.get(i)
            if post and post.get("media_url"):
                if post.get("type") == "🎥 Video":
                    st.video(post["media_url"])
                else:
                    st.image(post["media_url"], use_container_width=True)
            else:
                st.markdown("<div class='preview-box'>Your media will appear here</div>", unsafe_allow_html=True)

            caption = st.text_area("Full Caption (for social media)",
                                   value=post.get("caption", "") if post else "",
                                   height=100, key=f"cap_{i}")

            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Approve Post", use_container_width=True, key=f"app_{i}"):
                    st.session_state.posts[i].update({"caption": caption, "approved": True})
                    st.success(f"Post {i} Approved!")
                    st.rerun()
            with c2:
                if st.button("❌ Reset", use_container_width=True, key=f"reset_{i}"):
                    st.session_state.posts[i] = {}
                    st.rerun()

    st.divider()
    st.subheader("Generated Posts")

    for post_id, post in list(st.session_state.posts.items()):
        if not post:
            continue
        with st.container():
            col1, col2 = st.columns([1, 3])

            with col1:
                if post.get("media_url"):
                    st.image(post["media_url"], width=180)
                elif post.get("raw_file"):
                    rf = post["raw_file"]
                    st.image(rf["bytes"] if isinstance(rf, dict) else rf, width=180)

            with col2:
                st.markdown(f"**Post {post_id}**")
                st.write((post.get("caption", "No caption yet") or "No caption yet")[:180] + "...")

                status = "✅ Approved" if post.get("approved") else "⏳ Pending"
                st.caption(f"Status: {status} | {post.get('generated_at', '')[:10]}")

                c1, c2, c3 = st.columns(3)
                with c1:
                    if st.button("Approve", key=f"app_{post_id}"):
                        st.session_state.posts[post_id]["approved"] = True
                        st.rerun()
                with c2:
                    new_cap = st.text_input("", value=post.get("caption", ""),
                                            label_visibility="collapsed", key=f"edit_{post_id}")
                    if new_cap != post.get("caption", ""):
                        st.session_state.posts[post_id]["caption"] = new_cap
                with c3:
                    if st.button("Delete", key=f"del_{post_id}", type="secondary"):
                        del st.session_state.posts[post_id]
                        st.rerun()

            st.divider()

# ====================== SCHEDULE HELPER ======================
def schedule_post(account_id, post_id, post, scheduled_time):
    api_headers = {
        "blotato-api-key": st.session_state.blotato_key,
        "Content-Type": "application/json"
    }
    media_url = post.get("media_url")

    if not media_url and post.get("raw_file"):
        try:
            rf = post["raw_file"]
            file_bytes = rf["bytes"]
            file_name = rf["name"]
            file_type = rf["type"]
            upload_resp = requests.post(
                f"{BASE_URL}/media/uploads",
                json={"filename": file_name},
                headers=api_headers
            )
            upload_resp.raise_for_status()
            data = upload_resp.json()
            requests.put(data["presignedUrl"],
                         data=file_bytes,
                         headers={"Content-Type": file_type})
            media_url = data["publicUrl"]
            st.success("Media uploaded.")
        except Exception as e:
            st.error(f"Media upload failed: {e}")
            return

    if not media_url:
        st.error("No media available to schedule.")
        return

    caption_text = post.get("caption", "")
    scheduled_iso = scheduled_time.isoformat()
    platform_config = st.session_state.get("platform_config", {})
    results = []

    for acc_id, cfg in platform_config.items():
        platform = cfg["platform"]
        text = (caption_text[:220] if platform == "twitter"
                else caption_text[:150] if platform == "tiktok"
                else caption_text)
        target = {"targetType": cfg["targetType"]}
        if platform == "tiktok":
            target.update({
                "privacyLevel": "PUBLIC_TO_EVERYONE",
                "disabledComments": False,
                "disabledDuet": False,
                "disabledStitch": False,
                "isBrandedContent": False,
                "isYourBrand": False,
                "isAiGenerated": True,
                "autoAddMusic": True
            })
        try:
            r = requests.post(f"{BASE_URL}/posts", headers=api_headers, json={
                "post": {
                    "accountId": acc_id,
                    "content": {"text": text, "mediaUrls": [media_url], "platform": platform},
                    "target": target
                },
                "scheduledTime": scheduled_iso
            })
            sub_id = r.json().get("postSubmissionId", r.text[:60])
            results.append((cfg["label"], r.status_code, sub_id))
        except Exception as e:
            results.append((cfg["label"], "error", str(e)))

    all_ok = all(str(s).startswith("2") for _, s, _ in results)
    if all_ok:
        st.success(f"✅ Post {post_id} scheduled on all platforms!")
    else:
        st.warning("Some platforms may have failed:")
    for label, status, sub_id in results:
        icon = "✅" if str(status).startswith("2") else "❌"
        st.caption(f"{icon} {label} — {sub_id}")


# ====================== SCHEDULE TAB ======================
with tab2:
    st.header("⏰ Schedule Post")

    if "accounts" not in st.session_state or not st.session_state.accounts:
        with st.spinner("Loading accounts..."):
            try:
                headers = {"blotato-api-key": st.session_state.blotato_key}
                resp = requests.get(f"{BASE_URL}/users/me/accounts", headers=headers)
                if resp.status_code == 200:
                    st.session_state.accounts = resp.json().get("items", [])
                    st.session_state.platform_config = {
                        acc["id"]: {
                            "label": f"{acc.get('username') or acc.get('name') or acc['id']} ({acc['platform'].upper()})",
                            "platform": acc["platform"],
                            "targetType": acc["platform"],
                        }
                        for acc in st.session_state.accounts
                    }
                else:
                    st.session_state.accounts = []
                    st.session_state.platform_config = {}
            except:
                st.session_state.accounts = []
                st.session_state.platform_config = {}

    accounts = st.session_state.get("accounts", [])
    if not accounts:
        st.error("No connected accounts found.")
        st.stop()

    default_account_id = accounts[0].get("id")

    approved_posts = {key: post for key, post in st.session_state.posts.items()
                      if post.get("approved")}

    if not approved_posts:
        st.warning("No approved posts yet. Generate and approve something first.")
    else:
        st.subheader("Select Post to Schedule")

        post_options = {}
        for key, post in approved_posts.items():
            caption_preview = (post.get("caption") or "No caption")[:65]
            post_options[key] = f"Post {key} — {caption_preview}..."

        selected_post_key = st.selectbox(
            "Choose Post to Schedule",
            options=list(post_options.keys()),
            format_func=lambda k: post_options[k]
        )

        if selected_post_key:
            post = approved_posts[selected_post_key]

            st.divider()
            st.subheader(f"Post {selected_post_key}")

            if post.get("caption"):
                st.write(post["caption"])

            if post.get("media_url"):
                if post.get("type") == "🎥 Video":
                    st.video(post["media_url"])
                else:
                    st.image(post["media_url"], width=400)
            elif post.get("raw_file"):
                rf = post["raw_file"]
                if isinstance(rf, dict) and "bytes" in rf:
                    st.image(rf["bytes"], width=400)
                else:
                    st.image(rf, width=400)

            col1, col2 = st.columns(2)
            with col1:
                sch_date = st.date_input("Date", datetime.now(tz).date(), key="sch_date")
            with col2:
                sch_time = st.time_input("Time (CT)",
                                         datetime.now(tz).replace(hour=10, minute=0).time(),
                                         key="sch_time")

            scheduled_time = datetime.combine(sch_date, sch_time).replace(tzinfo=tz)
            st.caption(f"**Scheduled for:** {scheduled_time.strftime('%A, %B %d at %I:%M %p CT')}")

            if st.button("🚀 Schedule This Post", type="primary", use_container_width=True):
                schedule_post(default_account_id, selected_post_key, post, scheduled_time)


# ====================== MEDIA EDITOR HELPERS ======================

NATURE_PRESETS = {
    "None": None,
    "🌅 Golden Hour": {"warm": True, "brightness": 1.1, "contrast": 1.05, "saturation": 1.3,
                        "rgb_shift": (1.15, 1.02, 0.82)},
    "🌫️ Misty":       {"blur": 1.5, "brightness": 1.2, "contrast": 0.85, "saturation": 0.9,
                        "rgb_shift": (1.0, 1.02, 1.12)},
    "✨ Ethereal":     {"blur": 0.8, "brightness": 1.35, "contrast": 0.75, "saturation": 0.6,
                        "rgb_shift": (1.05, 1.05, 1.1)},
    "🌲 Deep Forest":  {"brightness": 1.0, "contrast": 1.25, "saturation": 1.2,
                        "rgb_shift": (0.92, 1.12, 1.05)},
    "🌇 Sunset":       {"brightness": 1.05, "contrast": 1.1, "saturation": 1.4,
                        "rgb_shift": (1.2, 0.88, 0.75)},
    "🌙 Moonlit":      {"brightness": 0.85, "contrast": 1.1, "saturation": 0.35,
                        "rgb_shift": (0.9, 0.95, 1.25)},
}

TEXT_POSITIONS = {
    "Center":       lambda w, h, tw, th: ((w - tw) // 2, (h - th) // 2),
    "Top Center":   lambda w, h, tw, th: ((w - tw) // 2, int(h * 0.08)),
    "Bottom Center":lambda w, h, tw, th: ((w - tw) // 2, int(h * 0.82)),
    "Top Left":     lambda w, h, tw, th: (int(w * 0.05), int(h * 0.08)),
    "Top Right":    lambda w, h, tw, th: (int(w * 0.95) - tw, int(h * 0.08)),
    "Bottom Left":  lambda w, h, tw, th: (int(w * 0.05), int(h * 0.82)),
    "Bottom Right": lambda w, h, tw, th: (int(w * 0.95) - tw, int(h * 0.82)),
}

def me_load_font(size, bold=True):
    font_paths = [
        "arialbd.ttf" if bold else "arial.ttf",
        "Arial Bold.ttf" if bold else "Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except:
            pass
    return ImageFont.load_default()

def me_apply_preset(img, preset_name):
    cfg = NATURE_PRESETS.get(preset_name)
    if not cfg:
        return img
    img = img.convert("RGB")
    if cfg.get("blur"):
        img = img.filter(ImageFilter.GaussianBlur(radius=cfg["blur"]))
    img = ImageEnhance.Brightness(img).enhance(cfg.get("brightness", 1.0))
    img = ImageEnhance.Contrast(img).enhance(cfg.get("contrast", 1.0))
    img = ImageEnhance.Color(img).enhance(cfg.get("saturation", 1.0))
    if "rgb_shift" in cfg:
        rk, gk, bk = cfg["rgb_shift"]
        r, g, b = img.split()
        r = r.point(lambda x: min(255, int(x * rk)))
        g = g.point(lambda x: min(255, int(x * gk)))
        b = b.point(lambda x: min(255, int(x * bk)))
        img = Image.merge("RGB", (r, g, b))
    return img

def me_apply_adjustments(img, brightness=1.0, contrast=1.0, saturation=1.0, sharpness=1.0):
    img = ImageEnhance.Brightness(img).enhance(brightness)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    img = ImageEnhance.Color(img).enhance(saturation)
    img = ImageEnhance.Sharpness(img).enhance(sharpness)
    return img

def me_apply_texts(img, text_configs):
    draw = ImageDraw.Draw(img)
    for cfg in text_configs:
        text = cfg.get("text", "").strip()
        if not text:
            continue
        font_size  = cfg.get("font_size", 64)
        color      = cfg.get("color", "#ffffff")
        position   = cfg.get("position", "Bottom Center")
        shadow     = cfg.get("shadow", True)
        font       = me_load_font(font_size, bold=cfg.get("bold", True))

        # Wrap long text
        words = text.split()
        lines, current = [], ""
        for word in words:
            test = f"{current} {word}".strip()
            if draw.textlength(test, font=font) < img.width * 0.9:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        line_h = font_size + 8
        total_h = line_h * len(lines)
        max_w   = max(int(draw.textlength(l, font=font)) for l in lines)

        pos_fn = TEXT_POSITIONS.get(position, TEXT_POSITIONS["Bottom Center"])
        base_x, base_y = pos_fn(img.width, img.height, max_w, total_h)

        for idx, line in enumerate(lines):
            lw = int(draw.textlength(line, font=font))
            x  = base_x + (max_w - lw) // 2
            y  = base_y + idx * line_h
            if shadow:
                draw.text((x + 2, y + 2), line, font=font, fill="#00000099")
            draw.text((x, y), line, font=font, fill=color)
    return img

def me_process_image(raw_bytes, preset, brightness, contrast, saturation, sharpness, text_configs):
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    img = me_apply_preset(img, preset)
    img = me_apply_adjustments(img, brightness, contrast, saturation, sharpness)
    img = me_apply_texts(img, text_configs)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=95)
    return buf.getvalue()

def me_generate_voiceover_gtts(script, lang="en"):
    tts = gTTS(text=script, lang=lang, slow=False)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    return buf.getvalue()

def me_generate_voiceover_elevenlabs(script, api_key, voice_id="21m00Tcm4TlvDq8ikWAM"):
    VOICE_IDS = {
        "Rachel (Warm)":    "21m00Tcm4TlvDq8ikWAM",
        "Bella (Soft)":     "EXAVITQu4vr4xnSDxMaL",
        "Antoni (Deep)":    "ErXwobaYiN019PkySvjV",
        "Elli (Bright)":    "MF3mGyEYCl7XYWbV9V6O",
        "Josh (Natural)":   "TxGEqnHWrfWFTfGW9XjX",
    }
    vid = VOICE_IDS.get(voice_id, voice_id)
    r = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{vid}",
        headers={"xi-api-key": api_key, "Content-Type": "application/json"},
        json={"text": script, "model_id": "eleven_monolingual_v1",
              "voice_settings": {"stability": 0.55, "similarity_boost": 0.75}}
    )
    r.raise_for_status()
    return r.content

def me_analyze_with_claude(api_key, file_type, context=""):
    if not ANTHROPIC_AVAILABLE:
        return None
    client = _anthropic_lib.Anthropic(api_key=api_key)
    prompt = (
        f"You are a creative director for a nature and heartwarming social media brand. "
        f"The user has a {file_type} they want to post. Context: '{context}'\n\n"
        f"Suggest 3 short poetic quotes perfect for this content, and 2 editing style recommendations. "
        f"Format exactly as:\n"
        f"QUOTE 1: [quote]\n"
        f"QUOTE 2: [quote]\n"
        f"QUOTE 3: [quote]\n"
        f"STYLE: [one sentence style recommendation]\n"
        f"PRESET: [one of: Golden Hour / Misty / Ethereal / Deep Forest / Sunset / Moonlit]\n"
        f"CAPTION: [Instagram caption with hashtags]"
    )
    msg = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

def me_render_video(video_bytes, settings):
    if not MOVIEPY_AVAILABLE:
        return None, "moviepy not installed"
    try:
        import tempfile
        suffix = ".mp4"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
            tmp_in.write(video_bytes)
            tmp_path = tmp_in.name

        clip = VideoFileClip(tmp_path)

        # Speed
        speed = settings.get("speed", 1.0)
        if speed != 1.0:
            clip = clip.with_speed_scaled(speed)

        # Brightness/contrast via PIL frame processing
        brightness = settings.get("brightness", 1.0)
        contrast   = settings.get("contrast", 1.0)
        saturation = settings.get("saturation", 1.0)
        preset     = settings.get("preset", "None")

        def process_frame(frame):
            img = Image.fromarray(frame).convert("RGB")
            img = me_apply_preset(img, preset)
            img = me_apply_adjustments(img, brightness, contrast, saturation)
            # Apply text overlays to every frame (static text)
            texts = settings.get("text_configs", [])
            if texts:
                img = me_apply_texts(img, texts)
            import numpy as np
            return np.array(img)

        if preset != "None" or brightness != 1.0 or contrast != 1.0 or saturation != 1.0 or settings.get("text_configs"):
            clip = clip.image_transform(process_frame)

        # Voiceover
        vo_bytes = settings.get("voiceover_bytes")
        if vo_bytes:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
                tmp_audio.write(vo_bytes)
                audio_path = tmp_audio.name
            audio_clip = AudioFileClip(audio_path)
            clip = clip.set_audio(audio_clip)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_out:
            out_path = tmp_out.name

        clip.write_videofile(out_path, codec="libx264", audio_codec="aac",
                             logger=None, fps=clip.fps or 30)
        clip.close()

        with open(out_path, "rb") as f:
            result = f.read()

        os.unlink(tmp_path)
        os.unlink(out_path)
        return result, None

    except Exception as e:
        return None, str(e)

def me_upload_to_blotato(file_bytes, file_name, file_type):
    api_headers = {
        "blotato-api-key": st.session_state.blotato_key,
        "Content-Type": "application/json"
    }
    upload_resp = requests.post(
        f"{BASE_URL}/media/uploads",
        json={"filename": file_name},
        headers=api_headers
    )
    upload_resp.raise_for_status()
    data = upload_resp.json()
    requests.put(data["presignedUrl"], data=file_bytes, headers={"Content-Type": file_type})
    return data["publicUrl"]


# ====================== MEDIA EDITOR TAB ======================
with tab3:
    # Init session state
    for key, default in [
        ("me_preset", "None"),
        ("me_brightness", 1.0), ("me_contrast", 1.0),
        ("me_saturation", 1.0), ("me_sharpness", 1.0),
        ("me_texts", [{"text": "", "font_size": 64, "color": "#ffffff",
                        "position": "Bottom Center", "bold": True, "shadow": True}]),
        ("me_voiceover_bytes", None),
        ("me_rendered_bytes", None),
        ("me_rendered_type", None),
        ("me_el_key", ""),
        ("me_anthropic_key", ""),
        ("me_ai_result", None),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    st.header("🎬 Media Editor")
    st.caption("Upload · Style · Overlay · Voiceover · Render · Post")

    # ── Upload ──────────────────────────────────────────────────
    uploaded_files = st.file_uploader(
        "Drop your images or videos here",
        type=["jpg", "jpeg", "png", "mp4", "mov"],
        accept_multiple_files=True,
        key="me_uploader",
        help="Supports images (JPG, PNG) and videos (MP4, MOV)"
    )

    if not uploaded_files:
        st.markdown("<div class='preview-box' style='min-height:200px'>📁 Upload media above to get started</div>",
                    unsafe_allow_html=True)
        st.stop()

    # File selector
    file_map = {f.name: f for f in uploaded_files}
    if len(uploaded_files) > 1:
        selected_name = st.selectbox("Editing file:", list(file_map.keys()), key="me_selected")
    else:
        selected_name = uploaded_files[0].name

    current_file = file_map[selected_name]
    is_video = current_file.type.startswith("video")
    file_bytes = current_file.getvalue()

    st.divider()

    # ── Main Layout ─────────────────────────────────────────────
    preview_col, tools_col = st.columns([3, 2], gap="large")

    with preview_col:
        st.subheader("👁️ Live Preview")

        if is_video:
            st.video(current_file)
            st.caption("Video preview shows original. Click **Render** to see final output.")
        else:
            # Compute live preview every rerun
            try:
                preview_bytes = me_process_image(
                    file_bytes,
                    st.session_state.me_preset,
                    st.session_state.me_brightness,
                    st.session_state.me_contrast,
                    st.session_state.me_saturation,
                    st.session_state.me_sharpness,
                    [t for t in st.session_state.me_texts if t.get("text", "").strip()]
                )
                st.image(preview_bytes, use_container_width=True)
            except Exception as e:
                st.image(file_bytes, use_container_width=True)
                st.caption(f"Preview error: {e}")

        # Show rendered result if available
        if st.session_state.me_rendered_bytes:
            st.divider()
            st.subheader("✅ Rendered Output")
            if st.session_state.me_rendered_type == "video":
                st.video(st.session_state.me_rendered_bytes)
            else:
                st.image(st.session_state.me_rendered_bytes, use_container_width=True)

    with tools_col:
        st.subheader("🛠️ Editing Tools")

        tool = st.radio("", ["🎨 Style & Presets", "📝 Text Overlays",
                              "🎙️ Voiceover", "🤖 AI Suggestions"],
                         key="me_tool", label_visibility="collapsed")

        st.divider()

        # ── TOOL 1: Style & Presets ────────────────────────────
        if tool == "🎨 Style & Presets":

            st.markdown("**Nature Presets**")
            preset_names = list(NATURE_PRESETS.keys())
            cols = st.columns(3)
            for idx, pname in enumerate(preset_names):
                with cols[idx % 3]:
                    active = st.session_state.me_preset == pname
                    label = f"**{pname}**" if active else pname
                    if st.button(label, key=f"preset_{idx}", use_container_width=True):
                        st.session_state.me_preset = pname
                        st.rerun()

            st.caption(f"Active: **{st.session_state.me_preset}**")
            st.divider()

            st.markdown("**Fine Adjustments**")
            new_b = st.slider("☀️ Brightness", 0.3, 2.0, st.session_state.me_brightness, 0.05, key="me_b_slider")
            new_c = st.slider("🔲 Contrast",   0.3, 2.0, st.session_state.me_contrast,   0.05, key="me_c_slider")
            new_s = st.slider("🎨 Saturation", 0.0, 2.5, st.session_state.me_saturation, 0.05, key="me_s_slider")
            new_sh= st.slider("🔪 Sharpness",  0.0, 3.0, st.session_state.me_sharpness,  0.1,  key="me_sh_slider")

            if (new_b != st.session_state.me_brightness or new_c != st.session_state.me_contrast or
                    new_s != st.session_state.me_saturation or new_sh != st.session_state.me_sharpness):
                st.session_state.me_brightness = new_b
                st.session_state.me_contrast   = new_c
                st.session_state.me_saturation = new_s
                st.session_state.me_sharpness  = new_sh
                st.rerun()

            if is_video:
                st.divider()
                st.markdown("**Video Settings**")
                st.session_state["me_speed"] = st.select_slider(
                    "⚡ Speed", options=[0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0, 4.0],
                    value=st.session_state.get("me_speed", 1.0), key="me_speed_sl"
                )
                st.session_state["me_transition"] = st.selectbox(
                    "Transition", ["None", "Fade In", "Fade Out", "Fade In/Out"],
                    key="me_trans_sl"
                )

            if st.button("↺ Reset All Adjustments", key="me_reset_adj"):
                for k, v in [("me_preset","None"),("me_brightness",1.0),
                              ("me_contrast",1.0),("me_saturation",1.0),("me_sharpness",1.0)]:
                    st.session_state[k] = v
                st.rerun()

        # ── TOOL 2: Text Overlays ──────────────────────────────
        elif tool == "📝 Text Overlays":

            texts = st.session_state.me_texts
            updated = False

            for idx in range(len(texts)):
                with st.expander(f"Text Layer {idx + 1}", expanded=idx == 0):
                    t = texts[idx]
                    new_text = st.text_area("Quote / Text", value=t.get("text", ""),
                                             height=70, key=f"me_txt_{idx}",
                                             placeholder="Enter your quote here…")
                    c1, c2 = st.columns(2)
                    with c1:
                        new_size  = st.slider("Size", 20, 120, t.get("font_size", 64), key=f"me_tsz_{idx}")
                        new_color = st.color_picker("Color", t.get("color", "#ffffff"), key=f"me_tcol_{idx}")
                    with c2:
                        new_pos  = st.selectbox("Position", list(TEXT_POSITIONS.keys()),
                                                 index=list(TEXT_POSITIONS.keys()).index(
                                                     t.get("position", "Bottom Center")),
                                                 key=f"me_tpos_{idx}")
                        new_bold   = st.toggle("Bold", value=t.get("bold", True), key=f"me_tbold_{idx}")
                        new_shadow = st.toggle("Shadow", value=t.get("shadow", True), key=f"me_tshad_{idx}")

                    if is_video:
                        c3, c4 = st.columns(2)
                        with c3:
                            texts[idx]["start_time"] = st.number_input("Start (s)", 0.0, step=0.5, key=f"me_tstart_{idx}")
                        with c4:
                            texts[idx]["end_time"] = st.number_input("End (s)", 5.0, step=0.5, key=f"me_tend_{idx}")
                        texts[idx]["animation"] = st.selectbox(
                            "Animation", ["None", "Fade", "Slide Up", "Typewriter"],
                            key=f"me_tanim_{idx}"
                        )

                    changed = (new_text != t.get("text") or new_size != t.get("font_size") or
                               new_color != t.get("color") or new_pos != t.get("position") or
                               new_bold != t.get("bold") or new_shadow != t.get("shadow"))
                    if changed:
                        texts[idx].update({"text": new_text, "font_size": new_size,
                                           "color": new_color, "position": new_pos,
                                           "bold": new_bold, "shadow": new_shadow})
                        updated = True

                    if st.button("🗑 Remove", key=f"me_tdel_{idx}"):
                        texts.pop(idx)
                        st.session_state.me_texts = texts
                        st.rerun()

            if updated:
                st.session_state.me_texts = texts
                st.rerun()

            if st.button("＋ Add Text Layer", use_container_width=True, key="me_addtext"):
                st.session_state.me_texts.append({
                    "text": "", "font_size": 64, "color": "#ffffff",
                    "position": "Center", "bold": True, "shadow": True
                })
                st.rerun()

        # ── TOOL 3: Voiceover ──────────────────────────────────
        elif tool == "🎙️ Voiceover":

            script = st.text_area("Voiceover Script", height=120,
                                   placeholder="Type the narration or quote to be spoken…",
                                   key="me_vo_script")

            provider = st.radio("Provider", ["ElevenLabs", "gTTS (Free)"],
                                 horizontal=True, key="me_vo_provider")

            if provider == "ElevenLabs":
                el_key = st.text_input("ElevenLabs API Key", type="password",
                                        value=st.session_state.me_el_key,
                                        key="me_el_key_input")
                st.session_state.me_el_key = el_key
                voice = st.selectbox("Voice", ["Rachel (Warm)", "Bella (Soft)",
                                                "Antoni (Deep)", "Elli (Bright)",
                                                "Josh (Natural)"], key="me_voice")
            else:
                if not GTTS_AVAILABLE:
                    st.info("gTTS not installed — add `gtts` to requirements.txt")
                voice = None

            if st.button("🎙️ Generate Voiceover", type="primary",
                          use_container_width=True, key="me_gen_vo"):
                if not script.strip():
                    st.warning("Enter a script first.")
                else:
                    with st.spinner("Generating voiceover…"):
                        try:
                            if provider == "ElevenLabs":
                                if not st.session_state.me_el_key:
                                    st.warning("Enter your ElevenLabs API key.")
                                else:
                                    vo = me_generate_voiceover_elevenlabs(
                                        script, st.session_state.me_el_key, voice)
                                    st.session_state.me_voiceover_bytes = vo
                            else:
                                if GTTS_AVAILABLE:
                                    vo = me_generate_voiceover_gtts(script)
                                    st.session_state.me_voiceover_bytes = vo
                                else:
                                    st.error("Install gtts: `pip install gtts`")
                        except Exception as e:
                            st.error(f"Voiceover failed: {e}")

            if st.session_state.me_voiceover_bytes:
                st.success("✅ Voiceover ready")
                st.audio(st.session_state.me_voiceover_bytes, format="audio/mp3")
                if st.button("✕ Remove Voiceover", key="me_rm_vo"):
                    st.session_state.me_voiceover_bytes = None
                    st.rerun()

        # ── TOOL 4: AI Suggestions ─────────────────────────────
        elif tool == "🤖 AI Suggestions":

            ant_key = st.text_input("Anthropic API Key", type="password",
                                     value=st.session_state.me_anthropic_key,
                                     key="me_ant_input",
                                     placeholder="sk-ant-…")
            st.session_state.me_anthropic_key = ant_key

            context = st.text_area("Context (optional)", height=70,
                                    placeholder="Describe the image/video or add any notes…",
                                    key="me_ai_context")

            if st.button("🤖 Analyze & Suggest Edits", type="primary",
                          use_container_width=True, key="me_ai_btn"):
                if not st.session_state.me_anthropic_key:
                    st.warning("Enter your Anthropic API key above.")
                elif not ANTHROPIC_AVAILABLE:
                    st.error("Anthropic library not installed.")
                else:
                    with st.spinner("Analyzing with Claude…"):
                        try:
                            result = me_analyze_with_claude(
                                st.session_state.me_anthropic_key,
                                "video" if is_video else "image",
                                context
                            )
                            st.session_state.me_ai_result = result
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")

            if st.session_state.me_ai_result:
                st.divider()
                st.markdown("**✨ Claude's Suggestions**")
                result_text = st.session_state.me_ai_result
                st.text_area("", value=result_text, height=280,
                              key="me_ai_result_display", disabled=True)

                # Quick-apply preset if Claude suggested one
                for preset_key in ["Golden Hour", "Misty", "Ethereal", "Deep Forest", "Sunset", "Moonlit"]:
                    if f"PRESET: {preset_key}" in result_text:
                        preset_emoji = {
                            "Golden Hour": "🌅 Golden Hour", "Misty": "🌫️ Misty",
                            "Ethereal": "✨ Ethereal", "Deep Forest": "🌲 Deep Forest",
                            "Sunset": "🌇 Sunset", "Moonlit": "🌙 Moonlit"
                        }.get(preset_key, "None")
                        if st.button(f"Apply suggested preset: {preset_emoji}", key="me_apply_preset"):
                            st.session_state.me_preset = preset_emoji
                            st.rerun()
                        break

                # Quick-apply first quote as text overlay
                for line in result_text.splitlines():
                    if line.startswith("QUOTE 1:"):
                        quote = line.replace("QUOTE 1:", "").strip()
                        if st.button("Apply Quote 1 as text overlay", key="me_apply_q1"):
                            if st.session_state.me_texts:
                                st.session_state.me_texts[0]["text"] = quote
                            else:
                                st.session_state.me_texts = [{"text": quote, "font_size": 64,
                                    "color": "#ffffff", "position": "Bottom Center",
                                    "bold": True, "shadow": True}]
                            st.rerun()
                        break

    # ── Render & Export ──────────────────────────────────────────
    st.divider()
    st.subheader("🎬 Render & Export")

    render_col, dl_col, blotato_col = st.columns(3)

    with render_col:
        if st.button("🎬 Render Final", type="primary", use_container_width=True, key="me_render"):
            text_configs = [t for t in st.session_state.me_texts if t.get("text", "").strip()]

            if is_video:
                if not MOVIEPY_AVAILABLE:
                    st.error("moviepy is not installed. Add `moviepy` to requirements.txt and restart.")
                else:
                    bar = st.progress(0, text="🎬 Rendering video…")
                    settings = {
                        "preset":       st.session_state.me_preset,
                        "brightness":   st.session_state.me_brightness,
                        "contrast":     st.session_state.me_contrast,
                        "saturation":   st.session_state.me_saturation,
                        "speed":        st.session_state.get("me_speed", 1.0),
                        "text_configs": text_configs,
                        "voiceover_bytes": st.session_state.me_voiceover_bytes,
                    }
                    bar.progress(20, text="Processing frames…")
                    result, err = me_render_video(file_bytes, settings)
                    if err:
                        bar.empty()
                        st.error(f"Render failed: {err}")
                    else:
                        bar.progress(100, text="✅ Render complete!")
                        st.session_state.me_rendered_bytes = result
                        st.session_state.me_rendered_type  = "video"
                        st.rerun()
            else:
                bar = st.progress(0, text="🖼️ Processing image…")
                bar.progress(40, text="Applying effects…")
                try:
                    result = me_process_image(
                        file_bytes, st.session_state.me_preset,
                        st.session_state.me_brightness, st.session_state.me_contrast,
                        st.session_state.me_saturation, st.session_state.me_sharpness,
                        text_configs
                    )
                    bar.progress(100, text="✅ Done!")
                    st.session_state.me_rendered_bytes = result
                    st.session_state.me_rendered_type  = "image"
                    st.rerun()
                except Exception as e:
                    bar.empty()
                    st.error(f"Render failed: {e}")

    with dl_col:
        if st.session_state.me_rendered_bytes:
            ext  = "mp4" if st.session_state.me_rendered_type == "video" else "jpg"
            mime = "video/mp4" if ext == "mp4" else "image/jpeg"
            base = os.path.splitext(current_file.name)[0]
            st.download_button(
                "⬇️ Download",
                data=st.session_state.me_rendered_bytes,
                file_name=f"{base}_edited.{ext}",
                mime=mime,
                use_container_width=True,
                key="me_dl"
            )
        else:
            st.button("⬇️ Download", disabled=True, use_container_width=True, key="me_dl_dis")

    with blotato_col:
        if st.session_state.me_rendered_bytes:
            if st.button("📤 Send to Blotato", use_container_width=True, key="me_send"):
                with st.spinner("Uploading to Blotato…"):
                    try:
                        ext       = "mp4" if st.session_state.me_rendered_type == "video" else "jpg"
                        mime      = "video/mp4" if ext == "mp4" else "image/jpeg"
                        base      = os.path.splitext(current_file.name)[0]
                        fname     = f"{base}_edited.{ext}"
                        pub_url   = me_upload_to_blotato(
                            st.session_state.me_rendered_bytes, fname, mime)
                        # Add to posts queue for scheduling
                        next_slot = max(st.session_state.posts.keys()) + 1 \
                                    if st.session_state.posts else 1
                        st.session_state.posts[next_slot] = {
                            "media_url": pub_url,
                            "caption": "",
                            "type": "🎥 Video" if ext == "mp4" else "📸 Photo",
                            "approved": False,
                            "generated_at": datetime.now(tz).isoformat()
                        }
                        st.success(f"✅ Added to Post {next_slot} — go to Create tab to caption & approve, then Schedule.")
                    except Exception as e:
                        st.error(f"Upload failed: {e}")
        else:
            st.button("📤 Send to Blotato", disabled=True,
                       use_container_width=True, key="me_send_dis")

    # Reset rendered output if file changes
    if st.session_state.get("me_last_file") != current_file.name:
        st.session_state.me_rendered_bytes = None
        st.session_state.me_rendered_type  = None
        st.session_state["me_last_file"]   = current_file.name


st.caption("Life & Legacy Studio • Scheduling Connected")
