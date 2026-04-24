import streamlit as st
import subprocess, sys, tempfile, os
import streamlit.components.v1 as components

st.set_page_config(page_title="AntiGravity IDE", layout="wide", page_icon="⚡")

# ─── BUILT-IN LESSON CONTENT ────────────────────────────────────────────────
LESSONS = {
    "Hash Maps (Two Sum)": {
        "topic": "Arrays",
        "content": """
## 🗂️ Hash Maps in Python

A **dictionary** (hash map) lets you store and look up values in **O(1)** time.

```python
# Basic usage
seen = {}
seen[2] = 0      # store value → index
print(seen[2])   # → 0
```

### Why use it for Two Sum?
Instead of checking every pair (O(n²)), store each number you've seen.
For each new number, check if `target - number` is already stored.

```python
def two_sum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return [seen[complement], i]
        seen[n] = i
```

### Key Operations
| Operation | Syntax | Time |
|-----------|--------|------|
| Insert | `d[key] = val` | O(1) |
| Lookup | `key in d` | O(1) |
| Get | `d[key]` | O(1) |
""",
        "visual_url": None,
    },
    "Two Pointers (Reverse String)": {
        "topic": "Arrays",
        "content": """
## 👉👈 Two Pointer Technique

Use two pointers starting from opposite ends, moving inward.

```
["h", "e", "l", "l", "o"]
  ↑                   ↑
 left               right
```

Swap `left` and `right`, then move them toward the center.

```python
def reverse_string(s):
    left, right = 0, len(s) - 1
    while left < right:
        s[left], s[right] = s[right], s[left]
        left += 1
        right -= 1
```

### Trace through example:
```
Step 1: swap h ↔ o  → ["o","e","l","l","h"]
Step 2: swap e ↔ l  → ["o","l","l","e","h"]
Step 3: left >= right, stop ✅
```
""",
        "visual_url": None,
    },
    "Stack — Valid Parentheses": {
        "topic": "Stacks",
        "content": """
## 📚 Stack Data Structure

A stack is **Last In, First Out (LIFO)** — like a pile of plates.

```python
stack = []
stack.append("(")   # push
stack.pop()         # pop → "("
```

### Algorithm for Valid Parentheses

1. Loop through each character
2. If it's an **opening** bracket → push to stack
3. If it's a **closing** bracket → pop and check if it matches
4. At the end, stack must be empty

```python
def is_valid(s):
    stack = []
    pairs = {")": "(", "}": "{", "]": "["}
    for c in s:
        if c in "([{":
            stack.append(c)
        elif not stack or stack[-1] != pairs[c]:
            return False
        else:
            stack.pop()
    return len(stack) == 0
```

### Trace: `"()[]{}"` → True ✅
### Trace: `"(]"` → False ❌
""",
        "visual_url": None,
    },
    "Binary Search": {
        "topic": "Searching",
        "content": """
## 🔍 Binary Search

Works on **sorted arrays**. Halves the search space each step → **O(log n)**.

```
[-1, 0, 3, 5, 9, 12]   target = 9
  lo           hi
       mid = 2  → nums[2]=3 < 9, move lo right
              lo  hi
           mid=4 → nums[4]=9 == target ✅ return 4
```

```python
def search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            lo = mid + 1    # search right half
        else:
            hi = mid - 1    # search left half
    return -1
```

### Complexity
| | Value |
|--|--|
| Time | O(log n) |
| Space | O(1) |
""",
        "visual_url": None,
    },
    "Kadane's Algorithm": {
        "topic": "DP",
        "content": """
## 📈 Kadane's Algorithm (Max Subarray)

At every element, decide: **extend** the current subarray or **start fresh**?

```python
curr = max(nums[i],  curr + nums[i])
#          start       extend
```

Track the global maximum as you go.

```python
def max_subarray(nums):
    max_sum = curr = nums[0]
    for n in nums[1:]:
        curr = max(n, curr + n)
        max_sum = max(max_sum, curr)
    return max_sum
```

### Trace: `[-2, 1, -3, 4, -1, 2, 1, -5, 4]`
```
n=-2: curr=-2, max=-2
n= 1: curr= 1, max= 1   ← start fresh (1 > -2+1)
n=-3: curr=-2, max= 1
n= 4: curr= 4, max= 4   ← start fresh
n=-1: curr= 3, max= 4
n= 2: curr= 5, max= 5
n= 1: curr= 6, max= 6 ✅
n=-5: curr= 1, max= 6
n= 4: curr= 5, max= 6
```
**Answer: 6**
""",
        "visual_url": None,
    },
    "Sorting — Visualgo": {
        "topic": "Sorting",
        "content": None,
        "visual_url": "https://visualgo.net/en/sorting",
    },
    "Linked List — Visualgo": {
        "topic": "Linked Lists",
        "content": None,
        "visual_url": "https://visualgo.net/en/list",
    },
    "BST — Visualgo": {
        "topic": "Trees",
        "content": None,
        "visual_url": "https://visualgo.net/en/bst",
    },
    "Two Sum — YouTube": {
        "topic": "Arrays",
        "content": None,
        "visual_url": "youtube:https://www.youtube.com/watch?v=KLlXCFG5TnA",
    },
    "Binary Search — YouTube": {
        "topic": "Searching",
        "content": None,
        "visual_url": "youtube:https://www.youtube.com/watch?v=6ysjqCUv3K4",
    },
    "Kadane's — YouTube": {
        "topic": "DP",
        "content": None,
        "visual_url": "youtube:https://www.youtube.com/watch?v=86CQq3pKSUw",
    },
}

