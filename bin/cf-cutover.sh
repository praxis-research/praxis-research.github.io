#!/usr/bin/env bash
# Point praxis-research.org at GitHub Pages, in Cloudflare.
#
#   export CLOUDFLARE_API_TOKEN=...      # needs Zone:DNS:Edit on this zone
#   bin/cf-cutover.sh                    # dry run, prints the plan
#   bin/cf-cutover.sh --apply            # make the change
#
# Touches ONLY the A/AAAA/CNAME records for the apex and www. MX, TXT, SPF and
# everything else are left alone — Google Workspace mail runs on this domain.
set -euo pipefail

ZONE="praxis-research.org"
TARGET="praxis-research.github.io"
APPLY=false
[[ "${1:-}" == "--apply" ]] && APPLY=true

: "${CLOUDFLARE_API_TOKEN:?set CLOUDFLARE_API_TOKEN (Zone:DNS:Edit on $ZONE)}"

API="https://api.cloudflare.com/client/v4"
auth=(-H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json")

# GitHub Pages apex addresses.
A_RECORDS=(185.199.108.153 185.199.109.153 185.199.110.153 185.199.111.153)
AAAA_RECORDS=(2606:50c0:8000::153 2606:50c0:8001::153 2606:50c0:8002::153 2606:50c0:8003::153)

die() { echo "error: $*" >&2; exit 1; }

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
echo "will CREATE (all DNS-only, so GitHub can issue the certificate):"
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
                  "ttl":1,"proxied":False}))' "$1" "$2" "$3")")
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
echo "next: wait for the certificate, then"
echo "  gh api -X PUT repos/praxis-research/praxis-research.github.io/pages -F https_enforced=true"
