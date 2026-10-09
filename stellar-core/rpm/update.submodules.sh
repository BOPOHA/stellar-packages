#!/bin/bash
set -euo pipefail

TMP_SPEC=$(mktemp /tmp/stellar-core.spec.XXXXXX)
TMP_GITMODULES=$(mktemp /tmp/stellar-core.gitmodules.XXXXXX)
trap 'rm -f "$TMP_SPEC" "$TMP_GITMODULES"' EXIT

# Stellar core user functions
STELLAR_CORE_VERSION=$(rpmspec -q --qf "%{Version}" stellar-core.spec)
API_GH_STELLAR_CORE=https://api.github.com/repos/stellar/stellar-core
REF=v${STELLAR_CORE_VERSION}

curl -fsSL "$API_GH_STELLAR_CORE/contents/.gitmodules?ref=$REF" \
  | jq -r .content \
  | base64 --decode > "$TMP_GITMODULES"

mapfile -t StCoreSubModuleDirs < <(
  git config --file "$TMP_GITMODULES" --get-regexp '^submodule\..*\.path$' \
    | awk '{print $2}'
)
declare -A StCoreSubModuleCommits=()

function stellar_core_submodule_sources() {
  ST_CORE_SUBMODULE_SRC=""
  declare -i i=0
  for smod in "${StCoreSubModuleDirs[@]}"; do
    Submodule=$(curl -fsSL "$API_GH_STELLAR_CORE/contents/${smod}?ref=$REF")
    Commit=$(jq -r .sha <<< "$Submodule")
    StCoreSubModuleCommits["$smod"]=$Commit
    Repository=$(jq -r .submodule_git_url <<< "$Submodule")
    Repository=${Repository#https://github.com/}
    Repository=${Repository%.git}
    SourceNumber=$((100 + i))
    SourceUrl="https://api.github.com/repos/${Repository}/tarball/${Commit}#/${Repository//\//-}-${Commit:0:7}.tar.gz"
    ST_CORE_SUBMODULE_SRC+="Source${SourceNumber}: $SourceUrl\n"
    i+=1
  done
  printf '%b' "$ST_CORE_SUBMODULE_SRC"
}

function stellar_core_submodule_prep() {
  ST_CORE_SUBMODULE_PREP=""
  declare -i i=0
  for smod in "${StCoreSubModuleDirs[@]}"; do
    SourceNumber=$((100 + i))
    ST_CORE_SUBMODULE_PREP+="tar -zxf %{SOURCE${SourceNumber}} --strip-components 1 -C ${smod}/\n"
    if [[ "$smod" == src/rust/soroban/* ]]; then
      ST_CORE_SUBMODULE_PREP+="echo '${StCoreSubModuleCommits[$smod]}' > ${smod}/.git-revision\n"
    fi
    i+=1
  done
  printf '%b' "$ST_CORE_SUBMODULE_PREP"
}
# end Stellar core user functions


MARKER_SOURCES='submodule sources'
MARKER_PREP='submodules setup'

{
  sed    "/# START: $MARKER_SOURCES/q"                          stellar-core.spec
  stellar_core_submodule_sources
  sed -n "/^# END: $MARKER_SOURCES/,/^# START: $MARKER_PREP/p"  stellar-core.spec
  stellar_core_submodule_prep
  sed -n "/# END: $MARKER_PREP/,//p"                            stellar-core.spec
} > $TMP_SPEC

mv "$TMP_SPEC" stellar-core.spec
echo SUCCESS