# ─── PROBLEMS ───────────────────────────────────────────────────────────────
PROBLEMS = [
    {
        "title": "1. Two Sum", "difficulty": "Easy",
        "description": "Given an array of integers and a target, return indices of the two numbers that add up to the target.",
        "input_display": "[2, 7, 11, 15], target = 9", "expected": "[0, 1]",
        "test_code": """
result = two_sum([2, 7, 11, 15], 9)
print(result)
assert sorted(result) == [0, 1], f"Expected [0,1], got {result}"
print("ALL TESTS PASSED")
""",
        "starter": "def two_sum(nums, target):\n    # Write your solution here\n    pass\n",
        "hints": ["Use a hash map to store visited numbers.", "For each element, check if (target - element) is already in the map."],
        "suggested": "Hash Maps (Two Sum)",
    },
    {
        "title": "2. Reverse a String", "difficulty": "Easy",
        "description": "Reverse a string given as a list of characters, in-place.",
        "input_display": '["h","e","l","l","o"]', "expected": '["o","l","l","e","h"]',
        "test_code": """
s = ["h","e","l","l","o"]
reverse_string(s)
print(s)
assert s == ["o","l","l","e","h"], f"Got {s}"
print("ALL TESTS PASSED")
""",
        "starter": "def reverse_string(s):\n    # Modify s in-place using two pointers\n    pass\n",
        "hints": ["Use two pointers from both ends.", "Swap elements while left < right."],
        "suggested": "Two Pointers (Reverse String)",
    },
    {
        "title": "3. Valid Parentheses", "difficulty": "Easy",
        "description": "Given a string with '(', ')', '{', '}', '[', ']', determine if it is valid.",
        "input_display": '"()[]{}"', "expected": "True",
        "test_code": """
print(is_valid("()[]{}"))
assert is_valid("()[]{}") == True
assert is_valid("(]") == False
assert is_valid("{[]}") == True
print("ALL TESTS PASSED")
""",
        "starter": "def is_valid(s):\n    # Use a stack\n    pass\n",
        "hints": ["Use a stack data structure.", "Push opening brackets, pop and match for closing ones."],
        "suggested": "Stack — Valid Parentheses",
    },
    {
        "title": "4. Binary Search", "difficulty": "Easy",
        "description": "Given a sorted array and a target, return its index using binary search, or -1.",
        "input_display": "[-1, 0, 3, 5, 9, 12], target = 9", "expected": "4",
        "test_code": """
print(search([-1,0,3,5,9,12], 9))
assert search([-1,0,3,5,9,12], 9) == 4
assert search([-1,0,3,5,9,12], 2) == -1
print("ALL TESTS PASSED")
""",
        "starter": "def search(nums, target):\n    # Use lo and hi pointers\n    pass\n",
        "hints": ["Use two pointers lo and hi.", "Compute mid = (lo+hi)//2 and halve the search space."],
        "suggested": "Binary Search",
    },
    {
        "title": "5. Maximum Subarray", "difficulty": "Medium",
        "description": "Find the contiguous subarray with the largest sum (Kadane's Algorithm).",
        "input_display": "[-2, 1, -3, 4, -1, 2, 1, -5, 4]", "expected": "6",
        "test_code": """
print(max_subarray([-2,1,-3,4,-1,2,1,-5,4]))
assert max_subarray([-2,1,-3,4,-1,2,1,-5,4]) == 6
assert max_subarray([1]) == 1
print("ALL TESTS PASSED")
""",
        "starter": "def max_subarray(nums):\n    # Kadane's algorithm\n    pass\n",
        "hints": ["At each step: extend current subarray or start fresh.", "Track global max alongside current sum."],
        "suggested": "Kadane's Algorithm",
    },
]

# ─── CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0.5rem 1.5rem 2rem !important; max-width: 100% !important; }

