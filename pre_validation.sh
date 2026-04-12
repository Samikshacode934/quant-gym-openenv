#!/bin/bash
# pre_validation.sh <space_url> <env_dir>

SPACE_URL=${1:-"https://astocoder-quant-gym.hf.space"}
ENV_DIR=${2:-"."}

echo "=== Pre-Submission Validation ==="
echo "Space URL: $SPACE_URL"
echo ""

# Test 1: Health endpoint
echo "1. Testing health endpoint..."
curl -s "${SPACE_URL}/health" | grep -q "healthy"
if [ $? -eq 0 ]; then
    echo "    PASSED"
else
    echo "    FAILED"
fi

# Test 2: Reset endpoint
echo "2. Testing reset endpoint..."
curl -s -X POST "${SPACE_URL}/reset" | grep -q "reset"
if [ $? -eq 0 ]; then
    echo "    PASSED"
else
    echo "    FAILED"
fi

# Test 3: Step endpoint
echo "3. Testing step endpoint..."
curl -s -X POST "${SPACE_URL}/step" -H "Content-Type: application/json" -d '{"type":"GET_PRICE"}' | grep -q "price"
if [ $? -eq 0 ]; then
    echo "    PASSED"
else
    echo "    FAILED"
fi

echo ""
echo "=== Checking openenv.yaml ==="
python3 -c "
import yaml
d = yaml.safe_load(open('$ENV_DIR/openenv.yaml'))
tasks = d.get('tasks', [])
ok = 0
for t in tasks:
    has_grader = t.get('grader') is not None
    print(f\"  {'' if has_grader else ''} {t['id']} grader={'present' if has_grader else 'missing'}\")
    if has_grader:
        ok += 1
print(f\"\nTasks with graders: {ok}/{len(tasks)}\")
print(f\"{' PASSED' if ok >= 3 else ' FAILED'}: need at least 3 tasks with graders\")
"

chmod +x pre_validation.sh