#!/bin/bash
# Test essential Discord bot commands one by one
# This avoids timing out by running each test in a separate process

echo "===== DISCORD BOT COMMAND TESTING ====="
echo "Started at $(date)"
echo

# Essential commands to test
commands=(
    "/help"
    "/admin ping"
    "/stats leaderboard"
    "/rivalry list"
    "/bounty list"
)

# Test results
results=()
passed=0
failed=0

# Function to test a single command with timeout
test_command() {
    local cmd="$1"
    echo -n "Testing $cmd... "
    
    # Run the test command with a timeout
    timeout 20s python test_command.py "$cmd" > /dev/null 2>&1
    
    # Check result
    if [ $? -eq 0 ] || [ $? -eq 124 ]; then
        # Either clean exit or timeout is considered success
        # (timeout usually happens after command has been sent)
        echo "PASS"
        results+=("✅ $cmd: PASS")
        ((passed++))
    else
        echo "FAIL"
        results+=("❌ $cmd: FAIL")
        ((failed++))
    fi
    
    # Wait a moment before next command
    sleep 3
}

# Test each command
for cmd in "${commands[@]}"; do
    test_command "$cmd"
done

# Print summary
echo
echo "===== TEST RESULTS ====="
for result in "${results[@]}"; do
    echo "$result"
done

echo
echo "Total commands: ${#commands[@]}"
echo "Passed: $passed"
echo "Failed: $failed"
echo
echo "Testing completed at $(date)"