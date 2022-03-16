# Cloudflare manager

Manages the IP address of DNS records and their cache mode.

DNS records type:

- watched_common_records: DNS is updated to current public IP with cached enabled
- watched_nocached_records: DNS is updated to current public IP with cache disabled

The rest records are ignored.

## Docker

**Note: the [publish pipeline](.github/workflows/publish.yml) is in charge of building the docker image, you shouldn't have to manually build it.**

```shell
docker buildx build -t sralloza/cloudflare-manager:1.0.0 --platform=linux/arm/v7,linux/amd64 --push .
```

To run:

```shell
docker run --env-file ENV_FILE --rm sralloza/cloudflare-manager:1.0.0
```
