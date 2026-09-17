from openai import OpenAI
import json
from normalizer import normalize_product

client = OpenAI()

text = input("Enter product description: ")

response = client.responses.create(
    model="gpt-5.6-luna",

    input=[
        {
            "role": "system",
            "content": """
You are an AI Product Information Extraction system for artisan products.

Your job is to extract ONLY information that the artisan explicitly provides.

IMPORTANT RULES:
1. Do NOT guess or infer information.
2. If information is not explicitly mentioned, return null.
3. Do not assume material type from the product image or product name.
4. Understand Hindi, Hinglish, and English.
5. Convert the extracted information into the required JSON structure.
6. Keep the meaning of the artisan's words.
7. If a dimension is given but its specific direction (length/width/height) is not clear,
   do not assign it to a specific dimension.
"""
        },
        {
            "role": "user",
            "content": text
        }
    ],

    text={
        "format": {
            "type": "json_schema",
            "name": "artisan_product",
            "description": "Structured information extracted from an artisan product description.",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": ["string", "null"]
                    },
                    "category": {
                        "type": ["string", "null"]
                    },
                    "material": {
                        "type": ["string", "null"]
                    },
                    "colour": {
                        "type": ["string", "null"]
                    },
                    "dimensions": {
                        "type": "object",
                        "properties": {
                            "length": {
                                "type": ["number", "null"]
                            },
                            "width": {
                                "type": ["number", "null"]
                            },
                            "height": {
                                "type": ["number", "null"]
                            },
                            "unit": {
                                "type": ["string", "null"]
                            }
                        },
                        "required": [
                            "length",
                            "width",
                            "height",
                            "unit"
                        ],
                        "additionalProperties": False
                    },
                    "craft_technique": {
                        "type": ["string", "null"]
                    },
                    "usage": {
                        "type": ["string", "null"]
                    },
                    "care_instructions": {
                        "type": ["string", "null"]
                    },
                    "special_features": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        }
                    },
                    "origin": {
                        "type": ["string", "null"]
                    },
                    "price": {
                        "type": ["number", "null"]
                    }
                },

                "required": [
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
        }
    }
)

data = json.loads(response.output_text)
data = normalize_product(data)

print("\nStructured Product JSON:")
print(json.dumps(data, indent=2, ensure_ascii=False))

required_fields = [
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
]

missing_fields = []

for field in required_fields:
    value = data.get(field)

    if value is None or value == "" or value == []:
        missing_fields.append(field)

print("\nMissing Information:")

if missing_fields:
    for field in missing_fields:
        print("-", field)
else:
    print("None. All information is available.")

questions = {
    "product_name": "What is the name of this product?",
    "category": "What category does this product belong to?",
    "material": "What material is this product made from?",
    "colour": "What is the colour of this product?",
    "craft_technique": "Which technique was used to make this product?",
    "usage": "What is this product used for?",
    "care_instructions": "How should this product be cleaned or stored?",
    "special_features": "Does this product have any special features?",
    "origin": "Where was this product made?",
    "price": "What is the selling price of this product?"
}

print("\nFollow-up Questions:")

for field in missing_fields:
    print("-", questions[field])