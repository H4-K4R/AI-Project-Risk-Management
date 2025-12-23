"""
COMPREHENSIVE RESOURCE OPTIMIZER TEST
Tests determinism, constraints, and actual improvement
"""

import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Scripts.resource_optimizer import optimize_resources

print("="*70)
print("🧪 RESOURCE OPTIMIZER TEST SUITE")
print("="*70)

# Load data from parent directory
df = pd.read_csv('../dummy_data.csv')

print("\n📊 BASELINE DATA:")
print("="*70)
print(f"Total Tasks: {len(df)}")
print(f"Total Resources: {df['Resource_Name'].nunique()}")
print(f"Current Allocation:")
for resource in df['Resource_Name'].unique():
    resource_tasks = df[df['Resource_Name'] == resource]
    print(f"  {resource}: {len(resource_tasks)} tasks, {resource_tasks['Duration_Days'].sum()} days")

print(f"\nBaseline Duration (sum of all tasks): {df['Duration_Days'].sum()} days")
print(f"Baseline Max Resource Workload: {df.groupby('Resource_Name')['Duration_Days'].sum().max()} days")

# ============================================================
# TEST 1: Determinism (Run 5 Times)
# ============================================================
print("\n" + "="*70)
print("TEST 1: DETERMINISM CHECK (LP Should Be Deterministic)")
print("="*70)
print("Running optimization 5 times on same data...\n")

results_list = []
for i in range(5):
    result = optimize_resources(df)
    results_list.append(result)
    print(f"Run {i+1}: Duration = {result['optimized_duration']:.1f} days, "
          f"Improvement = {result['improvement_percentage']:.1f}%, "
          f"Status = {result['status']}")

# Check if all results are identical
all_durations = [r['optimized_duration'] for r in results_list]
all_improvements = [r['improvement_percentage'] for r in results_list]

if len(set(all_durations)) == 1:
    print("\n✅ PASS: All 5 runs produced identical results (deterministic)")
else:
    print("\n❌ FAIL: Results vary across runs (non-deterministic)")
    print(f"   Durations: {all_durations}")

# ============================================================
# TEST 2: What Is Being Optimized?
# ============================================================
print("\n" + "="*70)
print("TEST 2: WHAT IS THE OPTIMIZER ACTUALLY DOING?")
print("="*70)

result = results_list[0]  # Use first run

print("\n📋 OPTIMIZATION PROBLEM DEFINITION:")
print("-" * 70)
print("Objective Function:")
print("  Minimize: Project makespan (longest resource workload)")
print("\nDecision Variables:")
print("  x[task, resource] = 1 if task assigned to resource, 0 otherwise")
print("\nConstraints:")
print("  1. Each task assigned to exactly ONE resource")
print("  2. Each resource gets ≤ max_tasks_per_resource")
print(f"     (max = {len(df) // df['Resource_Name'].nunique() + 2} tasks per resource)")

# ============================================================
# TEST 3: Constraint Verification
# ============================================================
print("\n" + "="*70)
print("TEST 3: CONSTRAINT VERIFICATION")
print("="*70)

allocation = result['optimized_allocation']

# Check Constraint 1: Each task appears exactly once
task_count = {}
for item in allocation:
    task_id = item['task_id']
    task_count[task_id] = task_count.get(task_id, 0) + 1

constraint1_pass = all(count == 1 for count in task_count.values())
print(f"\nConstraint 1 (Each task assigned once):")
if constraint1_pass:
    print(f"  ✅ PASS: All {len(task_count)} tasks assigned exactly once")
else:
    print(f"  ❌ FAIL: Some tasks assigned multiple times or not at all")
    for task, count in task_count.items():
        if count != 1:
            print(f"     Task {task}: {count} assignments")

# Check Constraint 2: Resource capacity
resource_workload = {}
for item in allocation:
    r = item['resource']
    resource_workload[r] = resource_workload.get(r, 0) + 1

max_allowed = len(df) // df['Resource_Name'].nunique() + 2
constraint2_pass = all(count <= max_allowed for count in resource_workload.values())

print(f"\nConstraint 2 (Resource capacity ≤ {max_allowed} tasks):")
if constraint2_pass:
    print(f"  ✅ PASS: All resources within capacity")
else:
    print(f"  ❌ FAIL: Some resources exceed capacity")
    
