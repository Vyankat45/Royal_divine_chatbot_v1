# app/metadata.py

def generate_metadata(url: str):

    metadata = {}

    # Company Pages
    if "about.php" in url:
        metadata["page_type"] = "company"
        metadata["section"] = "about"

    elif "quality.php" in url:
        metadata["page_type"] = "company"
        metadata["section"] = "quality"

    elif "certificates.php" in url:
        metadata["page_type"] = "company"
        metadata["section"] = "certificate"

    elif "contact.php" in url:
        metadata["page_type"] = "company"
        metadata["section"] = "contact"

    elif "index.php" in url:
        metadata["page_type"] = "company"
        metadata["section"] = "home"

    # Product Pages
    else:

        metadata["page_type"] = "product"

        if "dryfruits" in url:
            metadata["category"] = "dryfruits"

        elif "spices" in url:
            metadata["category"] = "spices"

        elif "fruits" in url:
            metadata["category"] = "fruits"

        elif "vegetables" in url:
            metadata["category"] = "vegetables"

        elif "grains" in url:
            metadata["category"] = "grains"

        # supplier / manufacturer-exporter
        if "supplier" in url:
            metadata["business_type"] = "supplier"

        elif "manufacturer-exporter" in url:
            metadata["business_type"] = "manufacturer_exporter"

        # Product Name
        filename = url.split("/")[-1]

        product_name = (
            filename
            .replace("-supplier.php", "")
            .replace("-manufacturer-exporter.php", "")
            .replace("-dryfruits", "")
            .replace("-spices", "")
            .replace("-fruits", "")
            .replace("-vegetables", "")
            .replace("-grains", "")
            .replace("-nuts", "")
        )

        metadata["product_name"] = product_name

    return metadata