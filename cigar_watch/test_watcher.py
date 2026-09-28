import http.server
import json
import os
import tempfile
import threading
import unittest
from unittest import mock

import watcher

JSONLD_IN = """<html><head><script type="application/ld+json">
{"@context":"https://schema.org","@type":"Product","name":"Quai d'Orsay No. 54",
 "offers":[{"@type":"Offer","price":"189.00","priceCurrency":"CHF",
            "availability":"https://schema.org/InStock"}]}
</script></head><body>Quai d'Orsay No. 54</body></html>"""

JSONLD_OUT = JSONLD_IN.replace("InStock", "OutOfStock")

WOO_OUT = """<html><body><div id="product-1347" class="product type-product outofstock">
Quai d'Orsay No. 54 <p class="stock">Rupture de stock</p></div></body></html>"""

MICRODATA_IN = """<div itemscope itemtype="http://schema.org/Product"><h1>Quai d'Orsay No. 54</h1>
<link itemprop="availability" href="http://schema.org/InStock"/></div>"""

KEYWORDS_OUT = "<h1>Quai d'Orsay No. 54</h1><span>Nicht lieferbar</span>"
KEYWORDS_IN = "<h1>Quai d'Orsay No. 54</h1><button>In den Warenkorb</button>"
AMBIGUOUS = "<h1>Quai d'Orsay No. 54</h1><button>Add to cart</button> Sold out"


class ParserTests(unittest.TestCase):
    def test_jsonld(self):
        self.assertEqual(watcher.check_structured(JSONLD_IN), (watcher.IN, "CHF 189.00"))
        self.assertEqual(watcher.check_structured(JSONLD_OUT)[0], watcher.OUT)

    def test_microdata(self):
        self.assertEqual(watcher.check_structured(MICRODATA_IN)[0], watcher.IN)

    def test_woocommerce(self):
        self.assertIsNone(watcher.check_structured(WOO_OUT))
        self.assertEqual(watcher.check_woocommerce(WOO_OUT)[0], watcher.OUT)

    def test_keywords(self):
        self.assertEqual(watcher.check_keywords(KEYWORDS_OUT)[0], watcher.OUT)
        self.assertEqual(watcher.check_keywords(KEYWORDS_IN)[0], watcher.IN)
        self.assertIsNone(watcher.check_keywords(AMBIGUOUS))


class Handler(http.server.BaseHTTPRequestHandler):
    pages = {}

    def do_GET(self):
        body = self.pages.get(self.path)
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        ctype = "application/json" if self.path.endswith(".js") else "text/html; charset=utf-8"
        self.send_header("Content-Type", ctype)
        self.end_headers()
        self.wfile.write(body.encode())

    def log_message(self, *args):
        pass


class EndToEndTests(unittest.TestCase):
    def setUp(self):
        self.server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{self.server.server_port}"
        self.tmp = tempfile.mkdtemp()
        self.targets_file = os.path.join(self.tmp, "targets.json")
        with open(self.targets_file, "w") as f:
            json.dump({
                "product": "Quai d'Orsay No. 54",
                "must_contain": ["quai", "54"],
                "targets": [
                    {"shop": "Shopify", "url": base + "/products/qdo-54", "strategy": "shopify"},
                    {"shop": "Generic", "url": base + "/qdo54.html"},
                    {"shop": "Gone", "url": base + "/missing.html"},
                ],
            }, f)
        self.patches = [
            mock.patch.object(watcher, "TARGETS_FILE", self.targets_file),
            mock.patch.object(watcher, "STATE_FILE", os.path.join(self.tmp, "state.json")),
        ]
        for p in self.patches:
            p.start()
        self.sent = []
        self.patches.append(mock.patch.object(
            watcher, "send_telegram", side_effect=lambda t: self.sent.append(t) or True))
        self.patches[-1].start()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        self.server.shutdown()

    def set_pages(self, shopify_available, generic_page):
        Handler.pages = {
            "/products/qdo-54.js": json.dumps({
                "title": "Quai d'Orsay No. 54", "available": shopify_available,
                "variants": [{"title": "Box 25", "available": shopify_available, "price": 47500}],
            }),
            "/qdo54.html": generic_page,
        }

    def test_lifecycle(self):
        # 1er passage : tout en rupture -> un seul message de démarrage.
        self.set_pages(False, JSONLD_OUT)
        watcher.run()
        self.assertEqual(len(self.sent), 1)
        self.assertIn("démarrée", self.sent[0])

        # Retour en stock sur les 2 boutiques -> 2 alertes avec lien + prix.
        self.set_pages(True, JSONLD_IN)
        watcher.run()
        self.assertEqual(len(self.sent), 3)
        self.assertIn("DISPONIBLE", self.sent[1])
        self.assertIn("CHF 475.00", self.sent[1])
        self.assertIn("CHF 189.00", self.sent[2])

        # Toujours en stock -> pas de spam.
        watcher.run()
        self.assertEqual(len(self.sent), 3)

        # Site en panne puis retour en stock : pas de ré-alerte (dernier état connu conservé).
        Handler.pages.pop("/qdo54.html")
        Handler.pages["/qdo54.html"] = "<html>erreur</html>"
        watcher.run()
        self.set_pages(True, JSONLD_IN)
        watcher.run()
        self.assertEqual(len(self.sent), 3)

        # Rupture puis re-stock -> nouvelle alerte.
        self.set_pages(False, JSONLD_OUT)
        watcher.run()
        self.set_pages(True, JSONLD_OUT)
        watcher.run()
        self.assertEqual(len(self.sent), 4)
        self.assertIn("Shopify", self.sent[3])

    def test_first_run_lists_in_stock(self):
        self.set_pages(True, JSONLD_OUT)
        watcher.run()
        self.assertEqual(len(self.sent), 1)
        self.assertIn("Déjà en stock", self.sent[0])
        self.assertIn("Shopify", self.sent[0])

    def test_failure_alert_after_threshold(self):
        self.set_pages(False, "<html>page sans le produit</html>")
        for _ in range(watcher.FAILURE_ALERT_THRESHOLD):
            watcher.run()
        self.assertTrue(any("aveugle" in m and "Generic" in m for m in self.sent))
        self.set_pages(False, JSONLD_OUT)
        watcher.run()
        self.assertIn("rétablie", self.sent[-1])


if __name__ == "__main__":
    unittest.main()
