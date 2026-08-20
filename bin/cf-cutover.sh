#!/usr/bin/env bash
# Point praxis-research.org at GitHub Pages, in Cloudflare.
#
#   export CLOUDFLARE_API_TOKEN=...      # needs Zone:DNS:Edit on this zone
#   bin/cf-cutover.sh                    # dry run, prints the plan
#   bin/cf-cutover.sh --apply            # make the change
#
# Touches ONLY the A/AAAA/CNAME records for the apex and www. MX, TXT, SPF and
# everything else are left alone — Google Workspace mail runs on this domain.
#
# Records are created PROXIED. This domain sends HSTS with a two-year max-age,
# so the gap between DNS moving and GitHub issuing its own certificate would be
# a hard failure for returning visitors, not a warning they can click through.
# Cloudflare's edge certificate already covers the apex and *.praxis-research.org,
# so proxying removes the gap entirely.
set -euo pipefail

ZONE="praxis-research.org"
TARGET="praxis-research.github.io"
APPLY=false
[[ "${1:-}" == "--apply" ]] && APPLY=true

die() { echo "error: $*" >&2; exit 1; }

# The token comes from the environment, or from a file so it never has to be
# typed into a shared terminal or pasted into a chat log.
TOKEN_FILE="${CLOUDFLARE_TOKEN_FILE:-$HOME/.config/praxis/cloudflare-token}"
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" && -f "$TOKEN_FILE" ]]; then
  perms=$(stat -f '%Lp' "$TOKEN_FILE" 2>/dev/null || stat -c '%a' "$TOKEN_FILE")
  [[ "$perms" == "600" || "$perms" == "400" ]] ||
    die "$TOKEN_FILE is mode $perms — must be 600. Run: chmod 600 $TOKEN_FILE"
  CLOUDFLARE_API_TOKEN=$(tr -d '[:space:]' < "$TOKEN_FILE")
fi

if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  cat >&2 <<MSG
No Cloudflare token found.

Put it in a file — it is never printed, and never enters a shell history:

  mkdir -p ~/.config/praxis
  nano ~/.config/praxis/cloudflare-token     # paste, save, quit
  chmod 600 ~/.config/praxis/cloudflare-token

The token needs Zone:DNS:Edit scoped to $ZONE only. Revoke it after the
cutover at https://dash.cloudflare.com/profile/api-tokens
MSG
  exit 1
fi

API="https://api.cloudflare.com/client/v4"
auth=(-H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json")

# GitHub Pages apex addresses.
A_RECORDS=(185.199.108.153 185.199.109.153 185.199.110.153 185.199.111.153)
AAAA_RECORDS=(2606:50c0:8000::153 2606:50c0:8001::153 2606:50c0:8002::153 2606:50c0:8003::153)

zone_id=$(curl -s "${auth[@]}" "$API/zones?name=$ZONE" | python3 -c '
import json,sys
d=json.load(sys.stdin)
if not d.get("success"): sys.exit("cloudflare: "+json.dumps(d.get("errors")))
r=d.get("result") or sys.exit("zone not found or token lacks access")
print(r[0]["id"])')
echo "zone $ZONE -> $zone_id"

records=$(curl -s "${auth[@]}" "$API/zones/$zone_id/dns_records?per_page=200")

# Records we will remove: A/AAAA/CNAME on the apex and on www, and nothing else.
doomed=$(echo "$records" | python3 -c '
import json,sys
zone=sys.argv[1]
d=json.load(sys.stdin)
if not d.get("success"): sys.exit("cloudflare: "+json.dumps(d.get("errors")))
for r in d["result"]:
    if r["type"] in ("A","AAAA","CNAME") and r["name"] in (zone, "www."+zone):
        print(r["id"], r["type"], r["name"], r["content"], "proxied" if r.get("proxied") else "dns-only")
' "$ZONE")

echo
echo "will DELETE:"
[[ -n "$doomed" ]] && echo "$doomed" | sed 's/^/  - /' || echo "  (none)"
echo
echo "will CREATE (all PROXIED — see the note in DEPLOY.md about HSTS):"
for ip in "${A_RECORDS[@]}";    do echo "  + A     $ZONE -> $ip"; done
for ip in "${AAAA_RECORDS[@]}"; do echo "  + AAAA  $ZONE -> $ip"; done
echo "  + CNAME www.$ZONE -> $TARGET"
echo
echo "untouched: MX, TXT/SPF, and every other record type."

if ! $APPLY; then
  echo
  echo "dry run. re-run with --apply to make the change."
  exit 0
fi

# The records being deleted are Cloudflare-proxied, so their real targets are
# not visible in public DNS. Save them before touching anything, or a rollback
# has nothing to restore from.
backup="dns-backup-$ZONE.json"
echo "$records" | python3 -c '
import json,sys
zone=sys.argv[1]
d=json.load(sys.stdin)
keep=[r for r in d["result"]
      if r["type"] in ("A","AAAA","CNAME") and r["name"] in (zone,"www."+zone)]
json.dump(keep, open(sys.argv[2],"w"), indent=2)
print(f"saved {len(keep)} records to {sys.argv[2]}")
' "$ZONE" "$backup"

echo
while read -r id type name content _; do
  [[ -z "${id:-}" ]] && continue
  echo "deleting $type $name ($content)"
  curl -s -X DELETE "${auth[@]}" "$API/zones/$zone_id/dns_records/$id" >/dev/null
done <<< "$doomed"

create() { # type name content
  echo "creating $1 $2 -> $3"
  out=$(curl -s -X POST "${auth[@]}" "$API/zones/$zone_id/dns_records" \
    --data "$(python3 -c '
import json,sys
print(json.dumps({"type":sys.argv[1],"name":sys.argv[2],"content":sys.argv[3],
                  "ttl":1,"proxied":True}))' "$1" "$2" "$3")")
  echo "$out" | python3 -c '
import json,sys
d=json.load(sys.stdin)
if not d.get("success"): sys.exit("  FAILED: "+json.dumps(d.get("errors")))'
}

for ip in "${A_RECORDS[@]}";    do create A    "$ZONE" "$ip"; done
for ip in "${AAAA_RECORDS[@]}"; do create AAAA "$ZONE" "$ip"; done
create CNAME "www.$ZONE" "$TARGET"

echo
echo "done. propagation is usually seconds on Cloudflare."
echo "previous records saved to $backup — that is what a rollback restores."
echo
echo "Records are proxied, so Cloudflare terminates TLS with its own certificate"
echo "and forwards to GitHub Pages. There is no certificate gap. Do NOT set the"
echo "zone SSL mode to Full (strict): GitHub serves a *.github.io certificate to"
echo "Cloudflare, which strict mode rejects with a 526."
