#!/bin/bash

PLATFORM=$(uname)
ARCH=$(uname -m)

echo "Building for platform: $PLATFORM on architecture: $ARCH"

if [[ "$PLATFORM" == "Darwin" ]]; then
    pyinstaller --onefile --windowed cannon_ball/game.py --name "CannonballGame-$ARCH"
    
    if [[ "$ARCH" == "arm64" ]]; then
        ARCHFLAGS="-arch x86_64" pyinstaller --onefile --windowed cannon_ball/game.py --name "CannonballGame-x86_64"
    else
        ARCHFLAGS="-arch arm64" pyinstaller --onefile --windowed cannon_ball/game.py --name "CannonballGame-arm64"
    fi
elif [[ "$PLATFORM" == "Linux" ]]; then
    pyinstaller --onefile --windowed cannon_ball/game.py --name "CannonballGame-linux-$ARCH"
else
    echo "Unsupported platform: $PLATFORM"
    exit 1
fi

echo "Build complete! Executables can be found in the dist/ directory"

mkdir -p builds
mv dist/* builds/
rm -rf build dist *.spec

echo "All executables have been moved to the builds/ directory"