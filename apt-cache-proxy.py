import hashlib, http.server, json, os, re, sys, urllib.request

# Caching http proxy that is just enough for apt-get

# Usage:
#   $ python caching.py 8080
#   $ http_proxy=http://localhost:8080/ CMD ...

# Maybe only .deb should be cached (to properly handle upstream update of catalog files, keys etc)

cachedir = "_http_cache"
os.makedirs(cachedir, exist_ok=True)

def cache_path(x):
    return cachedir + os.sep + hashlib.md5(str(x).encode()).hexdigest()[:16]

class HTTPProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if m := re.match(r"GET (.*) HTTP/[0-9.]+$", self.requestline):
            url = m.group(1)
            cache = cache_path(url)
            try:
                # Use cache
                with open(cache, "rb") as f:
                    with open(cache + ".info.json", "r") as fj:
                        self.send_response(200)
                        for k, v in json.load(fj)["headers"]:
                            self.send_header(k, v)
                        self.end_headers()
                        while True:
                            data = f.read(1024)
                            if not data:
                                break
                            self.wfile.write(data)
                return
            except FileNotFoundError:
                try:
                    # Proxy request and save response
                    req = urllib.request.Request(url=url, headers=self.headers)
                    with urllib.request.urlopen(req) as res:
                        with open(cache, "wb") as f:
                            with open(cache + ".info.json", "w") as fj:
                                jso = {
                                    "url": url,
                                    "headers": [[k, v] for k, v in res.getheaders()],
                                }
                                json.dump(jso, fj, separators=(",", ":"))
                            self.send_response(res.status)
                            for k, v in res.getheaders():
                                self.send_header(k, v)
                            self.end_headers()
                            while True:
                                data = res.read(1024)
                                if not data:
                                    break
                                self.wfile.write(data)
                                f.write(data)
                    return
                except:
                    try:
                        # Remove incomplete cache
                        os.remove(cache)
                        os.remove(cache + ".info.json")
                    except:
                        pass
        # Error
        self.send_response(500)
        self.end_headers()


host, port = "0.0.0.0", int(sys.argv[1])

try:
    print(f"http_proxy=http://<ip>:{port}")
    http.server.HTTPServer((host, port), HTTPProxyHandler).serve_forever()
except KeyboardInterrupt:
    pass

