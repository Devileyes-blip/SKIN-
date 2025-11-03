# import os
# import requests
# from openai import OpenAI
# from dotenv import load_dotenv
# import base64
# import json

# load_dotenv()

# class SkinAnalyzer:
#     def __init__(self):
#         api_key = os.getenv('OPENAI_API_KEY')
#         if not api_key:
#             raise RuntimeError('OPENAI_API_KEY not found in environment')
#         self.client = OpenAI(api_key=api_key)
#         self.products_db = self.load_products()

#     def load_products(self):
#         products_file = 'data/products.json'
#         if os.path.exists(products_file):
#             with open(products_file, 'r', encoding='utf-8') as f:
#                 return json.load(f)
#         return self.get_default_products()

#     def get_default_products(self):
#         return {
#             "acne": [
#                 {"name": "Fix Derma Shadow SPF 30+ Gel", "type": "Sunscreen",
#                  "key_highlights": ["Non-comedogenic formula", "Oil-free and lightweight", "Broad spectrum protection", "Suitable for acne-prone skin"],
#                  "price": "₹649", "size": "75g"},
#                 {"name": "Fix Derma FCL Acne Cleansing Gel", "type": "Cleanser",
#                  "key_highlights": ["Deep cleanses pores", "Controls excess oil", "Contains salicylic acid", "Reduces acne breakouts"],
#                  "price": "₹375", "size": "100ml"}
#             ],
#             "pigmentation": [
#                 {"name": "Fix Derma Nigrifix Cream", "type": "Brightening Cream",
#                  "key_highlights": ["Reduces dark spots", "Even skin tone", "Contains kojic acid", "Lightens hyperpigmentation"],
#                  "price": "₹525", "size": "30g"},
#                 {"name": "Fix Derma Melanorm Serum", "type": "Serum",
#                  "key_highlights": ["Powerful brightening formula", "Reduces melasma", "Contains tranexamic acid", "Fast-acting results"],
#                  "price": "₹825", "size": "30ml"}
#             ],
#             "aging": [
#                 {"name": "Fix Derma Strallium Stretch Marks Cream", "type": "Anti-aging & Repair",
#                  "key_highlights": ["Reduces fine lines", "Improves skin elasticity", "Hydrates deeply", "Repairs damaged skin"],
#                  "price": "₹749", "size": "75g"},
#                 {"name": "Fix Derma Retino 360 Cream", "type": "Retinol Cream",
#                  "key_highlights": ["Contains retinol", "Anti-aging formula", "Smooths wrinkles", "Improves texture"],
#                  "price": "₹895", "size": "30g"}
#             ],
#             "dryness": [
#                 {"name": "Fix Derma Foamie Face Wash", "type": "Gentle Cleanser",
#                  "key_highlights": ["Hydrating formula", "Gentle on dry skin", "pH balanced", "No harsh chemicals"],
#                  "price": "₹399", "size": "100ml"},
#                 {"name": "Fix Derma Emolene Cream", "type": "Moisturizer",
#                  "key_highlights": ["Deep hydration", "Repairs skin barrier", "Long-lasting moisture", "Non-greasy formula"],
#                  "price": "₹575", "size": "100g"}
#             ],
#             "sensitivity": [
#                 {"name": "Fix Derma Strallium Cream", "type": "Soothing Cream",
#                  "key_highlights": ["Calms irritated skin", "Hypoallergenic", "Fragrance-free", "Strengthens skin barrier"],
#                  "price": "₹749", "size": "75g"}
#             ]
#         }

#     def encode_image(self, image_path):
#         if not os.path.exists(image_path):
#             raise FileNotFoundError(f'Image path not found: {image_path}')
#         with open(image_path, "rb") as image_file:
#             return base64.b64encode(image_file.read()).decode('utf-8')

#     def _strip_markdown_json(self, text: str) -> str:
#         if not isinstance(text, str):
#             raise ValueError('Expected text to be a string')
#         text = text.strip()
#         if '```json' in text:
#             parts = text.split('```json', 1)[1]
#             if '```' in parts:
#                 parts = parts.split('```', 1)[0]
#             return parts.strip()
#         if text.startswith('```') and text.endswith('```'):
#             return text[3:-3].strip()
#         return text

