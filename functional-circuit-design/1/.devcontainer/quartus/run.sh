set -e

cd .devcontainer/quartus

if [ "${1:-}" = "build" ]; then
    echo "Building Quartus container..."
    podman build -f Containerfile -t quartus .
fi

podman run --rm -it \
    --net=host \
    --env="DISPLAY=$DISPLAY" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --volume="../../build:/build" \
    --device=/dev/dri:/dev/dri \
    --security-opt seccomp=unconfined \
    quartus