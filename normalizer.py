def normalize_material(material):
    if material is None:
        return None

    material_lower = material.lower().strip()

    material_map = {
        "bans": "bamboo",
        "baans": "bamboo",
        "bamboo": "bamboo",
        "बाँस": "bamboo",
        "बांस": "bamboo"
    }

    return material_map.get(material_lower, material)


def normalize_category(category):
    if category is None:
        return None

    category_lower = category.lower().strip()

    category_map = {
        "tokri": "basket",
        "basket": "basket",
        "टोकरी": "basket"
    }

    return category_map.get(category_lower, category)


def normalize_craft_technique(technique):
    if technique is None:
        return None

    technique_lower = technique.lower().strip()

    if "handmade" in technique_lower:
        return "handmade"

    if "haath se" in technique_lower:
        return "handmade"

    if "हाथ से" in technique_lower:
        return "handmade"

    if "हस्तनिर्मित" in technique_lower:
        return "handmade"

    return technique


def normalize_product(product):
    product["material"] = normalize_material(
        product.get("material")
    )

    product["category"] = normalize_category(
        product.get("category")
    )

    product["craft_technique"] = normalize_craft_technique(
        product.get("craft_technique")
    )

    return product