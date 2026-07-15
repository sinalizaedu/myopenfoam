#!/bin/bash
set -u
cd "$(dirname "$0")/.."
REPO="$(pwd)"
TAG=radpia4dura5; FACTOR=rad:4:5; SCR="on-caso-3__${TAG}"; PC=9034
DECK="cases/_mi/${SCR}/ccx/on-caso-3.inp"
echo "=== build+run $TAG (P=$PC) ==="; date
bash brunaStuff/build_meshindep.sh on-caso-3 on-caso-3 "$FACTOR" "$TAG" yes no
sed -i.bak -E "s|^CONTACT_LOCAL_SURF, P, .*$|CONTACT_LOCAL_SURF, P, ${PC}|" "$DECK"
docker run --rm --platform=linux/amd64 -u ubuntu \
  -v "$REPO/cases:/simulation" \
  -v "$REPO/cases/_lib/libsolids4FoamModels.so:/opt/of-user/lib/libsolids4FoamModels.so:ro" \
  -w /simulation/_mi fsi-openfoam:latest \
  bash -lc "./run.sh ${SCR} on-caso-3 yes no" > "brunaStuff/run_radpia4dura5.log" 2>&1
echo "rc=$?"; tail -2 "cases/_mi/${SCR}/ccx/on-caso-3.sta" 2>/dev/null
echo "=== done ==="; date
