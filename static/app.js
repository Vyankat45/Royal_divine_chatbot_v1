/* ══ Royal Divine Chatbot — app.js ════════════════════════════════ */

function getSessionId() {
    let sessionId = localStorage.getItem("chat_session_id");
    if (!sessionId) {
        sessionId = "session_" + Math.random().toString(36).substring(2) + Date.now();
        localStorage.setItem("chat_session_id", sessionId);
    }
    return sessionId;
}

/* ── open / close ─────────────────────────────────────────────── */
function openChat() {
    const widget = document.getElementById("chat-widget");
    const badge  = document.getElementById("fab-badge");
    widget.classList.add("open");
    widget.setAttribute("aria-hidden", "false");
    if (badge) badge.classList.add("hidden");
    scrollBottom();
    document.getElementById("w-input").focus();
}

function closeChat() {
    const widget = document.getElementById("chat-widget");
    widget.classList.remove("open");
    widget.setAttribute("aria-hidden", "true");
}

/* ── quick chip shortcut ──────────────────────────────────────── */
function quickAsk(text) {
    document.getElementById("w-input").value = text;
    sendMessage();
    const chips = document.getElementById("widget-chips");
    if (chips) chips.style.display = "none";
}

/* ── send ─────────────────────────────────────────────────────── */
async function sendMessage() {
    const input   = document.getElementById("w-input");
    const sendBtn = document.getElementById("w-send");
    const typing  = document.getElementById("widget-typing");

    const question = input.value.trim();
    if (!question) return;

    appendUserMsg(question);
    input.value = "";
    sendBtn.disabled = true;
    typing.style.display = "flex";
    scrollBottom();

    try {
        const res  = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({question: question, session_id: getSessionId()})
        });
        const data = await res.json();
        typing.style.display = "none";
        appendBotMsg(data.answer);

        if (
            data.answer.includes("Full Name")
            &&
            data.answer.includes("Email Address")
            &&
            data.answer.includes("Phone Number")
        ) {
            setTimeout(showContactForm, 300);
        }

    } catch {
        typing.style.display = "none";
        appendBotMsg("Sorry, I'm having trouble connecting right now. Please try again.");
    }

    sendBtn.disabled = false;
    input.focus();
}

/* ── append user bubble ───────────────────────────────────────── */
function appendUserMsg(text) {
    const box = document.getElementById("widget-messages");
    const row = document.createElement("div");
    row.className = "wmsg user-wmsg";
    row.innerHTML = `
        <div class="wavatar user-wavatar" aria-hidden="true">You</div>
        <div class="wbubble"><p>${escHtml(text)}</p></div>
    `;
    box.appendChild(row);
    scrollBottom();
}

/* ── append bot bubble with formatted HTML ────────────────────── */
function appendBotMsg(rawText) {
    const box = document.getElementById("widget-messages");
    const row = document.createElement("div");
    row.className = "wmsg bot-wmsg";
    row.innerHTML = `
        <div class="wavatar bot-wavatar" aria-hidden="true">
            <svg width="14" height="14" viewBox="0 0 30 30" fill="none">
                <circle cx="15" cy="15" r="15" fill="#E8601C"/>
                <path d="M9 20 L15 9 L21 20" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
                <circle cx="15" cy="21.5" r="1.8" fill="white"/>
            </svg>
        </div>
        <div class="wbubble">${formatResponse(rawText)}</div>
    `;
    box.appendChild(row);
    scrollBottom();
}

