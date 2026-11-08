#!/usr/bin/env bash
# Put an episode's final video on the 'uploads' branch so the Mac's browser can pull it into YouTube Studio.
# usage: bash tools/handoff.sh episodes/NNN_slug     -> prints the raw URL (and checks it is reachable)
set -e
EP=$(cd "$1" && pwd)
NUM=$(python3 -c "import json;print('%03d' % json.load(open('$EP/meta.json'))['episode'])")
[ -s "$EP/out/final.mp4" ] || { echo "no out/final.mp4 - run finish.py first"; exit 1; }
W=$(mktemp -d); cd "$W"
git init -q -b uploads; git config user.name "Claude"; git config user.email "noreply@anthropic.com"
cp "$EP/out/final.mp4" "ep$NUM.mp4"
git add "ep$NUM.mp4"
git commit -q -m "Upload hand-off: episode $NUM

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"
git remote add origin https://github.com/azizmoiz504-dotcom/shorts-studio
git push -q -f origin uploads
URL="https://raw.githubusercontent.com/azizmoiz504-dotcom/shorts-studio/uploads/ep$NUM.mp4"
for i in 1 2 3 4 5 6; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" -r 0-99 "$URL" || true)
  [ "$CODE" = "206" ] || [ "$CODE" = "200" ] && break; sleep 10
done
echo "HANDOFF $CODE $URL"
