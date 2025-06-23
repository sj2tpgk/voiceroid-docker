#!/bin/sh
export http_proxy=http://192.168.1.22:4444

# branch=stable version=7.0.2 id=debian dist=bookworm tag=-1
# branch=staging version=8.11 id=debian dist=bookworm tag=-1
branch=stable version=10.0.0.0 id=debian dist=bookworm tag=-1

dir="$branch-$version-$id-$dist-$tag"
mkdir "$dir"; cd "$dir"

wget -c \
    "http://dl.winehq.org/wine-builds/${id}/dists/${dist}/main/binary-amd64/wine-${branch}-amd64_${version}~${dist}${tag}_amd64.deb" \
    "http://dl.winehq.org/wine-builds/${id}/dists/${dist}/main/binary-amd64/wine-${branch}_${version}~${dist}${tag}_amd64.deb" \
    "http://dl.winehq.org/wine-builds/${id}/dists/${dist}/main/binary-amd64/winehq-${branch}_${version}~${dist}${tag}_amd64.deb" \
    "http://dl.winehq.org/wine-builds/${id}/dists/${dist}/main/binary-i386/wine-${branch}-i386_${version}~${dist}${tag}_i386.deb" \
    "http://dl.winehq.org/wine-builds/${id}/dists/${dist}/main/binary-i386/wine-${branch}_${version}~${dist}${tag}_i386.deb" \
    "http://dl.winehq.org/wine-builds/${id}/dists/${dist}/main/binary-i386/winehq-${branch}_${version}~${dist}${tag}_i386.deb"

for i in *.deb; do
    dpkg-deb -f "$i" Depends Recommends | sed 's/^[^ ]*: //; s/\( [(|][^,]*\)*\($\|,\)/:/g' > "$i.txt"
    dpkg-deb -I "$i" >> "$i.txt"
done

