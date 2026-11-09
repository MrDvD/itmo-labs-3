cd .devcontainer/quartus
podman build -f Containerfile -t quartus .
podman run --rm -it \
    --env="DISPLAY=$DISPLAY" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --volume="../../build:/build" \
    --device=/dev/dri:/dev/dri \
    quartus