FROM debian:12
#FROM debian:bookworm-slim

ENV DEBIAN_FRONTEND="noninteractive"
ENV http_proxy $http_proxy

# From https://github.com/Pi-Apps-Coders/box86-debs and https://github.com/Pi-Apps-Coders/box64-debs
RUN printf "Types: deb\nURIs: http://Pi-Apps-Coders.github.io/box86-debs/debian\nSuites: ./\nAllow-Insecure: yes\nTrusted: yes\n" > /etc/apt/sources.list.d/box86.sources && \
    printf "Types: deb\nURIs: http://Pi-Apps-Coders.github.io/box64-debs/debian\nSuites: ./\nAllow-Insecure: yes\nTrusted: yes\n" > /etc/apt/sources.list.d/box64.sources
# Install box86 and box64 (note commands for box86 will be different for 32bit host)
RUN dpkg --add-architecture armhf && \
    apt-get update && \
    apt-get install --yes --no-install-recommends box86-generic-arm:armhf box64-generic-arm

# Install libraries needed to run box
RUN apt-get install --yes --no-install-recommends wget curl libc6:armhf libstdc++6:armhf ca-certificates sudo gpg

# `cabextract` is needed by winetricks to install most libraries
# `xvfb` is needed in wine to spawn display window because some Windows program can't run without it (using `xvfb-run`)
# If you are sure you don't need it, feel free to remove
RUN apt install -y cabextract xvfb

# Clean up
RUN apt-get -y autoremove \
 && apt-get clean autoclean \
 && rm -rf /tmp/* /var/tmp/* /var/lib/apt/lists

# Install wine, wine64, and winetricks
COPY install-wine.sh /
RUN bash /install-wine.sh \
 && rm /install-wine.sh

# Install box wrapper for wine
COPY wrap-wine.sh /
RUN bash /wrap-wine.sh \
 && rm /wrap-wine.sh

ENV http_proxy=

WORKDIR /root
ENTRYPOINT ["bash", "-c"]
CMD ["bash"]

# vim: ft=dockerfile
