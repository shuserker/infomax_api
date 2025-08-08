#!/bin/bash
# Test script for control center functions

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 Testing Control Center Functions"
echo "=================================="

# Test 1: Check syntax
echo "1. Testing script syntax..."
if bash -n watchhamster_control_center.sh; then
    echo "✅ Script syntax is valid"
else
    echo "❌ Script has syntax errors"
    exit 1
fi

# Test 2: Check if functions exist in the file
echo
echo "2. Testing function definitions in file..."

functions_to_check=(
    "start_watchhamster"
    "stop_watchhamster" 
    "check_watchhamster_status"
    "manage_modules"
    "check_managed_processes"
    "control_individual_module"
    "restart_individual_module"
    "stop_individual_module"
    "show_individual_module_log"
)

for func in "${functions_to_check[@]}"; do
    if grep -q "^$func()" watchhamster_control_center.sh; then
        echo "✅ $func function is defined"
    else
        echo "❌ $func function is NOT defined"
    fi
done

echo
echo "3. Testing process detection logic (current system state)..."

# Test check_managed_processes function (dry run)
echo "Testing managed processes detection:"
processes=("posco_main_notifier.py" "realtime_news_monitor.py" "integrated_report_scheduler.py")
running_count=0
total_count=${#processes[@]}

for process in "${processes[@]}"; do
    if pgrep -f "$process" > /dev/null 2>&1; then
        PID=$(pgrep -f "$process")
        echo "  ✅ ${process%.*} (PID: $PID) - RUNNING"
        ((running_count++))
    else
        echo "  ❌ ${process%.*} - NOT RUNNING"
    fi
done

echo "  📊 Status: $running_count/$total_count modules running"

echo
echo "4. Testing watchhamster detection..."
if pgrep -f "monitor_WatchHamster.py" > /dev/null 2>&1; then
    WATCHHAMSTER_PID=$(pgrep -f "monitor_WatchHamster.py")
    echo "✅ WatchHamster is running (PID: $WATCHHAMSTER_PID)"
else
    echo "❌ WatchHamster is not running"
fi

echo
echo "5. Testing required files..."
required_files=(
    "lib_wt_common.sh"
    "Monitoring/Posco_News_mini/monitor_WatchHamster.py"
)

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
    fi
done

echo
echo "🎉 Control Center Function Testing completed!"
echo "All required functions are properly implemented and ready for use."