.ag-topbar { background:#fff; border-bottom:2px solid #e5e7eb; padding:13px 0 11px; margin-bottom:16px; display:flex; align-items:center; }
.ag-logo { font-family:'Syne',sans-serif; font-weight:800; font-size:21px; color:#111827; display:flex; align-items:center; gap:8px; }
.ag-dot { width:10px;height:10px;border-radius:50%;background:#2563eb;display:inline-block;animation:pulse 2s infinite; }
@keyframes pulse{0%,100%{opacity:1}50%{opacity:0.35}}

.sec-title { font-family:'Syne',sans-serif; font-weight:700; font-size:11px; text-transform:uppercase; letter-spacing:0.1em; color:#9ca3af; margin-bottom:10px; }

.rc-card { background:#fff; border:1.5px solid #e5e7eb; border-radius:10px; padding:10px 13px; margin-bottom:6px; cursor:pointer; }
.rc-card:hover { border-color:#93c5fd; }
.rc-card.active { border-color:#2563eb; background:#eff6ff; }
.rc-title { font-size:13px; font-weight:500; color:#111827; }
.rc-topic { font-size:11px; color:#9ca3af; margin-top:2px; }

.badge { display:inline-block; font-size:10px; font-weight:500; padding:2px 8px; border-radius:100px; margin-right:4px; }
.b-lesson { background:#e0e7ff; color:#3730a3; }
.b-visual { background:#ede9fe; color:#5b21b6; }
.b-video  { background:#fee2e2; color:#dc2626; }
.b-easy   { background:#dbeafe; color:#1d4ed8; }
.b-medium { background:#fef3c7; color:#b45309; }
.b-hard   { background:#fee2e2; color:#dc2626; }

.io-label { font-size:11px; font-weight:500; color:#9ca3af; margin-bottom:3px; }
.io-box { background:#f9fafb; border:1px solid #e5e7eb; border-radius:7px; padding:8px 12px; font-family:'JetBrains Mono',monospace; font-size:12px; color:#374151; }

.out-pass { background:#d1fae5;border:1px solid #6ee7b7;border-radius:8px;padding:12px 16px;color:#065f46;font-family:'JetBrains Mono',monospace;font-size:13px;white-space:pre-wrap; }
.out-fail { background:#fee2e2;border:1px solid #fca5a5;border-radius:8px;padding:12px 16px;color:#dc2626;font-family:'JetBrains Mono',monospace;font-size:13px;white-space:pre-wrap; }
.hint-box { background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:11px 15px;color:#1e40af;font-size:13px; }
.suggest-box { background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:8px 13px;font-size:12px;color:#166534;margin-bottom:10px; }
.divider { border:none;border-top:1px solid #f3f4f6;margin:12px 0; }

.lesson-box { background:#fff; border:1.5px solid #e5e7eb; border-radius:12px; padding:20px 22px; margin-top:8px; }

textarea {
    font-family:'JetBrains Mono',monospace !important; font-size:13px !important;
    background:#1a1a2e !important; color:#e2e8f0 !important;
    border-radius:8px !important; border:1.5px solid #334155 !important; line-height:1.7 !important;
}
textarea:focus { border-color:#3b82f6 !important; box-shadow:0 0 0 2px rgba(59,130,246,0.2) !important; }
</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE ───────────────────────────────────────────────────────────
for k, v in [("active_lesson", None), ("output", None), ("out_type", ""), ("hint_idx", 0), ("prob_idx", 0)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─── TOPBAR ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="ag-topbar">
  <div class="ag-logo"><span class="ag-dot"></span> AntiGravity <span style="font-weight:300;color:#9ca3af;margin-left:4px;">IDE</span></div>
  <span style="flex:1"></span>
  <span style="font-size:13px;color:#9ca3af;">Learn &amp; Code — Side by Side ⚡</span>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([1, 1.6], gap="large")

# ══════════════════════════════════════════════
# LEFT — LEARN PANEL
# ══════════════════════════════════════════════
with left:
    st.markdown('<div class="sec-title">📚 Resources</div>', unsafe_allow_html=True)

    all_topics = ["All"] + sorted(set(v["topic"] for v in LESSONS.values()))
    topic = st.selectbox("Topic", all_topics, label_visibility="collapsed")
    search = st.text_input("Search", placeholder="🔍  Search lessons...", label_visibility="collapsed")

    filtered_lessons = {
        name: data for name, data in LESSONS.items()
        if (topic == "All" or data["topic"] == topic)
        and (not search or search.lower() in name.lower() or search.lower() in data["topic"].lower())
    }

    def get_badge(data):
        if data["content"]:       return "b-lesson", "📖 Lesson"
        if data["visual_url"] and data["visual_url"].startswith("youtube"): return "b-video", "▶ YouTube"
        return "b-visual", "◉ Visual"

    for name, data in filtered_lessons.items():
        is_active = st.session_state.active_lesson == name
        bcls, blabel = get_badge(data)
        card_cls = "rc-card active" if is_active else "rc-card"
        st.markdown(f"""
        <div class="{card_cls}">
            <span class="badge {bcls}">{blabel}</span>
            <div class="rc-title">{name}</div>
            <div class="rc-topic">{data['topic']}</div>
        </div>
        """, unsafe_allow_html=True)
        btn_label = "✓ Viewing" if is_active else "Open →"
        if st.button(btn_label, key=f"btn_{name}", use_container_width=True):
            st.session_state.active_lesson = None if is_active else name
            st.rerun()

    # ── Render lesson ──
    if st.session_state.active_lesson:
        lesson = LESSONS[st.session_state.active_lesson]
        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        if lesson["content"]:
            # Built-in markdown lesson
            st.markdown(f'<div class="lesson-box">', unsafe_allow_html=True)
            st.markdown(lesson["content"])
            st.markdown('</div>', unsafe_allow_html=True)

        elif lesson["visual_url"]:
            url = lesson["visual_url"]
            if url.startswith("youtube:"):
                st.video(url.replace("youtube:", ""))
            else:
                components.iframe(url, height=500, scrolling=True)

        if st.button("✕ Close", key="close_lesson"):
            st.session_state.active_lesson = None
            st.rerun()

# ══════════════════════════════════════════════
# RIGHT — CODE PANEL
# ══════════════════════════════════════════════
with right:
    st.markdown('<div class="sec-title">💻 Code Editor</div>', unsafe_allow_html=True)

    prob_idx = st.selectbox(
        "Problem", range(len(PROBLEMS)),
        format_func=lambda i: PROBLEMS[i]["title"],
        label_visibility="collapsed"
    )

    if prob_idx != st.session_state.prob_idx:
        st.session_state.prob_idx = prob_idx
        st.session_state.output = None
        st.session_state.hint_idx = 0

    p = PROBLEMS[prob_idx]

    st.markdown(f"""
    <div class="suggest-box">
        📗 <b>Suggested lesson:</b> {p['suggested']} — click it in the left panel to read it inline.
    </div>
    """, unsafe_allow_html=True)

    diff_cls = {"Easy": "b-easy", "Medium": "b-medium", "Hard": "b-hard"}[p["difficulty"]]
    st.markdown(f'<span class="badge {diff_cls}">{p["difficulty"]}</span>', unsafe_allow_html=True)
    st.markdown(f'<p style="font-size:14px;color:#374151;margin:6px 0 12px;line-height:1.6">{p["description"]}</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="io-label">Input</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="io-box">{p["input_display"]}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="io-label">Expected Output</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="io-box">{p["expected"]}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    code = st.text_area(
        "Your Code:", value=p["starter"],
        height=280, key=f"code_{prob_idx}",
        label_visibility="visible"
    )

    b1, b2, b3 = st.columns(3)
    run   = b1.button("▶  Run Code", type="primary", use_container_width=True)
    hint  = b2.button("💡  Hint", use_container_width=True)
    reset = b3.button("↺  Reset", use_container_width=True)

    if reset:
        st.session_state.output = None
        st.session_state.hint_idx = 0
        st.rerun()

    if hint:
        hints = p["hints"]
        idx = st.session_state.hint_idx % len(hints)
        st.markdown(f'<div class="hint-box">💡 <b>Hint {idx+1}/{len(hints)}:</b> {hints[idx]}</div>', unsafe_allow_html=True)
        st.session_state.hint_idx += 1

    if run:
        if not code.strip() or code.strip() == p["starter"].strip():
            st.session_state.output = "⚠️  Write your solution first!"
            st.session_state.out_type = "fail"
        else:
            full = code + "\n" + p["test_code"]
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                    f.write(full); tmp = f.name
                res = subprocess.run([sys.executable, tmp], capture_output=True, text=True, timeout=5)
                os.unlink(tmp)
                if res.returncode == 0:
                    st.session_state.output = res.stdout.strip()
                    st.session_state.out_type = "pass"
                else:
                    st.session_state.output = (res.stderr or res.stdout).strip()
                    st.session_state.out_type = "fail"
            except subprocess.TimeoutExpired:


                
                st.session_state.output = "⏱  Time Limit Exceeded — check for infinite loops."
                st.session_state.out_type = "fail"
            except Exception as e:
                st.session_state.output = str(e)
                st.session_state.out_type = "fail"

    if st.session_state.output:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        cls = "out-pass" if st.session_state.out_type == "pass" else "out-fail"
        icon = "✅" if st.session_state.out_type == "pass" else "❌"
        st.markdown(f'<div class="{cls}">{icon}  {st.session_state.output}</div>', unsafe_allow_html=True)