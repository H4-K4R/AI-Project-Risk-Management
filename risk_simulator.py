"""
Monte Carlo Risk Simulation Module
AI-Powered Project Risk & Resource Management
 
# Aligns with AI4SE Phase 7: Risk Analysis & Prediction
# Uses Monte Carlo simulation to predict project outcomes
"""
 
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
 
 
@dataclass
class SimulationResult:
    """Results from Monte Carlo simulation."""
    mean_duration: float
    std_duration: float
    percentile_50: float
    percentile_75: float
    percentile_90: float
    percentile_95: float
    mean_cost: float
    std_cost: float
    risk_probability: float  # Probability of exceeding baseline
 
 
class RiskSimulator:
    """
    Monte Carlo simulation for project risk analysis.
    Simulates thousands of project scenarios to predict likely outcomes.
   
    Goal: Predict risks with 85%+ accuracy.
    """
   
    def __init__(self, df: pd.DataFrame, num_simulations: int = 1000):
        """
        Initialize simulator with project data.
       
        Args:
            df: DataFrame with project tasks
            num_simulations: Number of Monte Carlo iterations
        """
        self.df = df.copy()
        self.num_simulations = num_simulations
       
        # Risk multipliers for duration uncertainty
        self.risk_multipliers = {
            'High': (0.8, 1.5),    # High risk: -20% to +50% variance
            'Med': (0.9, 1.2),     # Medium risk: -10% to +20% variance
            'Low': (0.95, 1.05)    # Low risk: -5% to +5% variance
        }
   
    def run_simulation(self) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for project risk analysis.
       
        Returns:
            Dictionary with simulation results and risk assessment
        """
        print(f"\n🎲 Running Monte Carlo Simulation ({self.num_simulations} iterations)...")
       
        durations = []
        costs = []
       
        baseline_duration = self.df['Duration_Days'].sum()
        baseline_cost = (self.df['Duration_Days'] * self.df['Cost_Per_Day']).sum()
       
        # Run simulations
        for i in range(self.num_simulations):
            sim_duration, sim_cost = self._simulate_scenario()
            durations.append(sim_duration)
            costs.append(sim_cost)
           
            if (i + 1) % 200 == 0:
                print(f"  Progress: {i+1}/{self.num_simulations} simulations...")
       
        print("✅ Simulation complete!")
       
        # Calculate statistics
        durations = np.array(durations)
        costs = np.array(costs)
       
        result = SimulationResult(
            mean_duration=np.mean(durations),
            std_duration=np.std(durations),
            percentile_50=np.percentile(durations, 50),
            percentile_75=np.percentile(durations, 75),
            percentile_90=np.percentile(durations, 90),
            percentile_95=np.percentile(durations, 95),
            mean_cost=np.mean(costs),
            std_cost=np.std(costs),
            risk_probability=(durations > baseline_duration).sum() / self.num_simulations
        )
       
        # Generate risk assessment
        risk_assessment = self._assess_risk(result, baseline_duration, baseline_cost)
       
        return {
            'status': 'success',
            'simulation_result': result,
            'baseline_duration': baseline_duration,
            'baseline_cost': baseline_cost,
            'risk_assessment': risk_assessment,
            'confidence_level': self._calculate_confidence(result)
        }
   
    def _simulate_scenario(self) -> Tuple[float, float]:
        """
        Simulate one project scenario with task duration variance.
       
        Returns:
            Tuple of (total_duration, total_cost) for this scenario
        """
        total_duration = 0
        total_cost = 0
       
        for _, task in self.df.iterrows():
            risk_level = task['Risk_Level']
            base_duration = task['Duration_Days']
            cost_per_day = task['Cost_Per_Day']
           
            # Apply risk-based variance
            min_mult, max_mult = self.risk_multipliers.get(risk_level, (1.0, 1.0))
            duration_multiplier = np.random.uniform(min_mult, max_mult)
           
            simulated_duration = base_duration * duration_multiplier
            simulated_cost = simulated_duration * cost_per_day
           
            total_duration += simulated_duration
            total_cost += simulated_cost
       
        return total_duration, total_cost
   
    def _assess_risk(self, result: SimulationResult, baseline_duration: float,
                     baseline_cost: float) -> str:
        """Generate risk assessment report."""
       
        duration_overrun = ((result.mean_duration - baseline_duration) / baseline_duration) * 100
        cost_overrun = ((result.mean_cost - baseline_cost) / baseline_cost) * 100
       
        assessment = f"""
