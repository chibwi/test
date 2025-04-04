# import streamlit as st
# import os
# import json
# from PIL import Image
# from datetime import datetime
# import time

# st.set_page_config(page_title="Chat-Based Visual Inspection", layout="wide")
# st.title("💊 Chat-Based Medicine Package Visual Inspection")

# # Load simulation metadata
# with open("sim_meta.json") as f:
#     sim_meta = json.load(f)

# image_pairs = {os.path.basename(pair["user_img"]): pair for pair in sim_meta["image_pairs"]}

# # Session State Initialization
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []
# if "user_image" not in st.session_state:
#     st.session_state.user_image = None
# if "inspection_done" not in st.session_state:
#     st.session_state.inspection_done = False
# if "selected_pair" not in st.session_state:
#     st.session_state.selected_pair = None

# # Step 1: Upload an image
# st.sidebar.header("Upload Image")
# query_img = st.sidebar.file_uploader("Upload medicine package image (JPG/PNG)", type=["jpg", "jpeg", "png"])

# if query_img:
#     st.session_state.user_image = query_img
#     st.sidebar.image(query_img, caption="Your Uploaded Image", use_column_width=True)

#     if st.sidebar.button("Run Visual Inspection"):
#         filename = query_img.name
#         if filename in image_pairs:
#             st.session_state.selected_pair = image_pairs[filename]
#             st.session_state.inspection_done = True
#             st.session_state.chat_history = []
#         else:
#             st.error("❌ This image doesn't match any test data in sim_meta.json")

# # Step 2: Simulated Processing Steps
# if st.session_state.inspection_done:
#     st.header("🔄 Running Visual Inspection...")
#     progress = st.progress(0)
#     status = st.empty()

#     with st.spinner("Fetching reference image..."):
#         status.info("Step 1 of 3: Fetching reference image...")
#         time.sleep(1.5)
#         progress.progress(33)

#     with st.spinner("Aligning images..."):
#         status.info("Step 2 of 3: Aligning images...")
#         time.sleep(2)
#         progress.progress(66)

#     with st.spinner("Performing visual analysis using LLM..."):
#         status.info("Step 3 of 3: Performing visual analysis using LLM...")
#         time.sleep(2.5)
#         progress.progress(100)

#     st.success("✅ Visual inspection complete. You may now start chatting.")
#     status.empty()
#     progress.empty()

# # Step 3: Display system output and chat interface
# if st.session_state.inspection_done and st.session_state.selected_pair:
#     data = st.session_state.selected_pair
#     user_img = data["user_img"]
#     reference_img = data["reference_img"]
#     aligned_img = data["aligned_img"]
#     llm_notes = data["llm_analysis"]
#     confidence_profile = data["confidence_profile"]
#     score = data["score"]
#     chat_intro = data["chat_intro"]
#     chat_rules = data["chat_rules"]

#     st.header("📊 System Output")
#     st.markdown("Based on your uploaded image, the system has identified the best match from our database. The visual inspection involves aligning the uploaded package with the reference image and analyzing discrepancies using an LLM.")

#     with st.container():
#         col1, col2, col3 = st.columns(3)
#         with col1:
#             st.image(user_img, caption="User Image", use_column_width=True)
#         with col2:
#             st.image(reference_img, caption="Reference Image", use_column_width=True)
#         with col3:
#             st.image(aligned_img, caption="Aligned Image", use_column_width=True)

#     st.subheader("📋 LLM Visual Analysis")
#     for line in llm_notes:
#         st.markdown(f"- {line}")

#     st.subheader("🌸 Confidence Overview")
#     st.markdown(f"""
#     <div style='background-color: #000; color: #fff; padding: 20px; border-radius: 12px; text-align:center;'>
#         <div style='font-size: 28px;'>Confidence Level: <span style='color: gold;'>{score}%</span></div>
#         <div style='font-size: 18px; margin-top:10px;'>System confidence based on visual inspection indicators.</div>
#     </div>
#     """, unsafe_allow_html=True)

