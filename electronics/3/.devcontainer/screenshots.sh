#!/bin/bash
set -e

echo "Cleaning up previous Xvfb, VNC, and Wine processes..."
for pat in Xvfb x11vnc LTspice.exe openbox wine wineserver explorer.exe; do
    pkill -9 -f "$pat" 2>/dev/null || true
done
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null || true

Xvfb :99 -screen 0 1280x720x24 &
sleep 1
export DISPLAY=:99

openbox &
sleep 0.5

x11vnc -display :99 -forever -nopw &

LTSPICE_WINDOW_NAME="GenLtSp"
LTSPICE_EXE_PATH="/root/.wine/drive_c/Program Files/ADI/LTspice/LTspice.exe"

wine explorer /desktop=$LTSPICE_WINDOW_NAME,1280x720 "$LTSPICE_EXE_PATH" 2>/dev/null &

echo "Waiting for $LTSPICE_WINDOW_NAME window to appear..."
WID=""
for i in {1..15}; do
    WID=$(xdotool search --name "$LTSPICE_WINDOW_NAME" 2>/dev/null | head -n 1 || true)
    if [ -n "$WID" ]; then
        break
    fi
    sleep 0.5
done

wait_for() {
    local timeout=10
    local interval=0.2
    local start=$(date +%s.%N)
    while ! "$@"; do
        now=$(date +%s.%N)
        if (( $(echo "$now - $start > $timeout" | bc -l) )); then
            echo "Timeout waiting for: $*" >&2
            return 1
        fi
        sleep "$interval"
    done
}

capture_schema() {
    local img_name="$1"
    local item_x="$2"
    local item_y="$3"

    # open the "Open" dialog and select a schema file
    xdotool key ctrl+o
    echo "Waiting for existing files window..."
    wait_for xdotool search --sync --onlyvisible --name '^Open an'
    echo "Done waiting!"
    xdotool mousemove --window "$WID" 371 258 click 1
    sleep 0.3
    xdotool mousemove --window "$WID" 505 447 click --repeat 2 --delay 50 1
    sleep 0.3
    # # select a schema to open from the list
    xdotool mousemove --window "$WID" "$item_x" "$item_y" click --repeat 2 --delay 50 1
    sleep 0.3
    scrot -a "8,122,1265,564" "$img_name"

    echo "$(pwd)/$img_name" >> /schemas/schemas.txt
}

if [ -n "$WID" ]; then
    echo "Found window ID: $WID. Performing automation commands..."

    cd /schemas
    rm -f *.png *.txt

    echo "Waiting for LTspice window to appear..."
    LTWID=$(xdotool search --sync --onlyvisible --name '^LTspice' 2>/dev/null)
    echo "Found LTspice window ID: $LTWID"
    echo "Done waiting!"

    xdotool windowmove "$LTWID" 0 0
    xdotool windowsize "$LTWID" 1280 720

    for i in {1..20}; do
        eval "$(xdotool getwindowgeometry --shell "$LTWID")"
        [ "$WIDTH" -eq 1280 ] && [ "$HEIGHT" -eq 720 ] && break
        sleep 0.05
    done

    # create a new schematic
    xdotool mousemove --window "$WID" 25 35 click 1
    sleep 0.1
    xdotool mousemove --window "$WID" 81 60 click 1
    sleep 0.1

    capture_schema "schema1.png" 513 193
    capture_schema "schema2.png" 513 212
    capture_schema "schema3.png" 513 224
else
    echo "Error: Could not locate window $LTSPICE_WINDOW_NAME."
fi

# sleep 10
# echo "Cleaning up previous Xvfb, VNC, and Wine processes..."
# for pat in Xvfb x11vnc LTspice.exe openbox wine wineserver explorer.exe; do
#     pkill -9 -f "$pat" 2>/dev/null || true
# done
# rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 2>/dev/null || true

# while true; do xdotool getmouselocation; sleep 0.5; done
# xdotool search --all "" getwindowname %@
# export DISPLAY=:99