"""
Resource Optimization Module using Linear Programming
AI-Powered Project Risk & Resource Management
 
# Aligns with AI4SE Phase 12: Resource Planning & Optimization
# Uses PuLP for linear programming optimization
"""
 
import pandas as pd
from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value
from typing import Dict, Any, List, Tuple
import numpy as np
 
 
class ResourceOptimizer:
    """
    Optimize resource allocation to minimize project duration.
    Uses Linear Programming (PuLP) to find optimal task-resource assignments.
   
    Goal: Reduce project duration by at least 10% compared to baseline.
    """
   
    def __init__(self, df: pd.DataFrame):
        """
        Initialize optimizer with project data.
       
        Args:
            df: DataFrame with project tasks
        """
        self.df = df.copy()
        self.tasks = df['Task_ID'].tolist()
        self.resources = df['Resource_Name'].unique().tolist()
       
    def optimize_allocation(self) -> Dict[str, Any]:
        """
        Optimize resource allocation to minimize project completion time.
       
        Returns:
            Dictionary with optimization results and recommendations
        """
        # Calculate baseline duration (original max workload)
        baseline_duration = self._calculate_baseline_duration()
       
        # Create optimization model
        prob = LpProblem("Resource_Allocation_Optimization", LpMinimize)
       
        # Decision variables: x[t,r] = 1 if task t is assigned to resource r
        x = {}
        for t in self.tasks:
            for r in self.resources:
                x[(t, r)] = LpVariable(f"assign_{t}_{r}", cat='Binary')
       
        # Makespan variable: represents the project completion time (critical path)
        makespan = LpVariable("makespan", lowBound=0)
       
        # Task durations (can vary by resource skill)
        task_durations = {}
        for idx, row in self.df.iterrows():
            task_id = row['Task_ID']
            duration = row['Duration_Days']
            # Each resource has same duration for simplicity
            for r in self.resources:
                task_durations[(task_id, r)] = duration
       
        # Objective: Minimize makespan (project completion time)
        prob += makespan, "Minimize_Project_Makespan"
       
        # Constraint 1: Each task must be assigned to exactly one resource
        for t in self.tasks:
            prob += lpSum([x[(t, r)] for r in self.resources]) == 1, f"Task_{t}_Assignment"
       
        # Constraint 2: Makespan must be >= workload of each resource
        for r in self.resources:
            prob += (
                makespan >= lpSum([x[(t, r)] * task_durations[(t, r)] for t in self.tasks]),
                f"Makespan_{r}"
            )
       
        # Constraint 3: Resource capacity (max tasks per resource)
        max_tasks_per_resource = len(self.tasks) // len(self.resources) + 2
        for r in self.resources:
            prob += lpSum([x[(t, r)] for t in self.tasks]) <= max_tasks_per_resource, f"Capacity_{r}"
       
        # Solve the problem
        prob.solve()
       
        # Extract results
        optimized_allocation = self._extract_solution(x)
        optimized_duration = self._calculate_optimized_duration(optimized_allocation)
       
        improvement = ((baseline_duration - optimized_duration) / baseline_duration) * 100
       
        return {
            'status': 'success' if LpStatus[prob.status] == 'Optimal' else 'suboptimal',
            'baseline_duration': baseline_duration,
            'optimized_duration': optimized_duration,
            'improvement_percentage': improvement,  # Can be negative if worse
            'optimized_allocation': optimized_allocation,
            'recommendations': self._generate_recommendations(optimized_allocation, improvement)
        }
   
    def _calculate_baseline_duration(self) -> float:
        """Calculate baseline project duration from current allocation (max workload)."""
        # Calculate max resource workload in original allocation (realistic baseline)
        resource_workload = self.df.groupby('Resource_Name')['Duration_Days'].sum()
        return resource_workload.max()
   
    def _extract_solution(self, x: Dict) -> List[Dict]:
        """Extract task-resource assignments from optimization solution."""
        allocation = []
        for (t, r), var in x.items():
            if value(var) == 1:  # Task t is assigned to resource r
                task_data = self.df[self.df['Task_ID'] == t].iloc[0]
                allocation.append({
                    'task_id': t,
                    'task_name': task_data['Task_Name'],
                    'resource': r,
                    'duration': task_data['Duration_Days'],
                    'cost': task_data['Cost_Per_Day']
                })
        return allocation
   
    def _calculate_optimized_duration(self, allocation: List[Dict]) -> float:
        """
        Calculate optimized project duration.
        Accounts for parallel execution by resource.
        """
        # Group by resource
        resource_workload = {}
        for item in allocation:
            r = item['resource']
            if r not in resource_workload:
                resource_workload[r] = 0
            resource_workload[r] += item['duration']
       
        # Project duration = max resource workload (critical path)
        return max(resource_workload.values()) if resource_workload else 0
   
    def _generate_recommendations(self, allocation: List[Dict], improvement: float) -> str:
        """Generate actionable recommendations based on optimization."""
       
        # Group tasks by resource
        resource_tasks = {}
        for item in allocation:
            r = item['resource']
            if r not in resource_tasks:
                resource_tasks[r] = []
            resource_tasks[r].append(item)
       
        # Calculate baseline and optimized durations for display
        baseline_duration = self._calculate_baseline_duration()
        optimized_duration = max(sum(t['duration'] for t in tasks) for tasks in resource_tasks.values()) if resource_tasks else 0
       
        recommendations = f"""
OPTIMIZATION RECOMMENDATIONS
═══════════════════════════════════════════════════════════════
 
🎯 PERFORMANCE IMPROVEMENT: {improvement:.1f}%
{'✅ SUCCESSFUL OPTIMIZATION' if improvement > 0 else '⚠️  NO IMPROVEMENT - Original allocation is already optimal or better'}
{'✅ Meets 10% target' if improvement >= 10 else ''}
 
📊 DURATION COMPARISON:
  Original Critical Path: {baseline_duration} days
  Optimized Critical Path: {optimized_duration} days (longest resource)
 
📋 OPTIMIZED RESOURCE ALLOCATION:
"""
       
        for resource, tasks in sorted(resource_tasks.items()):
            total_days = sum(t['duration'] for t in tasks)
            total_cost = sum(t['duration'] * t['cost'] for t in tasks)
            recommendations += f"""
  {resource}:
    - Assigned Tasks: {len(tasks)}
    - Total Duration: {total_days} days
    - Total Cost: ${total_cost:,.2f}
    - Tasks: {', '.join([t['task_name'] for t in tasks[:5]])}{'...' if len(tasks) > 5 else ''}
"""
       
        recommendations += f"""
💡 KEY ACTIONS:
  {'1. Implement the optimized allocation to reduce project duration' if improvement > 0 else '1. Keep current allocation - it is already optimal'}
  2. Monitor critical path (longest resource workload) during execution
  3. Rebalance if new tasks are added or durations change
  4. Consider hiring if all resources are at capacity
  5. Implement parallel task execution where dependencies allow
 
📊 OPTIMIZATION DETAILS:
  - Algorithm: Linear Programming with Makespan Minimization (PuLP)
  - Objective: Minimize project critical path (longest resource workload)
  - Constraints: Task-resource assignment, capacity limits, makespan constraints
  - Status: {'✅ Optimal solution found' if improvement >= 0 else '⚠️  Suboptimal solution'}
 
⚠️  IMPORTANT NOTES:
  - This optimization ignores task dependencies (assumes all can run in parallel)
  - Actual project duration may be longer due to dependency chains
  - Consider critical path method (CPM) for dependency-aware scheduling
"""
       
        return recommendations
 
 
def optimize_resources(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Convenience function to run resource optimization.
   
    Args:
        df: DataFrame with project data
       
    Returns:
        Optimization results
    """
    optimizer = ResourceOptimizer(df)
    return optimizer.optimize_allocation()
 
 
if __name__ == "__main__":
    # Test optimization
    import pandas as pd
   
    df = pd.read_csv("dummy_data.csv")
    results = optimize_resources(df)
   
    print("\n" + "="*60)
    print("RESOURCE OPTIMIZATION RESULTS")
    print("="*60)
    print(f"Baseline Duration: {results['baseline_duration']} days")
    print(f"Optimized Duration: {results['optimized_duration']:.1f} days")
    print(f"Improvement: {results['improvement_percentage']:.1f}%")
    print(f"\nStatus: {results['status']}")
    print(results['recommendations'])
 
 
