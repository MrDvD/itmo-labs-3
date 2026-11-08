podman run --rm -it \
    --env="DISPLAY=$DISPLAY" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix" \
    --device=/dev/dri:/dev/dri \
    --volume="./:/winehq" \
    test