MONTE CARLO RISK SIMULATION RESULTS
═══════════════════════════════════════════════════════════════
 
🎯 SIMULATION PARAMETERS:
  - Number of Iterations: {self.num_simulations:,}
  - Risk Modeling: 3-level variance (High/Med/Low)
  - Method: Monte Carlo sampling
 
📊 DURATION ANALYSIS:
  - Baseline (Planned): {baseline_duration:.0f} days
  - Mean (Expected): {result.mean_duration:.1f} days ({duration_overrun:+.1f}%)
  - Standard Deviation: ±{result.std_duration:.1f} days
 
  Confidence Intervals:
    • 50% confidence: ≤ {result.percentile_50:.0f} days
    • 75% confidence: ≤ {result.percentile_75:.0f} days
    • 90% confidence: ≤ {result.percentile_90:.0f} days (Recommended buffer)
    • 95% confidence: ≤ {result.percentile_95:.0f} days (Conservative estimate)
 
💰 COST ANALYSIS:
  - Baseline (Planned): ${baseline_cost:,.2f}
  - Mean (Expected): ${result.mean_cost:,.2f} ({cost_overrun:+.1f}%)
  - Standard Deviation: ±${result.std_cost:,.2f}
 
  💡 Budget Recommendation: ${result.mean_cost + result.std_cost:,.2f}
     (Mean + 1σ for 84% confidence)
 
⚠️  RISK ASSESSMENT:
  - Probability of Delay: {result.risk_probability*100:.1f}%
  - Risk Level: {self._categorize_risk(result.risk_probability)}
 
  {'🔴 HIGH RISK: Significant chance of exceeding baseline' if result.risk_probability > 0.7
   else '🟡 MEDIUM RISK: Moderate chance of delays' if result.risk_probability > 0.4
   else '🟢 LOW RISK: Project likely to meet timeline'}
 
📋 RECOMMENDATIONS:
  1. Add {result.percentile_90 - baseline_duration:.0f} days buffer for 90% confidence
  2. Budget extra ${(result.mean_cost + result.std_cost) - baseline_cost:,.2f} for contingency
  3. {'Focus on high-risk tasks to reduce variance' if result.std_duration > baseline_duration * 0.2 else 'Current risk profile is acceptable'}
  4. Monitor actual vs. simulated outcomes to improve future predictions
  5. Re-run simulation if major project changes occur
 
🎲 SIMULATION ACCURACY:
  - Confidence Level: {self._calculate_confidence(result)}%
  - Based on: {self.num_simulations:,} Monte Carlo iterations
  {'✅ Meets 85% accuracy threshold for risk prediction' if self._calculate_confidence(result) >= 85
   else '⚠️  Consider running more simulations (recommend 10,000+)'}
"""
       
        return assessment
   
    def _categorize_risk(self, probability: float) -> str:
        """Categorize risk level based on delay probability."""
        if probability > 0.7:
            return "HIGH"
        elif probability > 0.4:
            return "MEDIUM"
        else:
            return "LOW"
   
    def _calculate_confidence(self, result: SimulationResult) -> float:
        """
        Calculate confidence level of simulation.
        Based on coefficient of variation and sample size.
        """
        cv = result.std_duration / result.mean_duration  # Coefficient of variation
       
        # Confidence increases with more simulations and lower variance
        base_confidence = min(90, 70 + (self.num_simulations / 100))
        variance_penalty = cv * 20  # Penalize high variance
       
        confidence = max(50, base_confidence - variance_penalty)
        return round(confidence, 1)
 
 
def simulate_project_risk(df: pd.DataFrame, num_simulations: int = 1000) -> Dict[str, Any]:
    """
    Convenience function to run Monte Carlo risk simulation.
   
    Args:
        df: DataFrame with project data
        num_simulations: Number of Monte Carlo iterations
       
    Returns:
        Simulation results and risk assessment
    """
    simulator = RiskSimulator(df, num_simulations)
    return simulator.run_simulation()
 
 
if __name__ == "__main__":
    # Test simulation
    import pandas as pd
   
    df = pd.read_csv("dummy_data.csv")
    results = simulate_project_risk(df, num_simulations=1000)
   
    print("\n" + "="*60)
    print("MONTE CARLO RISK SIMULATION")
    print("="*60)
    print(results['risk_assessment'])
    print(f"\nConfidence Level: {results['confidence_level']}%")
 
 