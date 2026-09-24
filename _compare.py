import sys
import xml.etree.ElementTree as ET

paths = sys.argv[1:3]
if len(paths) < 2:
    print("usage: _compare.py current.xml baseline.xml")
    sys.exit(2)

def load(path):
    root = ET.parse(path).getroot()
    suite = root if root.tag == "testsuite" else root[0]
    total = int(suite.get("tests"))
    failures = int(suite.get("failures"))
    errors = int(suite.get("errors"))
    fail = sorted(
        f"{tc.get('classname').split('.')[-1]}::{tc.get('name')}"
        for tc in root.iter("testcase")
        if len(tc)
    )
    return total, failures, errors, fail

cur_total, cur_f, cur_e, cur_fail = load(paths[0])
base_total, base_f, base_e, base_fail = load(paths[1])

print("CURRENT  : tests=%d failures=%d errors=%d passed=%d" % (cur_total, cur_f, cur_e, cur_total - cur_f - cur_e))
print("BASE     : tests=%d failures=%d errors=%d passed=%d" % (base_total, base_f, base_e, base_total - base_f - base_e))
print("FAILING (current) count=%d" % len(cur_fail))
print("FAILING (baseline)  count=%d" % len(base_fail))
print()
print("CURRENT FAILING SET:")
for x in cur_fail:
    print("  -", x)
print("NEWLY FAILING (current - baseline):", sorted(set(cur_fail) - set(base_fail)) or "NONE")
print("RESOLVED     (baseline - current) :", sorted(set(base_fail) - set(cur_fail)) or "NONE")
print("IDENTICAL SETS:", cur_fail == base_fail)
