#!/bin/bash
set -e

echo "Cleaning up previous Xvfb, VNC, and Wine processes..."
kill -9 $(pgrep -f Xvfb) 2>/dev/null || true
kill -9 $(pgrep -f x11vnc) 2>/dev/null || true
kill -9 $(pgrep -f WinMark.exe) 2>/dev/null || true
kill -9 $(pgrep -f wine) 2>/dev/null || true
rm -f /tmp/.X99-lock /tmp/.X11-unix/X99 || true

Xvfb :99 -screen 0 1280x720x24 &
sleep 1
export DISPLAY=:99

# x11vnc -display :99 -forever -nopw &

MARK_WINDOW_NAME="MarkWineGeneral"

cd /exe
wine explorer /desktop=$MARK_WINDOW_NAME,1280x720 WinMark.exe &

# 4. Wait and dynamically look for the window using a retry loop
echo "Waiting for $MARK_WINDOW_NAME window to appear..."
WID=""
for i in {1..15}; do
    WID=$(xdotool search --name "$MARK_WINDOW_NAME" 2>/dev/null | head -n 1 || true)
    if [ -n "$WID" ]; then
        break
    fi
    sleep 0.5
done

ocr_extraction() {
    local prefix="$1"
    local coords="$2"
    local total_regions=$3
    local skip_last_lines=$4

    local temp_output="/tmp/${prefix}_all_text.txt"
    > "$temp_output"

    for ((i=1; i<=total_regions; i++)); do
        local img_base="/exe/${prefix}_region_${i}"

        scrot -a "$coords" "${img_base}.png"
        convert "${img_base}.png" -crop 122x120+115+0 +repage "${img_base}_col.png"
        convert "${img_base}_col.png" -resize 300% -bordercolor white -border 20x20 -unsharp 1x1+0.5 "${img_base}_processed.png"
        
        if [ "$i" -eq "$total_regions" ] && [ "$skip_last_lines" -gt 0 ]; then
            tesseract "${img_base}_processed.png" stdout --oem 1 -l eng --psm 6 2>/dev/null | tail -n +$((skip_last_lines + 1)) >> "$temp_output"
        else
            tesseract "${img_base}_processed.png" stdout --oem 1 -l eng --psm 6 2>/dev/null >> "$temp_output"
        fi

        if [ "$i" -lt "$total_regions" ]; then
            sleep 1
            for _ in {1..5}; do
                xdotool key Down
            done
            sleep 1
        fi
    done

    cat "$temp_output"
}

run_workflow() {
    local ocr_func="$1"
    local file_x="$2"
    local file_y="$3"
    local scrot_coords="$4"
    local prefix="$5"
    local total_regions=$6
    local skip_last_lines=$7

    xdotool mousemove --window "$WID" 926 12 click 1
    sleep 0.3
    xdotool mousemove --window "$WID" 18 31 click 1
    sleep 0.3
    xdotool mousemove --window "$WID" 27 54 click 1
    sleep 0.3
    xdotool mousemove --window "$WID" "$file_x" "$file_y" click --repeat 2 --delay 50 1
    sleep 0.3
    xdotool mousemove --window "$WID" 315 59 click 1
    sleep 1

    for i in {1..6}; do
        xdotool key Down
    done

    "$ocr_func" "$prefix" "$scrot_coords" $total_regions $skip_last_lines > "/exe/${prefix}_extracted.txt"

    sleep 0.3
    xdotool mousemove --window "$WID" 769 280 click 1
}

if [ -n "$WID" ]; then
    echo "Found window ID: $WID. Maximizing and opening View menu..."
    rm -f /exe/*.png

    echo "[M1]"
    run_workflow "ocr_extraction" 470 293 "512,324,237,74" "run1" 2 1
    echo "[M2]"
    run_workflow "ocr_extraction" 470 320 "512,324,237,74" "run2" 4 2
else
    echo "Warning: Could not locate window $MARK_WINDOW_NAME. Skipping automation commands."
fi

# while true; do xdotool getmouselocation; sleep 0.5; done
# xdotool search --all "" getwindowname %@
# export DISPLAY=:99