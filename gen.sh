#!/bin/bash

set -euo pipefail

(cd clients/rust && ./gen.sh)