#     def analyze_skin(self, image_path):
#         try:
#             base64_image = self.encode_image(image_path)
#             prompt = (
#                 "You are an expert dermatologist and skincare specialist. Analyze this skin image and provide:\n"
#                 "1. Skin Concerns Detected (identify up to 3 main concerns from: acne, pigmentation, aging, dryness, sensitivity, oiliness, dullness)\n"
#                 "2. Severity Level (Mild, Moderate, Severe)\n"
#                 "3. Detailed Analysis (2-3 sentences describing what you observe)\n"
#                 "4. Skin Type (Oily, Dry, Combination, Sensitive, Normal)\n"
#                 "5. Primary Concern (the main issue to address first)\n\n"
#                 "Return your response in JSON format with keys: concerns, severity, analysis, skin_type, primary_concern."
#             )

#             response = self.client.chat.completions.create(
#                 model="gpt-4o",
#                 messages=[
#                     {
#                         "role": "user",
#                         "content": [
#                             {"type": "text", "text": prompt},
#                             {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
#                         ]
#                     }
#                 ],
#                 max_tokens=1000
#             )

#             choice = response.choices[0]
#             raw_text = ''
#             if hasattr(choice, 'message') and isinstance(choice.message, dict):
#                 content = choice.message.get('content')
#                 if isinstance(content, list):
#                     texts = [item.get('text') for item in content if isinstance(item, dict) and item.get('type') == 'text']
#                     raw_text = texts[0] if texts else ''
#                 elif isinstance(content, str):
#                     raw_text = content
#             elif hasattr(choice, 'text'):
#                 raw_text = getattr(choice, 'text', '')

#             analysis_text = self._strip_markdown_json(raw_text or '')
#             analysis = json.loads(analysis_text)

#             if not isinstance(analysis, dict):
#                 raise ValueError('Invalid analysis format')

#             recommendations = self.recommend_products(analysis)
#             return {"success": True, "skin_analysis": analysis, "recommendations": recommendations}

#         except Exception as e:
#             return {"success": False, "error": str(e), "message": "Failed to analyze image. Please try again."}

#     def recommend_products(self, analysis):
#         primary_concern = (analysis.get('primary_concern') or '').lower()
#         all_concerns = [c.lower() for c in analysis.get('concerns', []) if isinstance(c, str)]
#         recommendations = []
#         if primary_concern in self.products_db:
#             recommendations.extend(self.products_db[primary_concern][:2])
#         for concern in all_concerns:
#             if concern != primary_concern and concern in self.products_db:
#                 recommendations.extend(self.products_db[concern][:1])
#         return recommendations[:3]


# 

from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import json
import os

# --- put near the top of the file ---
import re

CONCERN_SYNONYMS = {
    "acne": [
        "acne", "pimple", "pimples", "zit", "blemish", "breakout", "comedone",
        "blackhead", "blackheads", "whitehead", "whiteheads", "clogged pore", "clogged pores"
    ],
    "dryness": [
        "dry", "dryness", "flaky", "flake", "flaking", "peeling", "peel", "tight", "dehydrated", "rough", "ashy", "scaly"
    ],
    "oiliness": [
        "oily", "oiliness", "greasy", "shine", "shiny", "sebum", "slick"
    ],
    "pigmentation": [
        "dark spot", "dark spots", "spot", "spots", "hyperpigmentation", "melasma",
        "uneven tone", "uneven skin tone", "age spot", "sun spot", "freckle", "freckles"
    ],
    "aging": [
        "wrinkle", "wrinkles", "fine line", "fine lines", "crow's feet", "sagging", "loss of firmness", "creasing"
    ],
    "sensitivity": [
        "sensitive", "sensitivity", "red", "redness", "irritation", "irritated", "inflamed", "inflamation", "stinging"
    ]
}

SEVERITY_KEYWORDS = {
    "severe": ["severe", "significant", "marked", "pronounced", "many", "a lot of"],
    "moderate": ["moderate", "some", "several", "noticeable"],
    "mild": ["mild", "slight", "few", "subtle"]
}

