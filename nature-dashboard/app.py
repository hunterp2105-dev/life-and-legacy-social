import streamlit as st
import requests
import time
import io
from datetime import datetime
import zoneinfo
from PIL import Image, ImageDraw, ImageFont

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

# ====================== PREMIUM DARK THEME CSS ======================
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
    .subtitle {
        text-align: center;
        color: #cbd5e1;
        font-size: 20px;
        margin-bottom: 48px;
    }
    .card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 32px;
        margin-bottom: 32px;
    }
    /* Purple radio buttons */
    .stRadio > div { background-color: transparent !important; }
    .stRadio label { color: #e0e7ff !important; }
    .stRadio [data-baseweb="radio"] span { border-color: #6366f1 !important; }
    .stRadio [data-baseweb="radio"] span[aria-checked="true"] {
        background-color: #6366f1 !important;
        border-color: #6366f1 !important;
    }
    /* Tabs — replace green with purple */
    .stTabs [data-baseweb="tab"] { color: #cbd5e1 !important; }
    .stTabs [aria-selected="true"] {
        color: #a5b4fc !important;
        border-bottom: 3px solid #818cf8 !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #818cf8 !important;
    }
    /* Text area */
    .stTextArea textarea {
        background-color: #1e2937 !important;
        color: #e2e8f0 !important;
        border: 1px solid #475569 !important;
    }
    /* Buttons */
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
</style>
""", unsafe_allow_html=True)

# ====================== HEADER ======================
st.title("✨ Content Studio")
st.caption("Generate • Approve • Schedule across Instagram, TikTok & X")
st.divider()

tab1, tab2 = st.tabs(["✍️ Create 3 Posts", "⏰ Schedule"])

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

                            bar.progress(5, text="⏳ Generation started… (videos take 30–90s)")
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

st.caption("Life & Legacy Studio • Scheduling Connected")
