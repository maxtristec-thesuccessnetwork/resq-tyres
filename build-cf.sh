#!/usr/bin/env bash
# Cloudflare Pages build: copies only the public site into dist/.
# Repo notes (*.md), tools/ and unused files stay out, as .vercelignore did.
set -euo pipefail
rm -rf dist && mkdir dist
cp -R *.html *.txt *.xml favicon.ico _headers _redirects assets css fonts js .well-known dist/
rm -f dist/js/tyre.js dist/assets/work*.jpg dist/assets/logo-header.jpg