# Priority when choosing primary concern
CONCERN_PRIORITY = ["acne", "pigmentation", "oiliness", "dryness", "sensitivity", "aging", "normal"]

def extract_tags_from_caption(caption: str):
    text = caption.lower()

    # collect concerns matched by synonyms
    found = set()
    for concern, words in CONCERN_SYNONYMS.items():
        for w in words:
            if w in text:
                found.add(concern)
                break

    # infer skin type heuristics
    skin_type = "Normal"
    if any(k in text for k in ["oily","greasy","shine","shiny","sebum"]) or "oiliness" in found:
        skin_type = "Oily"
    if any(k in text for k in ["dry","flaky","peeling","tight","dehydrated","rough"]) or "dryness" in found:
        skin_type = "Dry"
    if any(k in text for k in ["sensitive","red","redness","irritat","inflam"]) or "sensitivity" in found:
        skin_type = "Sensitive"

    # choose severity by keyword precedence severe > moderate > mild
    severity = "Mild"
    for level in ["severe", "moderate", "mild"]:
        if any(k in text for k in SEVERITY_KEYWORDS[level]):
            severity = level.capitalize()
            break

    # default to normal when no concern keywords surfaced
    if not found:
        found.add("normal")

    # primary concern by priority
    primary = sorted(list(found), key=lambda c: CONCERN_PRIORITY.index(c) if c in CONCERN_PRIORITY else 999)[0]

    return {"concerns": sorted(list(found)), "skin_type": skin_type, "severity": severity, "primary_concern": primary}



from transformers import InstructBlipProcessor, InstructBlipForConditionalGeneration
from PIL import Image
import json, torch

