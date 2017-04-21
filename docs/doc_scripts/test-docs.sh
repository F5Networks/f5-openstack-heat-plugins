#!/usr/bin/env bash

set -e
#set -x

echo "Installing dependencies"
pip install --user -r requirements.txt

echo "Building docs and Checking links with Sphinx"
make -C docs html
make -C docs linkcheck

echo "Checking grammar and style"
write-good `find ./docs -not \( -path ./docs/drafts -prune \) -name '*.rst'` --passive --so --no-illusion --thereIs --cliches