from app.vector_store import search_documents
from app.llm import generate_answer
from app.query_router import get_search_filter
from app.google_logger import log_conversation
from app.product_detector import detect_product, suggest_products
from app.moq_checker import is_below_moq

from app.lead_detector import (
    is_lead,
    extract_quantity,
    extract_country
)

from app.memory import (
    add_message,
    get_history
)

from app.lead_memory import lead_memory

from app.contact_extractor import (
    extract_email,
    extract_phone,
    extract_name
)

from app.customer_memory import customer_memory

from app.lead_logger import save_lead

from app.prompts import SYSTEM_PROMPT, NEGATIVE_PROMPT
from app.business_context import BUSINESS_CONTEXT

from app.guardrails import is_business_question

import logging
import re

logger = logging.getLogger(__name__)


def return_and_log(session_id, question, response):
    log_conversation(
        session_id=session_id,
        question=question,
        answer=response
    )
    return response


def ask_question(question, session_id):
    try:
        return _ask_question(question, session_id)
    except Exception as e:
        logger.exception("Unhandled error for session %s: %s", session_id, e)
        response = (
            "I apologise, but I encountered a technical issue.\n\n"
            "Please contact our sales team at sales@royaldivineproducts.com or call +91-8451878725."
        )
        return response


def _ask_question(question, session_id):
    history = get_history(session_id)

    customer = customer_memory.get(session_id)
    already_registered = False
    if customer:
        already_registered = customer.get("lead_submitted", False)

    pending_lead = lead_memory.get(session_id)

    # ==========================================
    # Pending Lead Flow - collect missing info
    # ==========================================
    if pending_lead:
        # If the question has quantity/country/contact info, process in lead flow
        has_lead_info = bool(extract_quantity(question)) or bool(extract_country(question)) or bool(extract_email(question)) or bool(extract_phone(question))
        if is_business_question(question) and not has_lead_info:
            return _answer_business_question(question, session_id, history)

        cancel_pattern = re.compile(
            r'\b(?:no\b(?!\w)|cancel|stop|nevermind|never mind|forget it|leave it)\b',
            re.IGNORECASE
        )
        if cancel_pattern.search(question):
            del lead_memory[session_id]
            response = "No problem. Feel free to ask if you need any information about our products."
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        # Update lead with any newly detected info
        new_product = detect_product(question, history) or pending_lead.get("product")
        new_qty = extract_quantity(question) or pending_lead.get("quantity")
        new_country = extract_country(question) or pending_lead.get("country")

        lead_memory[session_id]["product"] = new_product
        lead_memory[session_id]["quantity"] = new_qty
        lead_memory[session_id]["country"] = new_country

        pl = lead_memory[session_id]

        # Check if we still need product, quantity, or country
        if not pl["product"]:
            suggestions = suggest_products(question)
            extras = ""
            if suggestions:
                extras = "\n\nDid you mean: " + ", ".join(suggestions) + "?"
            response = (
                "Thank you for your interest. Which product are you looking to inquire about?\n"
                "Please specify the product name (e.g., almonds, cashews, dates, spices, etc.)." + extras
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        if not pl["quantity"]:
            response = (
                f"What quantity of {pl['product'].title()} are you looking for?\n"
                "Please specify the amount (e.g., 50 kg, 1 ton, 500 g)."
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        if not pl["country"]:
            response = (
                f"Which country will the {pl['product'].title()} be shipped to?"
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        # All order info collected — check MOQ before asking for contact
        if is_below_moq(pl["quantity"], pl["country"]):
            response = (
                "Thank you for your interest.\n\n"
                "Please note our minimum order quantities:\n\n"
                "• India: 1 Ton (1000 KG) minimum order\n"
                "• Export: 5 Tons (5000 KG) minimum order\n\n"
                "The quantity you mentioned is below our minimum. "
                "Please specify a higher quantity (e.g., 1 ton or more)."
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        # All order info collected — now ask for contact details
        email = extract_email(question) or pl.get("email", "")
        phone = extract_phone(question) or pl.get("phone", "")

        if email and phone:
            name = extract_name(question) or pl.get("name", email.split("@")[0].title())
            lead_memory[session_id]["email"] = email
            lead_memory[session_id]["phone"] = phone
            lead_memory[session_id]["name"] = name

            save_lead(
                session_id=session_id,
                name=name, email=email, phone=phone,
                product=pl["product"], quantity=pl["quantity"],
                country=pl["country"], question=pl["question"]
            )
            customer_memory[session_id] = {
                "lead_submitted": True, "name": name, "email": email, "phone": phone
            }
            del lead_memory[session_id]

            response = (
                "Thank you!\n\n"
                "Your inquiry has been submitted successfully.\n\n"
                "Order Summary:\n"
                f"• Product: {pl['product'].title()}\n"
                f"• Quantity: {pl['quantity']}\n"
                f"• Country: {pl['country']}\n\n"
                "Our sales team will contact you shortly at the provided details."
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        # Accumulate any contact info provided so far
        if email:
            lead_memory[session_id]["email"] = email
        if phone:
            lead_memory[session_id]["phone"] = phone

        # Need contact info
        response = (
            "Please provide your contact details so we can follow up:\n"
            "• Full Name\n"
            "• Email Address\n"
            "• Phone Number"
        )
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", response)
        return return_and_log(session_id, question, response)

    # ==========================================
    # Existing Customer Lead Flow
    # ==========================================
    if is_lead(question) and already_registered:
        product = detect_product(question, history)
        quantity = extract_quantity(question)

        # Country may not be extracted yet in this branch
        moq_country = extract_country(question) or "export"
        if is_below_moq(question, moq_country):
            response = (
                "Thank you for your interest.\n\n"
                "Please note our minimum order quantities:\n\n"
                "• India: 1 Ton (1000 KG) minimum order\n"
                "• Export: 5 Tons (5000 KG) minimum order\n\n"
                "Unfortunately, we cannot process orders below the MOQ."
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        if not product:
            response = (
                "I couldn't identify the product in your inquiry.\n\n"
                "Please specify the product name and we will connect you with our sales team."
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        response = (
            f"Thank you {customer['name']}.\n\n"
            f"Your inquiry for {product.title()} has been noted.\n\n"
            "We already have your contact information on file.\n\n"
            "Our sales team will contact you shortly regarding your inquiry."
        )
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", response)
        return return_and_log(session_id, question, response)

    # ==========================================
    # New Lead Flow
    # ==========================================
    if is_lead(question) and not already_registered:
        # If the question is asking for info (not clear purchase intent), answer it
        has_quantity = bool(extract_quantity(question))
        has_purchase_words = any(w in question.lower() for w in ["buy", "purchase", "order", "import"])
        if is_business_question(question) and not has_quantity and not has_purchase_words:
            return _answer_business_question(question, session_id, history)

        product = detect_product(question, history)
        quantity = extract_quantity(question)
        country = extract_country(question)

        if not product:
            suggestions = suggest_products(question)
            if suggestions:
                suggestion_text = "\n".join([f"• {s}" for s in suggestions])
                response = (
                    f"I couldn't find that product in our knowledge base.\n\n"
                    f"Did you mean one of these?\n{suggestion_text}\n\n"
                    "Please contact our sales team at sales@royaldivineproducts.com "
                    "or call +91-8451878725 for more information."
                )
            else:
                response = (
                    "I couldn't find that product in our knowledge base.\n\n"
                    "Please contact our sales team at sales@royaldivineproducts.com "
                    "or call +91-8451878725."
                )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        # Store whatever we have and ask for missing info one at a time
        lead_memory[session_id] = {
            "product": product,
            "quantity": quantity,
            "country": country,
            "question": question,
            "name": ""
        }

        # Ask for missing info step by step
        if not quantity:
            response = (
                f"Thank you for your interest in {product.title()}.\n\n"
                f"What quantity of {product.title()} are you looking for?\n"
                "Please specify the amount (e.g., 50 kg, 1 ton, 500 g)."
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        if not country:
            response = (
                f"Thank you for your interest in {product.title()}.\n\n"
                f"Which country will the {product.title()} be shipped to?"
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        # Both quantity and country present — now check MOQ
        if is_below_moq(quantity, country):
            del lead_memory[session_id]
            response = (
                "Thank you for your interest.\n\n"
                "Please note our minimum order quantities:\n\n"
                "• India: 1 Ton (1000 KG) minimum order\n"
                "• Export: 5 Tons (5000 KG) minimum order\n\n"
                "Unfortunately, we cannot process orders below the MOQ."
            )
            add_message(session_id, "user", question)
            add_message(session_id, "assistant", response)
            return return_and_log(session_id, question, response)

        # Product + quantity + country all present — ask for contact
        response = (
            f"Thank you for your interest in {product.title()}.\n\n"
            "Order Summary:\n"
            f"• Product: {product.title()}\n"
            f"• Quantity: {quantity}\n"
            f"• Country: {country}\n\n"
            "Please provide your contact details so we can follow up:\n"
            "• Full Name\n"
            "• Email Address\n"
            "• Phone Number"
        )
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", response)
        return return_and_log(session_id, question, response)

    # ==========================================
    # Normal RAG Flow
    # ==========================================
    return _answer_business_question(question, session_id, history)


def _answer_business_question(question, session_id, history):
    search_filter = get_search_filter(question)

    search_query = question
    if len(question.split()) <= 5:
        last_user_message = ""
        for msg in reversed(history):
            if msg["role"] == "user":
                last_user_message = msg["content"]
                break
        if last_user_message:
            search_query = last_user_message + " " + question

    results = search_documents(query=search_query, k=5, filter=search_filter)

    history_text = "\n".join(
        [f"{msg['role']}: {msg['content']}" for msg in history[-10:]]
    )

    pending_lead = lead_memory.get(session_id)
    lead_context = ""
    if pending_lead:
        lead_context = (
            "NOTE: The customer has a pending lead inquiry.\n"
            f"They inquired about: {pending_lead['product']}\n"
            f"Quantity: {pending_lead['quantity']}\n"
            f"Country: {pending_lead['country']}\n"
            "Respond to their current question naturally. "
            "At the end, gently remind them to complete the contact form if appropriate."
        )

    if len(results) == 0:
        # No vector results — answer from business context alone
        final_context = f"""
{SYSTEM_PROMPT}

{NEGATIVE_PROMPT}

BUSINESS CONTEXT:
{BUSINESS_CONTEXT}

CHAT HISTORY:
{history_text}

{lead_context}
"""
        answer = generate_answer(context=final_context, question=question)
        answer += (
            "\n\n"
            "📧 Email: sales@royaldivineproducts.com\n"
            "📞 Phone: +91-8451878725\n"
            "📍 3rd Floor, Kothari House, 269, Raja Ram Mohan Roy Road, Girgaon, Mumbai-400004"
        )
        add_message(session_id, "user", question)
        add_message(session_id, "assistant", answer)
        return return_and_log(session_id, question, answer)

    context = "\n\n".join([doc.page_content for doc in results])

    final_context = f"""
{SYSTEM_PROMPT}

{NEGATIVE_PROMPT}

BUSINESS CONTEXT:
{BUSINESS_CONTEXT}

CHAT HISTORY:
{history_text}

{lead_context}

RETRIEVED CONTEXT:
{context}
"""

    answer = generate_answer(context=final_context, question=question)

    answer += (
        "\n\n"
        "📧 Email: sales@royaldivineproducts.com\n"
        "📞 Phone: +91-8451878725\n"
        "📍 3rd Floor, Kothari House, 269, Raja Ram Mohan Roy Road, Girgaon, Mumbai-400004"
    )

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer)

    log_conversation(
        session_id=session_id,
        question=question,
        answer=answer
    )

    return answer