class SkinAnalyzer:
    def __init__(self):
        model_id = "Salesforce/instructblip-flan-t5-xl"   # use "-large" if VRAM is limited
        self.processor = InstructBlipProcessor.from_pretrained(model_id)
        self.model = InstructBlipForConditionalGeneration.from_pretrained(
            model_id, torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32, device_map="auto" if torch.cuda.is_available() else None
        )
        with open('data/products.json', 'r', encoding='utf-8') as f:
            self.products_db = json.load(f)


    # def analyze_skin(self, image_path):
    #     try:
    #         image = Image.open(image_path).convert("RGB")
    #         # BLIP is an image captioning model, so prompt = None
    #         inputs = self.processor(image, return_tensors="pt")
    #         out = self.model.generate(**inputs)
    #         description = self.processor.decode(out[0], skip_special_tokens=True)

    #         # For demo: treat raw description as 'analysis', and return dummy structure
    #         analysis = {
    #             "concerns": ["acne"],  # You can parse keywords from description for real pipelines
    #             "severity": "Moderate",
    #             "analysis": description,
    #             "skin_type": "Normal",  # BLIP can't really classify, add classifier if required
    #             "primary_concern": "acne"
    #         }
    #         recommendations = self.recommend_products(analysis)
    #         return {"success": True, "skin_analysis": analysis, "recommendations": recommendations}
    #     except Exception as e:
    #         import traceback
    #         traceback.print_exc()
    #         return {"success": False, "error": str(e), "message": "Failed to analyze image. Please try again."}

    # def analyze_skin(self, image_path):
    #     try:
    #         image = Image.open(image_path).convert("RGB")
    #         inputs = self.processor(image, return_tensors="pt")
    #         out = self.model.generate(**inputs)
    #         description = self.processor.decode(out[0], skip_special_tokens=True)

    #         desc = description.lower()
    #         concerns = []
    #         skin_type = "Normal"
    #         severity = "Mild"

    #         # Concerns and logic
    #         if "dry" in desc or "flaky" in desc:
    #             concerns.append("dryness")
    #             skin_type = "Dry"
    #             severity = "Mild"
    #         if "acne" in desc or "pimple" in desc or "blemish" in desc:
    #             concerns.append("acne")
    #             skin_type = "Oily"
    #             severity = "Moderate"
    #         if "wrinkle" in desc or "aging" in desc or "fine line" in desc:
    #             concerns.append("aging")
    #             severity = "Mild"
    #         if "pigment" in desc or "dark spot" in desc or "spot" in desc:
    #             concerns.append("pigmentation")
    #             severity = "Mild"
    #         if "red" in desc or "irritat" in desc or "sensitive" in desc:
    #             concerns.append("sensitivity")
    #             skin_type = "Sensitive"
    #             severity = "Mild"
    #         if not concerns:
    #             concerns.append("normal")
    #             skin_type = "Normal"

    #         primary_concern = concerns[0]

    #         # Update analysis dict
    #         analysis = {
    #             "concerns": concerns,
    #             "severity": severity,
    #             "analysis": description,
    #             "skin_type": skin_type,
    #             "primary_concern": primary_concern
    #         }
    #         recommendations = self.recommend_products(analysis)
    #         return {"success": True, "skin_analysis": analysis, "recommendations": recommendations}
    #     except Exception as e:
    #         import traceback
    #         traceback.print_exc()
    #         return {"success": False, "error": str(e), "message": "Failed to analyze image. Please try again."}

    # --- replace your analyze_skin method with this ---
    
    def _generate_caption_safe(self, image):
        # concise neutral prompt to avoid leaking domain words into caption
        prompt = "Describe the visible facial skin briefly."
        # conditional captioning (BLIP supports text + image)
        inputs = self.processor(images=image, text=prompt, return_tensors="pt")
        out = self.model.generate(**inputs, max_new_tokens=64)
        cap = self.processor.decode(out[0], skip_special_tokens=True).strip()

        # if the model echoed the prompt, retry without prompt
        pw = set(prompt.lower().split())
        cw = set(cap.lower().split())
        overlap = len(pw & cw) / max(1, len(pw))
        if overlap > 0.5 or cap.lower().startswith(prompt[:20].lower()):
            inputs = self.processor(images=image, return_tensors="pt")
            out = self.model.generate(**inputs, max_new_tokens=64)
            cap = self.processor.decode(out[0], skip_special_tokens=True).strip()
        return cap

    
    def analyze_skin(self, image_path):
        try:
            image = Image.open(image_path).convert("RGB")

            instruction = (
                "Analyze this facial skin image and respond in one short sentence mentioning: "
                "visible concerns among {acne, oiliness, dryness, sensitivity, dark spots, wrinkles} "
                "and a severity word {mild, moderate, severe}."
            )

            inputs = self.processor(images=image, text=instruction, return_tensors="pt").to(self.model.device)
            with torch.no_grad():
                out = self.model.generate(**inputs, max_new_tokens=96)
            description = self.processor.batch_decode(out, skip_special_tokens=True)[0].strip()

            parsed = extract_tags_from_caption(description)

            analysis = {
                "concerns": parsed["concerns"],
                "severity": parsed["severity"],
                "analysis": description,
                "skin_type": parsed["skin_type"],
                "primary_concern": parsed["primary_concern"]
            }
            recs = self.recommend_products(analysis)
            return {"success": True, "skin_analysis": analysis, "recommendations": recs}
        except Exception as e:
            import traceback; traceback.print_exc()
            return {"success": False, "error": str(e), "message": "Failed to analyze image, please try again."}

    # def recommend_products(self, analysis):
    #     primary_concern = analysis.get('primary_concern', '').lower()
    #     all_concerns = [c.lower() for c in analysis.get('concerns', [])]

    #     recommendations = []
    #     if primary_concern in self.products_db:
    #         recommendations.extend(self.products_db[primary_concern][:2])
    #     for concern in all_concerns:
    #         if concern != primary_concern and concern in self.products_db:
    #             recommendations.extend(self.products_db[concern][:1])
    #     return recommendations[:3]

    def recommend_products(self, analysis):
        primary_concern = analysis.get('primary_concern', '').lower()
        all_concerns = [c.lower() for c in analysis.get('concerns', [])]

        recommendations = []
        if primary_concern in self.products_db:
            recommendations.extend(self.products_db[primary_concern][:2])   # top 2 for primary concern

        for concern in all_concerns:
            if concern != primary_concern and concern in self.products_db:
                recommendations.extend(self.products_db[concern][:1])       # top 1 for other concerns

        return recommendations[:3]  # show up to 3