#     col_rings = st.columns(5)
#     for i, (k, v) in enumerate(confidence_profile.items()):
#         status_label = "危険" if v >= 80 else ("確認" if 30 < v < 80 else "安全")
#         stroke_color = "#dc3545" if status_label == "危険" else ("#007bff" if status_label == "確認" else "#28a745")
#         col_rings[i].markdown(f"""
#         <div style='text-align: center;'>
#             <svg width="80" height="80">
#                 <circle cx="40" cy="40" r="30" stroke="#ccc" stroke-width="8" fill="none" />
#                 <circle cx="40" cy="40" r="30" stroke="{stroke_color}" stroke-width="8" fill="none" stroke-dasharray="{v * 1.88},188" transform="rotate(-90 40 40)"/>
#             </svg>
#             <div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{v}%</div>
#             <div style='font-size: 16px;'>{k}</div>
#             <div style='font-size: 14px; color: {stroke_color}; font-weight: bold;'>{status_label}</div>
#         </div>
#         """, unsafe_allow_html=True)

#     st.markdown("---")
#     st.subheader("💬 Chat with Inspector AI")

#     if not st.session_state.chat_history:
#         st.session_state.chat_history.append(("assistant", chat_intro))

#     for sender, message in st.session_state.chat_history:
#         with st.chat_message(sender):
#             st.markdown(message)

#     user_input = st.chat_input("Ask about the result or packaging...")
#     if user_input:
#         st.session_state.chat_history.append(("user", user_input))
#         matched = False
#         for keyword, response in chat_rules.items():
#             if keyword.lower() in user_input.lower():
#                 st.session_state.chat_history.append(("assistant", response))
#                 matched = True
#                 break
#         if not matched:
#             st.session_state.chat_history.append(("assistant", "🤖 Sorry, I don't have a specific answer to that, but I suggest reviewing the confidence scores above."))
# else:
#     st.info("⬅️ Upload a medicine package image from the sidebar and click 'Run Visual Inspection' to begin.")
import streamlit as st
import os
import json
from openai import OpenAI
from PIL import Image
import time
import pandas as pd
import io

# Set API Key
API_KEY = os.getenv("GPT_API_KEY")
if not API_KEY:
    st.error("GPT_API_KEY environment variable is not set. Please set it to continue.")
    st.stop()

# Initialize OpenAI client
try:
    client = OpenAI(api_key=API_KEY)
except Exception as e:
    st.error(f"Failed to initialize OpenAI client: {str(e)}")
    st.stop()

