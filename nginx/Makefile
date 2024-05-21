.PHONY: all
all: build

.PHONY: clean
clean:
	rm -rf build

.PHONY: build
build:
	set -e && \
	\
	if [ ! -d build ] ; then mkdir build ; fi && \
	\
	cd build && \
	\
	if [ ! -f 'nginx-1.26.0.tar.gz' ] ; then \
		wget 'https://nginx.org/download/nginx-1.26.0.tar.gz' -O 'nginx-1.26.0.tar.gz' ; \
	fi && \
	\
	if [ ! -d 'nginx-1.26.0' ] ; then \
		tar xvzf 'nginx-1.26.0.tar.gz' ; \
	fi && \
	\
	cd 'nginx-1.26.0' && \
	\
	BREW_CFLAGS='' ; \
	BREW_LDFLAGS='' ; \
	if [ "$$(uname)" = "Darwin" ] && command -v brew ; then \
		BREW_CFLAGS="-I$$(brew --prefix openssl)/include -I$$(brew --prefix pcre)/include" ; \
		BREW_LDFLAGS="-L$$(brew --prefix openssl)/lib -L$$(brew --prefix pcre)/lib" ; \
	fi ; \
	\
	./configure \
		--with-cc-opt="-g -O2 -fstack-protector $$BREW_CFLAGS" \
		--with-ld-opt="$$BREW_LDFLAGS" \
		\
		--with-compat \
		--with-threads \
		--with-debug \
		--with-ipv6 \
		--with-pcre \
		\
		--with-http_gzip_static_module \
		--with-http_ssl_module \
		--with-http_stub_status_module \
		--with-http_v2_module \
		\
		--with-stream \
		--with-stream_ssl_module \
		--with-stream_ssl_preread_module \
		\
		; \
	\
	make -j2 \
