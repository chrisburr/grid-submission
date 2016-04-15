#!/usr/bin/env bash

CONDA_INSTALL_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )/.miniconda"
if [ -d "$DIRECTORY" ]; then
    echo "Install directory already exists, exiting"
    exit 1
fi

# Install conda
TMP_DIR=$(mktemp -d)
curl -o $TMP_DIR/Miniconda2-latest-Linux-x86_64.sh https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh
chmod +x $TMP_DIR/Miniconda2-latest-Linux-x86_64.sh
$TMP_DIR/Miniconda2-latest-Linux-x86_64.sh -b -p $CONDA_INSTALL_DIR
rm -r $TMP_DIR

# Install dependencies
$CONDA_INSTALL_DIR/bin/conda install -y gevent six
/usr/bin/yes | $CONDA_INSTALL_DIR/bin/python -m pip install leveldb
