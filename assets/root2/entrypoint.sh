#!/bin/sh

cd "$(dirname "$0")" || exit 1

export WINEDLLOVERRIDES="mscoree,mshtml="
vdir=/root/Voiceroid/AHS/VOICEROID+/

[ -d "$vdir" ] || { echo "Directory $vdir not found (ensure assets/root1/Voiceroid/AHS/ exists when building)"; exit 1; }

echo Starting web server
./server.py 2137 &

echo Setting up user dictionary
mkdir -p /udic
[ -e /udic/user.dic.utf8 ] || echo '(品詞 (名詞 一般)) ((見出し語 (一声 2000)) (読み ヒトコエ) (発音 ヒトコエ) (付加情報 {accent=2-4:accent_con=*})) ;' > /udic/user.dic.utf8
chown --reference /udic /udic/user.dic.utf8
./udic_update

echo Setting up symlinks of cabocha and ipadic
ln -sf "$vdir"/yukari/lang/cabocha "$vdir"/tamiyasu/lang/cabocha
ln -sf "$vdir"/yukari/lang/ipadic  "$vdir"/tamiyasu/lang/ipadic

echo Starting Voiceroid yukari
# Note there is only a small difference in RAM usage between only launching one voiceroid and two voiceroids.
# It seems sequential launch is less likely to fail than parallel (slower tho)
./start_yukari &
while ! [ -f /root/ready_yukari ]; do
    sleep 1
done
sleep 1
./start_maki &

tail -f /dev/null

