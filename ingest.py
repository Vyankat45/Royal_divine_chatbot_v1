from app.loader import load_documents
from app.splitter import split_documents
from app.vector_store import save_documents

urls = [

    # ─── CORE / COMPANY ───────────────────────────────────────────────
    "https://www.royaldivineproducts.com/index.php",
    "https://www.royaldivineproducts.com/about.php",
    "https://www.royaldivineproducts.com/quality.php",
    "https://www.royaldivineproducts.com/certificates.php",
    "https://www.royaldivineproducts.com/contact.php",

    # ─── DRY FRUITS ───────────────────────────────────────────────────
    # Category landing (supplier + exporter pages)
    "https://www.royaldivineproducts.com/almond-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/almond-nuts-dryfruits-manufacturer-exporter.php",

    # Individual dry fruit products
    "https://www.royaldivineproducts.com/cashew-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/dates-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/pistachio-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/walnuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/peanuts-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/pine-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/pecans-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/black-dried-raisins-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/pumpkin-seeds-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/sunflower-seeds-nuts-dryfruits-supplier.php",
    "https://www.royaldivineproducts.com/watermelon-seeds-dryfruits-supplier.php",

    # ─── SPICES ───────────────────────────────────────────────────────
    # Category landing
    "https://www.royaldivineproducts.com/cumin-seeds-spices-supplier.php",
    # "https://www.royaldivineproducts.com/cumin-seeds-spices-manufacturer-exporter.php",

    # Individual spice products
    "https://www.royaldivineproducts.com/coriander-seeds-spices-supplier.php",
    "https://www.royaldivineproducts.com/black-seeds-spices-supplier.php",
    "https://www.royaldivineproducts.com/anise-seeds-spices-supplier.php",
    "https://www.royaldivineproducts.com/black-pepper-spices-supplier.php",
    "https://www.royaldivineproducts.com/white-pepper-spices-supplier.php",
    "https://www.royaldivineproducts.com/cloves-spices-supplier.php",
    "https://www.royaldivineproducts.com/dried-ginger-spices-supplier.php",
    "https://www.royaldivineproducts.com/turmeric-spices-supplier.php",
    "https://www.royaldivineproducts.com/cinnamon-spices-supplier.php",
    "https://www.royaldivineproducts.com/bay-leaf-spices-supplier.php",
    "https://www.royaldivineproducts.com/fenugreek-spices-supplier.php",
    "https://www.royaldivineproducts.com/fennel-seeds-spices-supplier.php",
    "https://www.royaldivineproducts.com/ajwain-seeds-spices-supplier.php",
    "https://www.royaldivineproducts.com/sesame-seeds-spices-supplier.php",
    "https://www.royaldivineproducts.com/dried-red-chili-spices-supplier.php",
    "https://www.royaldivineproducts.com/red-chili-powder-spices-supplier.php",

    # ─── FRUITS ───────────────────────────────────────────────────────
    # Category landing
    "https://www.royaldivineproducts.com/apples-fruits-supplier.php",
    # "https://www.royaldivineproducts.com/apples-fruits-manufacturer-exporter.php",
    "https://www.royaldivineproducts.com/coconuts-fruits-supplier.php",  # found in sidebar nav

    # ─── VEGETABLES ───────────────────────────────────────────────────
    # Category landing
    "https://www.royaldivineproducts.com/corn-vegetables-supplier.php",
    # "https://www.royaldivineproducts.com/corn-vegetables-manufacturer-exporter.php",

    # ─── GRAINS ───────────────────────────────────────────────────────
    # Category landing
    "https://www.royaldivineproducts.com/barley-grains-supplier.php",
    # "https://www.royaldivineproducts.com/barley-grains-manufacturer-exporter.php",

]

print("Loading documents...")
documents = load_documents(urls)

print(f"Loaded {len(documents)} documents")

print("Splitting documents...")
chunks = split_documents(documents)

print(f"Created {len(chunks)} chunks")

print("Saving to ChromaDB...")
save_documents(chunks)

print("Ingestion Complete")