/* ── format bot response into clean visual HTML ───────────────── */
function formatResponse(text) {
    let html = "";

    const sections = text.split(/\n{2,}/);

    sections.forEach(section => {
        const trimmed = section.trim();
        if (!trimmed) return;

        /* ── contact block detection ── */
        if (trimmed.includes("📧") || trimmed.includes("📞") || trimmed.includes("📍")) {
            html += `
                <div class="resp-contact">
                    ${inlineFormat(trimmed).replace(/\n/g, '<br>')}
                </div>
            `;
            return;
        }

        /* ── numbered / bullet list ── */
        const lines = trimmed.split("\n").map(l => l.trim()).filter(Boolean);
        const isList = lines.length > 1 && lines.every(l =>
            /^(\d+[\.\)]\s|\*\s|-\s|•\s)/.test(l)
        );
        if (isList) {
            const items = lines.map(l =>
                l.replace(/^(\d+[\.\)]\s|\*\s|-\s|•\s)/, "").trim()
            );
            html += `<ul class="resp-list">${items.map(i => `<li>${inlineFormat(i)}</li>`).join("")}</ul>`;
            return;
        }

        /* ── key: value highlight (single line, short) ── */
        if (/^[^:]{2,30}:\s*.+$/.test(trimmed) && lines.length === 1) {
            const [key, ...rest] = trimmed.split(":");
            html += `<div class="resp-highlight"><strong>${escHtml(key.trim())}:</strong> ${inlineFormat(rest.join(":").trim())}</div>`;
            return;
        }

        /* ── multi-line key-value block ── */
        const isKV = lines.length > 1 && lines.filter(l => /^[^:]{2,30}:\s*.+$/.test(l)).length >= lines.length * 0.6;
        if (isKV) {
            html += `<div class="resp-highlight">${lines.map(l => {
                const [k, ...v] = l.split(":");
                return `<strong>${escHtml(k.trim())}:</strong> ${inlineFormat(v.join(":").trim())}<br>`;
            }).join("")}</div>`;
            return;
        }

        /* ── bullet point detection ── */
        if (trimmed.includes("•")) {
            const parts = trimmed
                .split("•")
                .map(item => item.trim())
                .filter(item => item);

            html += `
                <ul class="resp-list">
                    ${parts.map(item =>
                        `<li>${inlineFormat(item)}</li>`
                    ).join("")}
                </ul>
            `;
            return;
        }

        /* ── plain paragraph ── */
        const para = inlineFormat(lines.join("<br>"));
        html += `<p>${para}</p>`;
    });

    return html || `<p>${inlineFormat(text)}</p>`;
}

/* ── inline formatting: bold, tags ─────────────────────────────── */
function inlineFormat(str) {
    return escHtml(str)
        .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
        .replace(/\*(.+?)\*/g, "<em>$1</em>")
        .replace(/(\+91[\d\s\-]{9,}|\+\d[\d\s\-]{7,})/g, '<a href="tel:$1" style="color:var(--orange);font-weight:500">$1</a>')
        .replace(/([\w.+-]+@[\w-]+\.[\w.]+)/g, '<a href="mailto:$1" style="color:var(--orange);font-weight:500">$1</a>');
}

document.addEventListener("DOMContentLoaded", () => {
    const inp = document.getElementById("w-input");
    if (inp) inp.addEventListener("keydown", e => {
        if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
    });
});

/* ── Inline Contact Form ───────────────────────────────────────── */
async function submitContactForm() {
    const name = document.getElementById("wcf-name").value.trim();
    const email = document.getElementById("wcf-email").value.trim();
    const phone = document.getElementById("wcf-phone").value.trim();

    if (!name || !email || !phone) {
        alert("Please fill in all fields.");
        return;
    }

    document.getElementById("widget-contact-form").style.display = "none";
    document.getElementById("wcf-name").value = "";
    document.getElementById("wcf-email").value = "";
    document.getElementById("wcf-phone").value = "";

    const message = `My name is ${name}\n${email}\n${phone}`;
    appendUserMsg(message);

    const typing = document.getElementById("widget-typing");
    typing.style.display = "flex";

    try {
        const res = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question: message, session_id: getSessionId() })
        });
        const data = await res.json();
        typing.style.display = "none";
        appendBotMsg(data.answer);

        if (
            data.answer.includes("Full Name")
            &&
            data.answer.includes("Email Address")
            &&
            data.answer.includes("Phone Number")
        ) {
            setTimeout(showContactForm, 300);
        }

    } catch {
        typing.style.display = "none";
        appendBotMsg("Sorry, we couldn't submit your details. Please try again.");
    }
}

function showContactForm() {
    const form = document.getElementById("widget-contact-form");
    if (form) form.style.display = "block";
}

/* ── helpers ────────────────────────────────────────────────────── */
function escHtml(str) {
    return String(str)
        .replace(/&/g,"&amp;").replace(/</g,"&lt;")
        .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
}

function scrollBottom() {
    const box = document.getElementById("widget-messages");
    if (box) box.scrollTop = box.scrollHeight;
}
