from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import tempfile
import json

app = Flask(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# =========================================================
# PRODUCT JSON SCHEMA
# =========================================================

PRODUCT_SCHEMA = {
    "type": "object",
    "properties": {

        "language": {"type": ["string", "null"]},

        "product_name": {"type": ["string", "null"]},

        "category": {"type": ["string", "null"]},

        "material": {"type": ["string", "null"]},

        "colour": {"type": ["string", "null"]},

        "dimensions": {
            "type": "object",
            "properties": {
                "length": {"type": ["number", "null"]},
                "width": {"type": ["number", "null"]},
                "height": {"type": ["number", "null"]},
                "unit": {"type": ["string", "null"]}
            },
            "required": [
                "length",
                "width",
                "height",
                "unit"
            ],
            "additionalProperties": False
        },

        "craft_technique": {"type": ["string", "null"]},

        "usage": {"type": ["string", "null"]},

        "care_instructions": {"type": ["string", "null"]},

        "special_features": {
            "type": "array",
            "items": {"type": "string"}
        },

        "origin": {"type": ["string", "null"]},

        "price": {"type": ["number", "null"]}
    },

    "required": [
        "language",
        "product_name",
        "category",
        "material",
        "colour",
        "dimensions",
        "craft_technique",
        "usage",
        "care_instructions",
        "special_features",
        "origin",
        "price"
    ],

    "additionalProperties": False
}


# =========================================================
# AI INSTRUCTIONS
# =========================================================

SYSTEM_PROMPT = """
You are an AI Product Intelligence Engine for an artisan marketplace.

The artisan can describe ANY product.

The product is NOT restricted to any predefined category.

The artisan may speak in:
Hindi, English, Hinglish, mixed Hindi-English,
or Indian regional languages.

IMPORTANT RULES:

1. Automatically identify the language.

2. Understand mixed-language speech naturally.

3. Hindi + English words in the same sentence are VALID.

4. Extract ONLY information explicitly stated by the artisan.

5. NEVER guess information.

6. NEVER hallucinate information.

7. NEVER infer material from product name.

8. NEVER infer colour, dimensions, origin, technique,
   usage or features.

9. If information is not explicitly provided, return null.

10. If dimensions are unclear, do not guess length,
    width or height.

11. Extract price only when explicitly stated.

12. Extract special features only when explicitly stated.

13. The product can be ANY artisan-made product.

14. Preserve the meaning of the artisan's words.

15. Return only the requested JSON structure.
"""


# =========================================================
# FOLLOW-UP QUESTIONS
# =========================================================

QUESTIONS = {

    "product_name":
        "What is the name of your product?",

    "category":
        "What type or category of product is this?",

    "material":
        "What material is your product made from?",

    "colour":
        "What is the colour of your product?",

    "dimensions":
        "What are the size or dimensions of your product?",

    "craft_technique":
        "Which technique did you use to make this product?",

    "usage":
        "What is this product used for?",

    "care_instructions":
        "How should this product be cleaned or stored?",

    "special_features":
        "What makes your product special?",

    "origin":
        "Where was this product made?",

    "price":
        "What is your selling price?"
}


# =========================================================
# FIND MISSING INFORMATION
# =========================================================

def find_missing_information(product):

    missing = []

    fields = [
        "product_name",
        "category",
        "material",
        "colour",
        "craft_technique",
        "usage",
        "care_instructions",
        "origin",
        "price"
    ]

    for field in fields:

        value = product.get(field)

        if value is None or value == "":
            missing.append(field)

    dimensions = product.get("dimensions", {})

    if (
        dimensions.get("length") is None
        and dimensions.get("width") is None
        and dimensions.get("height") is None
    ):
        missing.append("dimensions")

    if not product.get("special_features"):
        missing.append("special_features")

    return missing


# =========================================================
# DEMO DATA
# =========================================================

def demo_result():

    return {

        "language": "Hinglish",

        "product_name": "Handmade Artisan Product",

        "category": "Handicraft",

        "material": None,

        "colour": None,

        "dimensions": {
            "length": None,
            "width": None,
            "height": None,
            "unit": None
        },

        "craft_technique": "Handmade",

        "usage": None,

        "care_instructions": None,

        "special_features": [],

        "origin": None,

        "price": None
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# MAIN PROCESS
# =========================================================

@app.route("/process", methods=["POST"])
def process():

    audio_path = None

    try:

        # -------------------------------------------------
        # CHECK AUDIO
        # -------------------------------------------------

        if "audio" not in request.files:

            return jsonify({
                "success": False,
                "error": "No audio was received."
            }), 400


        audio = request.files["audio"]


        if audio.filename == "":

            return jsonify({
                "success": False,
                "error": "Empty audio file."
            }), 400


        # -------------------------------------------------
        # TEMP AUDIO FILE
        # -------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".webm"
        ) as temp:

            audio.save(temp.name)

            audio_path = temp.name


        # -------------------------------------------------
        # SPEECH → TEXT
        # -------------------------------------------------

        with open(audio_path, "rb") as audio_file:

            transcription = client.audio.transcriptions.create(
                model="gpt-4o-transcribe",
                file=audio_file
            )


        transcript = transcription.text.strip()


        if not transcript:

            return jsonify({
                "success": False,
                "error": "No speech could be detected."
            }), 400


        # -------------------------------------------------
        # TEXT → STRUCTURED JSON
        # -------------------------------------------------

        response = client.responses.create(

            model="gpt-5.6-luna",

            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": transcript
                }
            ],

            text={
                "format": {
                    "type": "json_schema",
                    "name": "artisan_product",
                    "description":
                        "Structured artisan product information",
                    "strict": True,
                    "schema": PRODUCT_SCHEMA
                }
            }
        )


        product = json.loads(
            response.output_text
        )


        # -------------------------------------------------
        # MISSING INFORMATION
        # -------------------------------------------------

        missing = find_missing_information(product)


        follow_up_questions = []

        for field in missing:

            if field in QUESTIONS:

                follow_up_questions.append(
                    QUESTIONS[field]
                )


        # -------------------------------------------------
        # REAL AI RESPONSE
        # -------------------------------------------------

        return jsonify({

            "success": True,

            "mode": "live",

            "transcription": transcript,

            "product": product,

            "missing_fields": missing,

            "follow_up_questions":
                follow_up_questions

        })


    except Exception as e:

        # =================================================
        # IMPORTANT:
        # API CREDIT / QUOTA FAILURE
        # =================================================

        error_text = str(e)

        print("\nAPI ERROR:")
        print(error_text)


        # -------------------------------------------------
        # DEMO FALLBACK
        # -------------------------------------------------

        if (
            "insufficient_quota" in error_text.lower()
            or "credit" in error_text.lower()
            or "429" in error_text
        ):

            product = demo_result()

            missing = find_missing_information(product)

            questions = []

            for field in missing:

                if field in QUESTIONS:

                    questions.append(
                        QUESTIONS[field]
                    )


            return jsonify({

                "success": True,

                "mode": "demo",

                "transcription":
                    "Demo voice transcription — API credits are currently unavailable.",

                "product": product,

                "missing_fields": missing,

                "follow_up_questions": questions

            })


        # -------------------------------------------------
        # OTHER ERRORS
        # -------------------------------------------------

        return jsonify({

            "success": False,

            "error":
                "The AI service is temporarily unavailable."

        }), 500


    finally:

        # -------------------------------------------------
        # DELETE TEMP AUDIO
        # -------------------------------------------------

        if (
            audio_path
            and os.path.exists(audio_path)
        ):

            os.remove(audio_path)


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )