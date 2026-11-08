# https://hub.docker.com/r/raetro/quartus?tag=21.1.1

if [ "$(podman image ls | grep raetro/quartus)" -n ]; then
    podman pull https://hub.docker.com/r/raetro/quartus?tag=21.1.1
fi

xhost +local:

podman run -it --rm \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  -v ./build:/build \
  raetro/quartus:21.1.1 \
  quartus