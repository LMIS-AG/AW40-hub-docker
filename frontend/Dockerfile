FROM ubuntu:20.04 as build

RUN apt-get update \
 && apt-get install -y bash curl file git libglu1-mesa unzip xz-utils zip \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd -r -g 1234 flutter \
 && useradd --no-log-init -r -u 1234 -g flutter -m flutter
USER flutter:flutter
WORKDIR /home/flutter

RUN curl -o flutter_sdk.tar.xz https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.7.12-stable.tar.xz \
 && mkdir flutter-sdk \
 && tar -xJf flutter_sdk.tar.xz -C flutter-sdk --strip-components=1 \
 && rm flutter_sdk.tar.xz

ENV PATH="$PATH:/home/flutter/flutter-sdk/bin:/home/flutter/flutter-sdk/bin/cache/dart-sdk/bin"

RUN flutter precache
RUN flutter config --no-analytics

# Dummy project, to be replaced by the real deal.
RUN flutter create --sample=widgets.SingleChildScrollView.1 myapp
WORKDIR /home/flutter/myapp
RUN flutter build web

FROM nginx:alpine as serve

COPY --from=build /home/flutter/myapp/build/web /usr/share/nginx/html

HEALTHCHECK --interval=30s --timeout=2s --retries=5 \
  CMD curl -fs http://localhost:80 || exit 1
#CMD ["nginx", "-g", "daemon off;"]
