.PHONY: build_x64 build_arm64 run debug apt_cache_proxy

# 1222 + 915
web_port := 2137
udic_dir := $$(pwd)/udic

build_x64:
	docker build \
		--build-arg http_proxy="$$http_proxy" \
		-t voiceroid -f Dockerfile_x64 .

build_arm64:
	docker build \
		--platform=linux/arm64 \
		--build-arg http_proxy="$$http_proxy" \
		-t voiceroid -f Dockerfile_arm64 .

run:
	docker run -it --rm -p $(web_port):2137 -v "$(udic_dir)":/udic voiceroid


debug:
	docker run -it --rm -p $(web_port):2137 -v "$(udic_dir)":/udic -p 5901:5901 -p 5902:5902 -v $$(pwd)/assets/root2:/root/2 --entrypoint bash voiceroid

apt_cache_proxy:
	ip -o -4 a | grep docker
	python apt-cache-proxy.py 4444
