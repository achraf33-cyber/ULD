# llama-dashboard wiki

Welcome to the **llama-dashboard** wiki. Start with [GPU & runtime limitations](GPU-Runtime-Limitations).

## Pages

- [GPU & runtime limitations](GPU-Runtime-Limitations) — multi-GPU and multi-vendor rules
- [Wizard guide](Wizard-Guide) — create-instance flow
- [Runtimes](Runtimes) — installed llama.cpp engines
- [Architecture](Architecture) — system design
- [Deployment](Deployment) — install and systemd

## Repository docs

The same content lives under `docs/` in the git repo for version control alongside code.

## Sync this wiki to Gitea

Enable wiki on the repo in Gitea (Settings → Wiki), then:

```bash
git clone http://192.168.10.14/achraf/llama-dashboard.wiki.git
cd llama-dashboard.wiki
cp ../llama-dashboard/wiki/*.md .
git add .
git commit -m "Sync wiki from repo wiki/ directory"
git push
```

Or from this directory after clone:

```bash
rsync -av /root/llama-dashboard/wiki/ ./llama-dashboard.wiki/
```
