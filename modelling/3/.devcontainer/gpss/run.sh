set -e

cd .devcontainer/gpss

if [ "${1:-}" = "build" ]; then
    echo "Building GPSS container..."
    podman build -f Containerfile -t gpss_world .
fi

podman run --rm -it \
    --net=host \
    --env="DISPLAY=$DISPLAY" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --volume="../../build:/build" \
    --device=/dev/dri:/dev/dri \
    gpss_world