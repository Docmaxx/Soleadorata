"""Surveille la disponibilité d'un cigare sur des boutiques en ligne et alerte via Telegram.

Stdlib uniquement (aucune dépendance à installer).

Usage :
    python watcher.py                 # un passage : vérifie, alerte, met à jour l'état
    python watcher.py --dry-run       # affiche les résultats sans alerter ni écrire l'état
    python watcher.py --test-telegram # envoie un message de test
"""

import argparse
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
TARGETS_FILE = os.path.join(HERE, "targets.json")
STATE_FILE = os.environ.get("CIGAR_STATE_FILE", os.path.join(HERE, "state.json"))

IN, OUT, UNKNOWN = "in", "out", "unknown"

# Nombre d'échecs consécutifs (≈ 5 min chacun) avant d'alerter qu'un site n'est plus surveillé.
FAILURE_ALERT_THRESHOLD = 12

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

IN_STOCK_SCHEMA = {
    "instock", "limitedavailability", "onlineonly", "instoreonly", "preorder", "presale",
}
OUT_STOCK_SCHEMA = {
    "outofstock", "soldout", "discontinued", "backorder",
}

OUT_PHRASES = [
    "ausverkauft", "nicht vorrätig", "nicht lieferbar", "nicht an lager",
    "derzeit nicht verfügbar", "nicht verfügbar", "zurzeit nicht erhältlich",
    "épuisé", "rupture de stock", "en rupture", "indisponible", "plus disponible",
    "out of stock", "sold out", "currently unavailable",
]
IN_PHRASES = [
    "in den warenkorb", "sofort lieferbar", "an lager", "auf lager", "lieferbar",
    "ajouter au panier", "en stock", "add to cart", "add to basket", "in stock",
]


class FetchError(Exception):
    pass


class NotFound(Exception):
    pass


def fetch(url, accept="text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8"):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": accept,
        "Accept-Language": "fr-CH,fr;q=0.9,de-CH;q=0.8,en;q=0.7",
    })
    last_err = None
    for attempt in range(2):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                charset = resp.headers.get_content_charset() or "utf-8"
                return resp.geturl(), resp.read().decode(charset, errors="replace")
        except urllib.error.HTTPError as e:
            if e.code in (404, 410):
                raise NotFound(f"HTTP {e.code}")
            last_err = f"HTTP {e.code}"
        except Exception as e:  # réseau, timeout, TLS
            last_err = f"{type(e).__name__}: {e}"
        if attempt == 0:
            time.sleep(3)
    raise FetchError(last_err)


# --------------------------------------------------------------------------- stratégies

def check_shopify(url):
    """Shopify expose /products/<handle>.js avec la dispo par variante."""
    base = url.split("?")[0].rstrip("/")
    _, body = fetch(base + ".js", accept="application/json")
    data = json.loads(body)
    variants = data.get("variants") or []
    available = [v for v in variants if v.get("available")]
    details = ", ".join(
        f"{v.get('title', '?')} : CHF {v.get('price', 0) / 100:.2f}" for v in available
    )
    return (IN if data.get("available") else OUT), details, data.get("title", "")


def _walk_availability(node, found):
    if isinstance(node, dict):
        avail = node.get("availability")
        if isinstance(avail, str):
            price = node.get("price") or node.get("lowPrice")
            currency = node.get("priceCurrency", "")
            found.append((avail, f"{currency} {price}".strip() if price else ""))
        for v in node.values():
            _walk_availability(v, found)
    elif isinstance(node, list):
        for v in node:
            _walk_availability(v, found)


def _schema_state(value):
    key = value.rsplit("/", 1)[-1].strip().lower()
    if key in IN_STOCK_SCHEMA:
        return IN
    if key in OUT_STOCK_SCHEMA:
        return OUT
    return UNKNOWN


def check_structured(page):
    """schema.org JSON-LD, puis microdata/meta. Retourne (état, détails) ou None."""
    found = []
    for block in re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        page, flags=re.S | re.I,
    ):
        try:
            _walk_availability(json.loads(block.strip()), found)
        except ValueError:
            continue
    states = [(_schema_state(a), p) for a, p in found]
    states = [s for s in states if s[0] != UNKNOWN]
    if states:
        ins = [p for s, p in states if s == IN]
        return (IN, ", ".join(p for p in ins if p)) if ins else (OUT, "")

    # Microdata : itemprop="availability" href/content=".../InStock"
    micro = re.findall(
        r'itemprop=["\']availability["\'][^>]*(?:href|content)=["\']([^"\']+)["\']'
        r'|(?:href|content)=["\']([^"\']+)["\'][^>]*itemprop=["\']availability["\']',
        page, flags=re.I,
    )
    micro_states = {_schema_state(a or b) for a, b in micro} - {UNKNOWN}
    if micro_states:
        return (IN if IN in micro_states else OUT), ""

    # Open Graph : <meta property="product:availability" content="instock">
    m = re.search(
        r'property=["\'](?:og|product):availability["\'][^>]*content=["\']([^"\']+)', page, re.I
    )
    if m:
        state = _schema_state(m.group(1).replace(" ", ""))
        if state != UNKNOWN:
            return state, ""
    return None


