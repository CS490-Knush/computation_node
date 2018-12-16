if [ "$1" != "" ]; then
    SHOW="tc qdisc show dev $(hostname)-eth0"
    echo "Original tc bandwidth limit..."
    ${SHOW}

    echo "Setting new bandwidth limit..."
    CMD="tc qdisc change dev $(hostname)-eth0 root tbf rate $1Kbit burst 15000b lat 2ms"
    echo "Running: ${CMD}"
    ${CMD}

    echo "New bandwidth limit..."
    ${SHOW}
else
    echo "New bandwidth is required"
fi