# Page configuration with improved layout
st.set_page_config(
    page_title="Medicine Package Inspection", 
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for better visual appearance
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.5rem;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    .card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .confidence-high {color: #28a745;}
    .confidence-medium {color: #ffc107;}
    .confidence-low {color: #dc3545;}
    .image-comparison-container {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .chat-bubble {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .chat-bubble.user {
        background-color: #e9f7fd;
        text-align: right;
    }
    .chat-bubble.assistant {
        background-color: #f1f1f1;
        text-align: left;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">💊 Chat-Based Medicine Package Visual Inspection</h1>', unsafe_allow_html=True)

# Load metadata with better error handling
try:
    with open("sim_meta.json") as f:
        sim_meta = json.load(f)
    image_pairs = {os.path.basename(pair["user_img"]): pair for pair in sim_meta["image_pairs"]}
except FileNotFoundError:
    st.error("Metadata file (sim_meta.json) not found. Please check the file path.")
    st.stop()
except json.JSONDecodeError:
    st.error("Error parsing the metadata file. Please check the format.")
    st.stop()

# Improved session state initialization
if "app_state" not in st.session_state:
    st.session_state.app_state = {
        "chat_history": [],
        "user_image": None,
        "inspection_done": False,
        "selected_pair": None,
        "showing_help": False,
        "comparison_mode": "side_by_side"
    }

# Sidebar with improved organization
with st.sidebar:
    st.markdown('<h2 class="subheader">Controls & Options</h2>', unsafe_allow_html=True)
    
    # Tab-based sidebar organization
    tab1, tab2 = st.tabs(["Upload", "Settings"])
    
    with tab1:
        st.header("Upload Image")
        query_img = st.file_uploader(
            "Upload medicine package image (JPG/PNG)", 
            type=["jpg", "jpeg", "png"],
            help="Select an image of the medicine package you want to inspect"
        )
        
        if query_img:
            st.session_state.app_state["user_image"] = query_img
            st.image(query_img, caption="Your Uploaded Image", use_column_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Run Inspection", use_container_width=True):
                    filename = query_img.name
                    if filename in image_pairs:
                        st.session_state.app_state["selected_pair"] = image_pairs[filename]
                        st.session_state.app_state["inspection_done"] = True
                        st.session_state.app_state["chat_history"] = []
                        st.rerun()
                    else:
                        st.error("❌ Image not found in database. Please try another image or contact support.")
            with col2:
                if st.button("Reset", use_container_width=True):
                    for key in st.session_state.app_state:
                        if key != "showing_help":
                            st.session_state.app_state[key] = [] if key == "chat_history" else None
                    st.rerun()
    
    with tab2:
        st.header("Display Settings")
        comparison_modes = {
            "side_by_side": "Side by Side View",
            "overlay": "Overlay View"
        }
        st.session_state.app_state["comparison_mode"] = st.selectbox(
            "Image Comparison Mode",
            options=list(comparison_modes.keys()),
            format_func=lambda x: comparison_modes[x]
        )
        
        st.checkbox("Show Help Tips", value=False, key="show_help_tips")
        if st.session_state.show_help_tips:
            st.session_state.app_state["showing_help"] = True
        else:
            st.session_state.app_state["showing_help"] = False
        
        # Export chat button
        if st.session_state.app_state["chat_history"]:
            if st.button("Export Chat History"):
                chat_text = "\n\n".join([f"{'You' if sender == 'user' else 'AI'}: {message}" 
                                        for sender, message in st.session_state.app_state["chat_history"]])
                
                buffer = io.StringIO()
                buffer.write(chat_text)
                buffer.seek(0)
                st.download_button(
                    label="Download Chat",
                    data=buffer,
                    file_name="inspection_chat_history.txt",
                    mime="text/plain"
                )

# Main content area
if st.session_state.app_state["inspection_done"]:
    if not st.session_state.app_state["selected_pair"]:
        with st.container():
            st.markdown('<h2 class="subheader">🔄 Running Visual Inspection...</h2>', unsafe_allow_html=True)
            progress = st.progress(0)
            status_container = st.empty()
            
            steps = [
                {"progress": 20, "message": "Preprocessing image...", "delay": 0.8},
                {"progress": 40, "message": "Fetching reference image...", "delay": 1.0},
                {"progress": 60, "message": "Aligning images...", "delay": 1.5},
                {"progress": 80, "message": "Analyzing visual features...", "delay": 1.2},
                {"progress": 100, "message": "Generating report...", "delay": 1.0}
            ]
            
            for step in steps:
                with st.spinner(step["message"]):
                    status_container.info(step["message"])
                    time.sleep(step["delay"])
                    progress.progress(step["progress"])
            
            st.success("✅ Inspection complete. Chat enabled.")
            status_container.empty()
            time.sleep(0.5)
            st.rerun()
    
    if st.session_state.app_state["selected_pair"]:
        data = st.session_state.app_state["selected_pair"]
        st.markdown('<h2 class="subheader">📊 Inspection Results</h2>', unsafe_allow_html=True)
        
        user_img, ref_img, aligned_img = data["user_img"], data["reference_img"], data["aligned_img"]
        
        if st.session_state.app_state["comparison_mode"] == "side_by_side":
            col1, col2, col3 = st.columns(3)
            with col1:
                st.image(user_img, caption="Your Package", use_column_width=True)
                st.markdown("<div style='text-align: center;'><small>Your uploaded image</small></div>", unsafe_allow_html=True)
            with col2:
                st.image(ref_img, caption="Reference Package", use_column_width=True)
                st.markdown("<div style='text-align: center;'><small>Authentic reference image</small></div>", unsafe_allow_html=True)
            with col3:
                st.image(aligned_img, caption="Analysis Alignment", use_column_width=True)
                st.markdown("<div style='text-align: center;'><small>Computer vision alignment</small></div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='image-comparison-container'>", unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["Your vs Reference", "Analysis Alignment"])
            with tab1:
                st.image(user_img, caption="Drag slider to compare", use_column_width=True)
                st.image(ref_img, caption="Reference Image (Authentic)", use_column_width=True)
                st.caption("Use your cursor to compare the images")
            with tab2:
                st.image(aligned_img, caption="Analysis Alignment", use_column_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Layout for Analysis, Confidence, and Chat
        col_left, col_right = st.columns([2, 1])
        
        # Analysis Findings Block
        with col_left:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 class="subheader">📋 Analysis Findings</h3>', unsafe_allow_html=True)
            if len(data["llm_analysis"]) > 3:
                with st.expander("View All Analysis Points", expanded=True):
                    for line in data["llm_analysis"]:
                        st.markdown(f"- {line}")
            else:
                for line in data["llm_analysis"]:
                    st.markdown(f"- {line}")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Confidence Overview Block
        with col_right:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.markdown('<h3 class="subheader">🌸 Confidence Overview</h3>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background-color: #343a40; color: #fff; padding: 20px; border-radius: 12px; text-align:center;'>
                <div style='font-size: 28px;'>Confidence Level: <span style='color: gold;'>{data['score']}%</span></div>
                <div style='font-size: 18px; margin-top:10px;'>System confidence based on visual inspection indicators.</div>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns(5)
            for i, (k, v) in enumerate(data["confidence_profile"].items()):
                status_label = "危険" if v >= 80 else ("確認" if 30 < v < 80 else "安全")
                stroke_color = "#dc3545" if status_label == "危険" else ("#007bff" if status_label == "確認" else "#28a745")
                cols[i].markdown(f"""
                <div style='text-align: center;'>
                    <svg width="80" height="80">
                        <circle cx="40" cy="40" r="30" stroke="#ccc" stroke-width="8" fill="none" />
                        <circle cx="40" cy="40" r="30" stroke="{stroke_color}" stroke-width="8" fill="none" stroke-dasharray="{v * 1.88},188" transform="rotate(-90 40 40)"/>
                    </svg>
                    <div style='font-size: 20px; font-weight: bold; margin-top: 5px;'>{v}%</div>
                    <div style='font-size: 16px;'>{k}</div>
                    <div style='font-size: 14px; color: {stroke_color}; font-weight: bold;'>{status_label}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat Block
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<h3 class="subheader">💬 Chat with Inspector AI</h3>', unsafe_allow_html=True)
        st.markdown("""
            Ask questions about the inspection results or request more information about specific features.
            The AI will analyze the visual differences and provide detailed explanations.
        """)
        
        # Initialize chat if empty
        if not st.session_state.app_state["chat_history"]:
            intro = data["chat_intro"]
            st.session_state.app_state["chat_history"].append(("assistant", intro))
        
        # Display chat messages with custom chat bubbles
        for sender, message in st.session_state.app_state["chat_history"]:
            st.markdown(f'<div class="chat-bubble {sender}"><strong>{"You" if sender=="user" else "AI"}:</strong> {message}</div>', unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input("Your question:", key="chat_input", placeholder="Ask about specific features, authenticity concerns, or packaging details...")
        if user_input:
            st.session_state.app_state["chat_history"].append(("user", user_input))
            system_prompt = f"""
            You are an AI assistant specialized in analyzing pharmaceutical packaging authenticity.
            Detailed inspection result:
            - Discrepancies: {', '.join(data['llm_analysis'])}
            - Confidence scores: {json.dumps(data['confidence_profile'])}
            - Overall confidence: {data['score']}%

            Answer queries clearly and concisely using bullet points when listing features. If confidence is low (<70%), emphasize caution.
            """
            chat_history_formatted = [
                {"role": "system", "content": system_prompt},
                *[
                    {"role": "user" if sender == "user" else "assistant", "content": msg}
                    for sender, msg in st.session_state.app_state["chat_history"]
                ]
            ]
            with st.spinner("Processing your question..."):
                time.sleep(0.5)
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=chat_history_formatted,
                        temperature=0.2,
                        max_tokens=250
                    )
                    reply = response.choices[0].message.content.strip()
                except Exception as e:
                    reply = "I apologize, but I encountered an error while generating a response. Please try again."
            st.session_state.app_state["chat_history"].append(("assistant", reply))
            st.experimental_rerun()
        st.markdown('</div>', unsafe_allow_html=True)
else:
    st.markdown("""
        ## 🔍 Welcome to Medicine Package Inspector
        
        This tool helps you verify the authenticity of medicine packaging by comparing your images with reference samples.
        
        ### How it works:
        1. Upload an image of your medicine package
        2. The system compares it with authentic reference images
        3. AI analyzes visual differences and generates an authenticity report
        4. Chat with the AI to get detailed explanations about specific features
        
        ### Get started:
        - Upload your medicine package image using the sidebar
        - Click "Run Inspection" to begin the analysis
    """)
    
    st.markdown("### Example Images")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("Upload clear, well-lit images for best results")
    with col2:
        st.warning("Ensure the package is completely visible in the frame")
    with col3:
        st.success("Multiple angles may improve analysis accuracy")
    
    st.info("⬅️ Upload an image from the sidebar to begin.")
