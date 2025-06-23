#!/bin/python3

import http, http.server, os, re, string, subprocess, urllib.parse

def shell(cmd):
    return subprocess.run(cmd, shell=True)

def preproc(text:str):
    bsizes    = [80, 160, 1800] # block size for first few blocks, then the size for the all other blocks
    bsize_idx = 0               # which block size is being used?

    def split_inclusive(s, delim):
        out = []
        while s:
            m = re.search(delim, s)
            pos = m.start() if m else len(s)
            out.append(s[:pos+1])
            s = s[pos+1:]
        return out

    nonreadable = r'[^\u0000-\u00ff\u3000-\u30ff\uff00-\uffefu\u4e00-\u9faf]+'
    text = re.sub(nonreadable, "", text)
    lines = [x.strip() for x in text.splitlines()]

    # iterate through each part, splitted by whitespace and punctations
    block = ""
    out = []
    for line in lines:
        for part in split_inclusive(line, r"[\s」』．…。、]"):
            # process this part
            while part:
                bsize_now = bsizes[bsize_idx]
                if len(block) + len(part) > bsize_now:
                    # block too long, cannot be extended
                    if len(block.strip()) == 0:
                        # empty block, add this part to output
                        # ideally, should split at かな/漢字 境界, not at an arbitrary char
                        out.append(part[:bsize_now])
                        part = part[bsize_now:]
                    else:
                        # nonempty block, output it (and continue processing this part)
                        out.append(block)
                        block = ""
                    # select next block size
                    bsize_idx = min(len(bsizes) - 1, bsize_idx + 1)
                else:
                    # extend block
                    block += part
                    break
        block += "\n"

    # output remaining block
    if block:
        out.append(block)

    return out

def summary(s:str):
    if len(s) <= 15:
        return s
    else:
        return s[:15] + " ... " + s[-15:]

def getMP3(text, voice):
    lis = preproc(text)
    if len(lis) == 0:
        return b''
    yield b'\xff\xf3' # this is the first 2 bytes of the mp3 header. send some bytes early so browser download dialog will open now
    first = True
    for i, subtext in enumerate(lis):
        print("Section", i, len(subtext), summary(subtext))
        with open(f"input.txt", "w") as f:
            f.write(subtext)
        savescript = "./save_maki" if voice == "maki" else "./save_yukari"
        shell(f"{savescript} ./input.txt ./output.wav")
        shell("sleep .4")
        shell(f"sox ./output.wav -C 96 ./output.mp3")
        with open(f"./output.mp3", "rb") as f:
            while True:
                data = f.read(64 * 1024)
                if not data:
                    break
                if first:
                    yield data[2:] # skip the first 2 bytes we already sent earlier
                    first = False
                else:
                    yield data
        shell("rm -f ./output.wav ./output.mp3")

def validate_dictvalue(dictvalue):
    for line in dictvalue.splitlines():
        if not line.strip():
            continue
        # example
        # (品詞 (名詞 固有名詞 人名 名)) ((見出し語 (機械 2000)) (読み キカイ) (発音 キカイ) (付加情報 {accent=0-3:accent_con=*})) ;
        t = r"[^()]+"
        m = re.match(rf"\(品詞 \({t}\)\) \(\(見出し語 \({t}\)\) \(読み {t}\) \(発音 {t}\) \(付加情報 {t}\)\) ;", line)
        if not m:
            return f"Invalid line: {line}"
    return ""

def get_dictvalue():
    with open("/udic/user.dic.utf8") as f:
        dictvalue = f.read()
    return dictvalue

def set_dictvalue(dictvalue):
    st = os.stat("/udic/user.dic.utf8")
    with open("/udic/user.dic.utf8", "w") as f:
        f.write(dictvalue)
    os.chown("/udic/user.dic.utf8", st.st_uid, st.st_gid)
    shell("./udic_update")
    shell("./stop_maki; ./stop_yukari; ./start_maki & ./start_yukari &")

class MyHandler(http.server.BaseHTTPRequestHandler):

    def log_request(self, code='-', size='-'):
        if isinstance(code, http.HTTPStatus):
            code = code.value
        self.log_message('"%s" %s %s',
                         self.requestline.encode("iso-8859-1").decode("utf-8"), str(code), str(size))

    def _respond(self, code, *headers):
        self.send_response(code)
        for k, v in headers:
            self.send_header(k, v)
        self.end_headers()

    def _parse_request(self):
        path = self.path.encode("iso-8859-1").decode("utf-8")
        urlparse = urllib.parse.urlparse(path)
        pathl = [x for x in urlparse.path.split("/") if x]
        query = { k: v[0] for k, v in urllib.parse.parse_qs(urlparse.query).items() if len(v) }
        return pathl, query

    def _route(self, query_override={}):
        pathl, query = self._parse_request()
        query = { **query, **query_override }
        if 0:
            pass

        elif not (os.path.exists("/root/ready_yukari") and os.path.exists("/root/ready_tamiyasu")):
            self._respond(200, ("content-type", "text/html"))
            self.wfile.write(b'Voiceroid is starting up ...<meta http-equiv=refresh content=3>')

        elif pathl == ["favicon.ico"]:
            self._respond(404)

        elif pathl == ["dict"]:
            self._respond(200, ("content-type", "text/html"))
            with open("./server-dict.html", "r") as f:
                dictvalue = get_dictvalue()
                html = string.Template(f.read()).safe_substitute(dictvalue=dictvalue)
                self.wfile.write(html.encode())

        elif pathl == ["dictset"]:
            dictvalue = query.get("dictvalue")
            if err := validate_dictvalue(dictvalue):
                self._respond(400, ("content-type", "text/plain; charset=utf-8"))
                self.wfile.write(b"Bad dict format: " + err.encode())
            else:
                set_dictvalue(dictvalue)
                self._respond(302, ("content-type", "text/plain"), ("location", "/"))

        elif not query.get("q"):
            self._respond(200, ("content-type", "text/html"))
            with open("./server.html", "r") as f:
                self.wfile.write(f.read().encode())

        else:
            voice = query.get("voice")
            if voice not in ["yukari", "maki"]: voice = "yukari"
            action = query.get("action")
            if action not in ["save", "play"]: action = "play"
            headers = [("content-type", "audio/mp3")]
            if action == "save":
                headers.append(("content-disposition", 'attachment; filename="voice.mp3"'))
            self._respond(200, *headers)
            self.wfile.write(b"")
            for blob in getMP3(query.get("q"), voice):
                self.wfile.write(blob)

    def do_GET(self):
        self._route()

    def do_POST(self):
        length = int(self.headers["content-length"])
        text = self.rfile.read(length).decode()
        if "=" not in text:
            # when curl http://... -d hello
            query_override = { "q": urllib.parse.unquote_plus(text) }
        elif self.headers["content-type"] != "application/x-www-form-urlencoded":
            self._respond(400)
            self.wfile.write(b"Bad request: bad content-type")
            return
        else:
            parsed = urllib.parse.parse_qs(text)
            if "q" not in parsed:
                self._respond(400)
                self.wfile.write(b"Bad request: missing q parameter")
                return
            else:
                query_override = { k: v[0] for k, v in parsed.items() }
        # process voice
        self._route(query_override)

if __name__ == "__main__":
    import sys
    host = "0.0.0.0"
    port = int(sys.argv[1])
    httpd = http.server.HTTPServer((host, port), MyHandler)
    print(f"Server at http://{host}:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