for resource, count in sorted(resource_workload.items()):
    status = "✅" if count <= max_allowed else "❌"
    print(f"  {status} {resource}: {count} tasks (max {max_allowed})")

# ============================================================
# TEST 4: Is It Actually Better?
# ============================================================
print("\n" + "="*70)
print("TEST 4: DOES OPTIMIZATION ACTUALLY IMPROVE?")
print("="*70)

baseline_duration = result['baseline_duration']
optimized_duration = result['optimized_duration']
improvement = result['improvement_percentage']

print(f"\nBASELINE (Original Allocation):")
print(f"  Method: Sum of all task durations (sequential)")
print(f"  Duration: {baseline_duration} days")
print(f"  Problem: Assumes no parallel execution")

print(f"\nOPTIMIZED (LP Solution):")
print(f"  Method: Max workload across resources (parallel)")
print(f"  Duration: {optimized_duration:.1f} days")
print(f"  Calculation: Max resource workload = critical path")

print(f"\nIMPROVEMENT:")
print(f"  Reduction: {baseline_duration - optimized_duration:.1f} days")
print(f"  Percentage: {improvement:.1f}%")

if improvement >= 10:
    print(f"  ✅ Meets 10% target")
elif improvement > 0:
    print(f"  ⚠️  Below 10% target but still improved")
else:
    print(f"  ❌ No improvement or got worse")

# ============================================================
# TEST 5: Detailed Workload Analysis
# ============================================================
print("\n" + "="*70)
print("TEST 5: WORKLOAD DISTRIBUTION ANALYSIS")
print("="*70)

print("\nORIGINAL ALLOCATION:")
original_workload = df.groupby('Resource_Name')['Duration_Days'].sum().sort_values(ascending=False)
for resource, days in original_workload.items():
    print(f"  {resource}: {days} days")
print(f"  Longest workload (critical path): {original_workload.max()} days")
print(f"  Shortest workload: {original_workload.min()} days")
print(f"  Imbalance: {original_workload.max() - original_workload.min()} days")

print("\nOPTIMIZED ALLOCATION:")
optimized_workload = {}
for item in allocation:
    r = item['resource']
    optimized_workload[r] = optimized_workload.get(r, 0) + item['duration']

for resource, days in sorted(optimized_workload.items(), key=lambda x: x[1], reverse=True):
    print(f"  {resource}: {days} days")
print(f"  Longest workload (critical path): {max(optimized_workload.values())} days")
print(f"  Shortest workload: {min(optimized_workload.values())} days")
print(f"  Imbalance: {max(optimized_workload.values()) - min(optimized_workload.values())} days")

# ============================================================
# FINAL VERDICT
# ============================================================
print("\n" + "="*70)
print("🎯 FINAL VERDICT")
print("="*70)

all_pass = constraint1_pass and constraint2_pass and len(set(all_durations)) == 1

if all_pass:
    print("✅ OPTIMIZER WORKS CORRECTLY:")
    print("   • Deterministic (same results every run)")
    print("   • Constraints respected")
    print("   • Valid optimization problem")
else:
    print("⚠️  ISSUES DETECTED:")
    if len(set(all_durations)) != 1:
        print("   ❌ Non-deterministic results")
    if not constraint1_pass:
        print("   ❌ Task assignment constraint violated")
    if not constraint2_pass:
        print("   ❌ Resource capacity constraint violated")

print("\n🤔 CRITICAL ANALYSIS:")
print("="*70)
print("What the optimizer ACTUALLY does:")
print("  1. Takes current task assignments")
print("  2. Reassigns tasks to balance workload across resources")
print("  3. Minimizes the longest resource workload (critical path)")
print("\nWhat it DOESN'T do:")
print("  ❌ Change task durations")
print("  ❌ Optimize task sequencing")
print("  ❌ Handle dependencies intelligently")
print("  ❌ Consider skill levels or efficiency")
print("\nWhy improvement is so large:")
print(f"  • Baseline ({baseline_duration}d) = Sum of ALL task durations")
print(f"  • This assumes 100% sequential execution (unrealistic)")
print(f"  • Optimized ({optimized_duration:.1f}d) = Longest resource workload")
print(f"  • This assumes 100% parallel execution (more realistic)")
print("\n💡 The 'improvement' is mostly from fixing the baseline calculation,")
print("   not from actual optimization. The LP solver is balancing workload.")
print("="*70)
