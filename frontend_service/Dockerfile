FROM rust:1 as build

RUN apt-get update && apt-get install -y libssl-dev ca-certificates && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://github.com/tailwindlabs/tailwindcss/releases/download/v3.4.6/tailwindcss-linux-x64 -o /usr/local/bin/tailwindcss
RUN chmod +x /usr/local/bin/tailwindcss

RUN cargo new --bin /app

WORKDIR /app

COPY ./Cargo.toml ./Cargo.lock ./

RUN cargo build --release

RUN rm src/*.rs

COPY ./src ./src
COPY ./.sqlx ./.sqlx
COPY ./templates ./templates
COPY ./tailwind.css ./
COPY ./tailwind.config.js ./

RUN mkdir ./public

RUN rm ./target/release/deps/ura_web*

RUN tailwindcss -c tailwind.config.js -i ./tailwind.css -o ./public/styles.css --minify
RUN cargo build --release

FROM debian:stable-slim as runner

WORKDIR /app

RUN apt-get update && apt-get install -y libssl-dev ca-certificates && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/target/release/ura-web .
COPY ./public ./public
COPY --from=build /app/public/styles.css ./public/styles.css

CMD ["./ura-web"]
