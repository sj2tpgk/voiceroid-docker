#!/bin/sh
command -v iconv >/dev/null || { echo "iconv not found"; exit 1; }
iconv -f utf8 -t sjis -o "${2:-user.dic}" "${1:-user.dic.utf8}"
