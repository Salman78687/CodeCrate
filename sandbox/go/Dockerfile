# Go sandbox image: golang plus a pre-built cache of the commonly used standard
# library packages. Without it, every run compiles the runtime from scratch,
# which takes 20-40 seconds under the sandbox's CPU limit.
FROM golang:1.27

ENV GOTOOLCHAIN=local
COPY warm.go /tmp/warm/main.go
RUN cd /tmp/warm \
    && GOCACHE=/gocache GOFLAGS=-trimpath go build -o /dev/null main.go \
    && rm -rf /tmp/warm \
    && chmod -R a+rX /gocache