def check_woocommerce(page):
    """WooCommerce marque le conteneur produit avec la classe instock / outofstock."""
    m = re.search(r'<div[^>]+id=["\']product-\d+["\'][^>]*class=["\']([^"\']+)', page, re.I)
    if not m:
        m = re.search(r'class=["\']([^"\']*\bproduct\b[^"\']*\b(?:instock|outofstock)\b[^"\']*)',
                      page, re.I)
    if m:
        classes = m.group(1).split()
        if "outofstock" in classes:
            return OUT, ""
        if "instock" in classes:
            return IN, ""
    return None


def _visible_text(page):
    page = re.sub(r"<(script|style|noscript)[^>]*>.*?</\1>", " ", page, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(text)).lower()


def check_keywords(page):
    text = _visible_text(page)
    has_out = any(p in text for p in OUT_PHRASES)
    # "nicht lieferbar" contient "lieferbar" : on retire les formules négatives d'abord.
    for p in OUT_PHRASES:
        text = text.replace(p, " ")
    has_in = any(p in text for p in IN_PHRASES)
    if has_out and not has_in:
        return OUT, ""
    if has_in and not has_out:
        return IN, ""
    return None


def check_target(target, must_contain):
    """Retourne (état, détails, erreur)."""
    url = target["url"]
    strategy = target.get("strategy", "auto")
    try:
        if strategy == "shopify":
            state, details, title = check_shopify(url)
            if not all(w in title.lower() for w in must_contain):
                return UNKNOWN, "", f"titre inattendu : {title!r}"
            return state, details, None

        final_url, page = fetch(url)
        text = _visible_text(page)
        if not all(w in text for w in must_contain):
            if final_url != url:
                return OUT, "", None  # redirection vers une catégorie/accueil = produit retiré
            return UNKNOWN, "", "produit introuvable dans la page"

        for check in (check_structured, check_woocommerce, check_keywords):
            result = check(page)
            if result:
                return result[0], result[1], None
        return UNKNOWN, "", "stock indéterminable (aucun signal fiable)"
    except NotFound:
        return OUT, "", None  # page supprimée : considérée indisponible
    except FetchError as e:
        return UNKNOWN, "", str(e)
    except Exception as e:
        return UNKNOWN, "", f"{type(e).__name__}: {e}"


# --------------------------------------------------------------------------- Telegram

def send_telegram(text):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("!! TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID manquants, message non envoyé :\n" + text)
        return False
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": "false",
    }).encode()
    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage", data=data)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"!! Échec envoi Telegram : {e}")
        return False


def fmt_available(product, target, details):
    lines = [
        f"🚨 <b>{html.escape(product)} DISPONIBLE</b>",
        f"🏪 {html.escape(target['shop'])}",
    ]
    if details:
        lines.append(f"💰 {html.escape(details)}")
    lines.append(f"👉 <a href=\"{html.escape(target['url'])}\">ACHETER MAINTENANT</a>")
    return "\n".join(lines)


# --------------------------------------------------------------------------- état

def load_state():
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def run(dry_run=False):
    with open(TARGETS_FILE, encoding="utf-8") as f:
        config = json.load(f)
    product = config["product"]
    must_contain = [w.lower() for w in config.get("must_contain", [])]
    state = load_state()
    first_run = not state
    initial_in = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    for target in config["targets"]:
        url = target["url"]
        entry = state.setdefault(url, {"state": UNKNOWN, "failures": 0})
        current, details, error = check_target(target, must_contain)
        print(f"[{current:>7}] {target['shop']:<38} {details or error or ''}")

        if dry_run:
            continue

        if current == UNKNOWN:
            entry["failures"] = entry.get("failures", 0) + 1
            entry["last_error"] = error
            if entry["failures"] == FAILURE_ALERT_THRESHOLD:
                send_telegram(
                    f"⚠️ Surveillance aveugle sur <b>{html.escape(target['shop'])}</b> "
                    f"depuis ~1h\n{html.escape(error or '')}\n{html.escape(url)}"
                )
            continue  # on garde le dernier état connu : pas de fausse ré-alerte

        if entry.get("failures", 0) >= FAILURE_ALERT_THRESHOLD:
            send_telegram(f"✅ Surveillance rétablie sur <b>{html.escape(target['shop'])}</b>")
        entry["failures"] = 0
        entry.pop("last_error", None)

        if current == IN and first_run:
            initial_in.append(target)  # un seul message récapitulatif au démarrage
        elif current == IN and entry.get("state") != IN:
            if send_telegram(fmt_available(product, target, details)):
                entry["alerted_at"] = now
            else:
                continue  # alerte non partie : on réessaiera au prochain passage
        if current != entry.get("state"):
            entry["changed_at"] = now
        entry["state"] = current
        entry["checked_at"] = now

    if dry_run:
        return
    if first_run:
        lines = [f"🟢 Surveillance <b>{html.escape(product)}</b> démarrée "
                 f"({len(config['targets'])} pages)."]
        if initial_in:
            lines.append("Déjà en stock chez :")
            lines += [f"• <a href=\"{html.escape(t['url'])}\">{html.escape(t['shop'])}</a>"
                      for t in initial_in]
        lines.append("Prochaines alertes : uniquement les retours en stock.")
        send_telegram("\n".join(lines))
    save_state(state)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test-telegram", action="store_true")
    args = parser.parse_args()
    if args.test_telegram:
        ok = send_telegram("✅ Cigar Watch connecté. Tu recevras les alertes ici.")
        sys.exit(0 if ok else 1)
    run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
