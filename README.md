![license](https://badgen.net/github/license/flavien-perier/discord-agent)
[![docker pulls](https://badgen.net/docker/pulls/flavienperier/discord-agent)](https://hub.docker.com/r/flavienperier/discord-agent)
[![ci status](https://badgen.net/github/checks/flavien-perier/discord-agent)](https://github.com/flavien-perier/discord-agent)

# Discord Agent

Discord bot that monitors the [bonjour-la-fuite](https://bonjourlafuite.eu.org/) data breach registry and sends webhook notifications when new leaks are published.

## Env variables

- BONJOUR_LA_FUITE_WEBHOOK_URL: Discord channel webhook URL (required)
- POLL_INTERVAL: Polling interval in seconds (default: 3600)

## Docker-compose example

```yaml
discord-agent:
  image: flavienperier/discord-agent
  container_name: discord-agent
  restart: always
  environment:
    BONJOUR_LA_FUITE_WEBHOOK_URL: https://discord.com/api/webhooks/...
```
