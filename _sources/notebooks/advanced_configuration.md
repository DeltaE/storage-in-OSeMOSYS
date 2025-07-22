# Advanced Configuration Tutorial

## Overview

This tutorial covers advanced configuration options and expert-level usage of the Storage-in-OSeMOSYS framework for complex energy system modeling scenarios.

## Advanced Configuration Options

### Multi-Level Configuration System

The framework supports hierarchical configuration management:

```yaml
# config/advanced_config.yaml
global:
  project_name: "Advanced Storage Study"
  version: "2025.07"
  author: "Your Name"
  
model:
  temporal:
    resolution: "hourly"
    clustering_method: "Kotzur"
    representative_periods: 12
    extreme_periods: 4
    
  spatial:
    regions: ["NORTH", "SOUTH", "EAST", "WEST"]
    transmission_enabled: true
    
  technologies:
    renewable:
      - WIND_ONSHORE
      - WIND_OFFSHORE  
      - SOLAR_PV
      - SOLAR_CSP
    storage:
      - BATTERY_LI
      - BATTERY_FLOW
      - PHES
      - CAES
      - HYDROGEN
    conventional:
      - CCGT
      - COAL
      - NUCLEAR

storage:
  advanced_constraints:
    degradation_modeling: true
    cycling_constraints: true
    ancillary_services: true
    
  battery:
    technologies:
      BATTERY_LI:
        energy_density: 250  # Wh/kg
        power_density: 1500  # W/kg
        cycle_life: 5000
        calendar_life: 15  # years
        round_trip_efficiency: 0.85
        degradation_rate: 0.02  # per year
        
      BATTERY_FLOW:
        energy_density: 40   # Wh/kg
        power_density: 200   # W/kg
        cycle_life: 12000
        calendar_life: 20
        round_trip_efficiency: 0.75
        degradation_rate: 0.005
        
  pumped_hydro:
    PHES:
      efficiency_pump: 0.85
      efficiency_turbine: 0.9
      minimum_power: 0.3  # fraction of rated power
      startup_time: 10    # minutes
      shutdown_time: 5    # minutes
      head_dependent: true
      
  hydrogen:
    HYDROGEN:
      electrolyzer_efficiency: 0.65
      fuel_cell_efficiency: 0.55
      storage_pressure: 350  # bar
      compression_energy: 2.5  # kWh/kg
      leakage_rate: 0.001  # per day

optimization:
  solver:
    name: "gurobi"  # or "cplex", "glpk"
    threads: 8
    mip_gap: 0.01
    time_limit: 7200  # seconds
    
  options:
    presolve: true
    cuts: "aggressive"
    heuristics: "intensive"
    
  advanced:
    decomposition: "benders"
    parallel_scenarios: true
    warm_start: true
```

### Custom Technology Definitions

```python
# advanced_tech_config.py
import yaml
from pathlib import Path

def create_advanced_battery_config():
    """Create advanced battery technology configuration"""
    
    battery_config = {
        'BATTERY_LI_GRID': {
            'type': 'storage',
            'storage_type': 'electrochemical',
            'parameters': {
                'CapitalCost': {
                    2020: 400,  # $/kWh
                    2025: 300,
                    2030: 200,
                    2035: 150,
                    2040: 120
                },
                'VariableCost': 0.5,  # $/MWh
                'FixedCost': 10,      # $/kW-year
                'Efficiency': 0.85,
                'StorageLevelStart': 0.5,
                'MinStorageCharge': 0.1,
                'MaxStorageCharge': 0.95,
                'StorageDuration': 4,  # hours
                'CyclingConstraints': {
                    'max_cycles_per_day': 2,
                    'depth_of_discharge': 0.8,
                    'degradation_factor': 0.99995  # per cycle
                }
            }
        },
        
        'HYDROGEN_SYSTEM': {
            'type': 'storage',
            'storage_type': 'chemical',
            'components': {
                'electrolyzer': {
                    'efficiency': 0.65,
                    'min_load': 0.1,
                    'ramp_rate': 0.5,  # per minute
                    'capital_cost': 800,  # $/kW
                    'operational_life': 15
                },
                'fuel_cell': {
                    'efficiency': 0.55,
                    'min_load': 0.05,
                    'ramp_rate': 0.8,
                    'capital_cost': 1200,  # $/kW
                    'operational_life': 10
                },
                'storage_tank': {
                    'pressure': 350,  # bar
                    'capital_cost': 30,  # $/kWh
                    'leakage_rate': 0.001,  # per day
                    'operational_life': 30
                }
            }
        }
    }
    
    return battery_config

def implement_advanced_constraints():
    """Implement advanced storage constraints"""
    
    constraints = {
        'cycling_degradation': {
            'description': 'Battery degradation based on cycling',
            'formula': 'capacity_remaining = initial_capacity * (degradation_factor ^ cycles)',
            'implementation': 'post_processing'
        },
        
        'state_of_charge_dependent_efficiency': {
            'description': 'Efficiency varies with state of charge',
            'formula': 'efficiency = base_efficiency * soc_efficiency_curve(soc)',
            'implementation': 'model_constraints'
        },
        
        'temperature_effects': {
            'description': 'Temperature-dependent performance',
            'formula': 'performance = base_performance * temperature_factor(ambient_temp)',
            'implementation': 'external_data'
        }
    }
    
    return constraints
```

## Multi-Objective Optimization

### Pareto-Optimal Solutions

```python
# multi_objective_optimization.py
import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

def multi_objective_storage_optimization():
    """Perform multi-objective optimization for storage planning"""
    
    # Define objectives
    objectives = {
        'minimize_cost': lambda x: calculate_total_cost(x),
        'minimize_emissions': lambda x: calculate_total_emissions(x),
        'maximize_reliability': lambda x: -calculate_reliability_score(x),
        'minimize_curtailment': lambda x: calculate_renewable_curtailment(x)
    }
    
    # Pareto frontier calculation
    pareto_solutions = []
    weights_combinations = generate_weight_combinations(len(objectives), 20)
    
    for weights in weights_combinations:
        # Combined objective function
        def combined_objective(x):
            total = 0
            for i, (obj_name, obj_func) in enumerate(objectives.items()):
                total += weights[i] * obj_func(x)
            return total
        
        # Optimize
        result = minimize(combined_objective, x0=get_initial_guess(), 
                         bounds=get_decision_variable_bounds(),
                         method='SLSQP')
        
        if result.success:
            # Evaluate all objectives for this solution
            solution_objectives = {}
            for obj_name, obj_func in objectives.items():
                solution_objectives[obj_name] = obj_func(result.x)
            
            pareto_solutions.append({
                'variables': result.x,
                'objectives': solution_objectives,
                'weights': weights
            })
    
    return pareto_solutions

def plot_pareto_frontier(pareto_solutions):
    """Plot 2D projections of Pareto frontier"""
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle('Multi-Objective Optimization: Pareto Frontiers', fontsize=16)
    
    # Extract objective values
    costs = [sol['objectives']['minimize_cost'] for sol in pareto_solutions]
    emissions = [sol['objectives']['minimize_emissions'] for sol in pareto_solutions]
    reliability = [-sol['objectives']['maximize_reliability'] for sol in pareto_solutions]
    curtailment = [sol['objectives']['minimize_curtailment'] for sol in pareto_solutions]
    
    # Plot 2D projections
    axes[0, 0].scatter(costs, emissions, alpha=0.7)
    axes[0, 0].set_xlabel('Total Cost (M$)')
    axes[0, 0].set_ylabel('CO2 Emissions (Mt)')
    axes[0, 0].set_title('Cost vs. Emissions')
    
    axes[0, 1].scatter(costs, reliability, alpha=0.7, color='orange')
    axes[0, 1].set_xlabel('Total Cost (M$)')
    axes[0, 1].set_ylabel('Reliability Score')
    axes[0, 1].set_title('Cost vs. Reliability')
    
    axes[0, 2].scatter(emissions, reliability, alpha=0.7, color='green')
    axes[0, 2].set_xlabel('CO2 Emissions (Mt)')
    axes[0, 2].set_ylabel('Reliability Score')
    axes[0, 2].set_title('Emissions vs. Reliability')
    
    axes[1, 0].scatter(costs, curtailment, alpha=0.7, color='red')
    axes[1, 0].set_xlabel('Total Cost (M$)')
    axes[1, 0].set_ylabel('Renewable Curtailment (%)')
    axes[1, 0].set_title('Cost vs. Curtailment')
    
    axes[1, 1].scatter(emissions, curtailment, alpha=0.7, color='purple')
    axes[1, 1].set_xlabel('CO2 Emissions (Mt)')
    axes[1, 1].set_ylabel('Renewable Curtailment (%)')
    axes[1, 1].set_title('Emissions vs. Curtailment')
    
    axes[1, 2].scatter(reliability, curtailment, alpha=0.7, color='brown')
    axes[1, 2].set_xlabel('Reliability Score')
    axes[1, 2].set_ylabel('Renewable Curtailment (%)')
    axes[1, 2].set_title('Reliability vs. Curtailment')
    
    plt.tight_layout()
    plt.show()
    
    return fig
```

## Uncertainty and Risk Analysis

### Monte Carlo Simulation

```python
# uncertainty_analysis.py
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

def monte_carlo_uncertainty_analysis(n_simulations=1000):
    """Perform Monte Carlo analysis for storage planning under uncertainty"""
    
    # Define uncertain parameters with probability distributions
    uncertain_params = {
        'renewable_capacity_factor': {
            'distribution': 'normal',
            'params': {'mean': 0.35, 'std': 0.05},
            'bounds': [0.2, 0.5]
        },
        'demand_growth': {
            'distribution': 'normal', 
            'params': {'mean': 0.02, 'std': 0.01},
            'bounds': [0.005, 0.05]
        },
        'storage_cost_reduction': {
            'distribution': 'beta',
            'params': {'a': 2, 'b': 2, 'scale': 0.6, 'loc': 0.2},
            'bounds': [0.2, 0.8]
        },
        'carbon_price': {
            'distribution': 'lognormal',
            'params': {'s': 0.5, 'scale': 50},
            'bounds': [20, 200]
        },
        'gas_price': {
            'distribution': 'gamma',
            'params': {'a': 2, 'scale': 15},
            'bounds': [5, 80]
        }
    }
    
    # Generate random samples
    samples = {}
    for param, config in uncertain_params.items():
        if config['distribution'] == 'normal':
            raw_samples = np.random.normal(
                config['params']['mean'], 
                config['params']['std'], 
                n_simulations
            )
        elif config['distribution'] == 'beta':
            raw_samples = stats.beta.rvs(
                config['params']['a'],
                config['params']['b'],
                loc=config['params']['loc'],
                scale=config['params']['scale'],
                size=n_simulations
            )
        elif config['distribution'] == 'lognormal':
            raw_samples = stats.lognorm.rvs(
                config['params']['s'],
                scale=config['params']['scale'],
                size=n_simulations
            )
        elif config['distribution'] == 'gamma':
            raw_samples = stats.gamma.rvs(
                config['params']['a'],
                scale=config['params']['scale'],
                size=n_simulations
            )
        
        # Apply bounds
        samples[param] = np.clip(raw_samples, 
                                config['bounds'][0], 
                                config['bounds'][1])
    
    # Run simulations
    results = []
    for i in range(n_simulations):
        if i % 100 == 0:
            print(f"Running simulation {i+1}/{n_simulations}")
        
        # Create scenario configuration
        scenario_config = {}
        for param in uncertain_params:
            scenario_config[param] = samples[param][i]
        
        # Run model
        try:
            result = run_storage_model_with_uncertainty(scenario_config)
            results.append(result)
        except Exception as e:
            print(f"Simulation {i+1} failed: {str(e)}")
            results.append(None)
    
    # Analyze results
    successful_results = [r for r in results if r is not None]
    analysis = analyze_monte_carlo_results(successful_results, samples)
    
    return analysis

def analyze_monte_carlo_results(results, input_samples):
    """Analyze Monte Carlo simulation results"""
    
    # Extract key metrics from results
    metrics = {}
    for result in results:
        if result is not None:
            for key in ['total_cost', 'storage_capacity', 'renewable_share', 'emissions']:
                if key not in metrics:
                    metrics[key] = []
                metrics[key].append(result.get(key, 0))
    
    # Statistical analysis
    statistics = {}
    for metric, values in metrics.items():
        statistics[metric] = {
            'mean': np.mean(values),
            'std': np.std(values),
            'min': np.min(values),
            'max': np.max(values),
            'q25': np.percentile(values, 25),
            'q50': np.percentile(values, 50),
            'q75': np.percentile(values, 75),
            'q95': np.percentile(values, 95),
            'q99': np.percentile(values, 99)
        }
    
    # Sensitivity analysis
    sensitivity = calculate_sensitivity_indices(input_samples, metrics)
    
    # Risk metrics
    risk_metrics = calculate_risk_metrics(metrics)
    
    return {
        'statistics': statistics,
        'sensitivity': sensitivity,
        'risk_metrics': risk_metrics,
        'raw_results': results
    }

def plot_uncertainty_analysis(analysis):
    """Plot uncertainty analysis results"""
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Storage Planning Under Uncertainty', fontsize=16)
    
    # Probability distributions
    metrics = ['total_cost', 'storage_capacity', 'renewable_share', 'emissions']
    titles = ['Total Cost (M$)', 'Storage Capacity (GW)', 
              'Renewable Share (%)', 'CO2 Emissions (Mt)']
    
    for i, (metric, title) in enumerate(zip(metrics, titles)):
        ax = axes[i//2, i%2]
        
        values = analysis['statistics'][metric]
        
        # Histogram
        ax.hist(values, bins=30, alpha=0.7, density=True, color='skyblue')
        
        # Statistical markers
        mean_val = analysis['statistics'][metric]['mean']
        q95_val = analysis['statistics'][metric]['q95']
        
        ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label='Mean')
        ax.axvline(q95_val, color='orange', linestyle='--', linewidth=2, label='95th Percentile')
        
        ax.set_xlabel(title)
        ax.set_ylabel('Probability Density')
        ax.set_title(f'{title} Distribution')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    return fig
```

## Advanced Temporal Modeling

### Custom Clustering Algorithms

```python
# custom_clustering.py
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import numpy as np

def adaptive_temporal_clustering(time_series_data, storage_data=None):
    """Implement adaptive temporal clustering for storage systems"""
    
    # Prepare features for clustering
    features = prepare_clustering_features(time_series_data, storage_data)
    
    # Determine optimal number of clusters
    optimal_clusters = find_optimal_clusters(features)
    
    # Perform clustering with storage-aware objectives
    clusters = storage_aware_clustering(features, optimal_clusters)
    
    # Generate representative periods
    representative_periods = generate_representative_periods(
        time_series_data, clusters, storage_data
    )
    
    return {
        'clusters': clusters,
        'representative_periods': representative_periods,
        'cluster_weights': calculate_cluster_weights(clusters),
        'clustering_metrics': evaluate_clustering_quality(features, clusters)
    }

def prepare_clustering_features(time_series_data, storage_data):
    """Prepare features for clustering including storage considerations"""
    
    features = []
    
    # Basic load and renewable features
    features.extend([
        time_series_data['demand'],
        time_series_data['wind'],
        time_series_data['solar']
    ])
    
    # Storage-specific features
    if storage_data is not None:
        # Net load (demand - renewables)
        net_load = time_series_data['demand'] - time_series_data['wind'] - time_series_data['solar']
        features.append(net_load)
        
        # Ramp rates
        demand_ramp = np.diff(time_series_data['demand'], prepend=time_series_data['demand'][0])
        renewable_ramp = np.diff(time_series_data['wind'] + time_series_data['solar'], 
                               prepend=time_series_data['wind'][0] + time_series_data['solar'][0])
        features.extend([demand_ramp, renewable_ramp])
        
        # Storage opportunity index
        storage_opportunity = calculate_storage_opportunity_index(time_series_data)
        features.append(storage_opportunity)
    
    # Temporal features
    hour_of_day = np.arange(len(time_series_data['demand'])) % 24
    day_of_week = (np.arange(len(time_series_data['demand'])) // 24) % 7
    features.extend([hour_of_day, day_of_week])
    
    return np.array(features).T

def storage_aware_clustering(features, n_clusters):
    """Perform clustering with storage system considerations"""
    
    # Initialize clustering with storage-aware objective
    clustering = StorageAwareKMeans(n_clusters=n_clusters)
    clusters = clustering.fit_predict(features)
    
    return clusters

class StorageAwareKMeans:
    """Custom K-means clustering that considers storage operation patterns"""
    
    def __init__(self, n_clusters, storage_weight=0.3):
        self.n_clusters = n_clusters
        self.storage_weight = storage_weight
        self.kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        
    def fit_predict(self, features):
        # Standard clustering
        standard_clusters = self.kmeans.fit_predict(features)
        
        # Storage-aware refinement
        refined_clusters = self.refine_clusters_for_storage(features, standard_clusters)
        
        return refined_clusters
    
    def refine_clusters_for_storage(self, features, initial_clusters):
        """Refine clusters to better represent storage operation patterns"""
        
        # Calculate storage operation patterns for each cluster
        cluster_storage_patterns = {}
        for cluster_id in range(self.n_clusters):
            cluster_mask = initial_clusters == cluster_id
            cluster_features = features[cluster_mask]
            
            # Calculate storage opportunity for this cluster
            storage_pattern = self.calculate_cluster_storage_pattern(cluster_features)
            cluster_storage_patterns[cluster_id] = storage_pattern
        
        # Refine cluster assignments based on storage patterns
        refined_clusters = initial_clusters.copy()
        
        # Implementation of refinement algorithm
        # (Details would depend on specific storage modeling requirements)
        
        return refined_clusters
    
    def calculate_cluster_storage_pattern(self, cluster_features):
        """Calculate storage operation pattern for a cluster"""
        
        # Extract relevant features for storage analysis
        net_load = cluster_features[:, 3]  # Assuming net load is 4th feature
        ramp_rates = cluster_features[:, 4:6]  # Demand and renewable ramps
        
        # Calculate storage metrics
        storage_potential = np.std(net_load)  # Variability indicates storage potential
        ramp_severity = np.mean(np.abs(ramp_rates))  # Average ramp magnitude
        
        return {
            'storage_potential': storage_potential,
            'ramp_severity': ramp_severity,
            'average_net_load': np.mean(net_load)
        }
```

## Advanced Results Analysis

### Machine Learning-Enhanced Analysis

```python
# ml_enhanced_analysis.py
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
import shap

def ml_enhanced_results_analysis(historical_results, scenario_parameters):
    """Use machine learning to analyze and predict storage system performance"""
    
    # Prepare dataset
    X, y = prepare_ml_dataset(historical_results, scenario_parameters)
    
    # Train models for different metrics
    models = {}
    predictions = {}
    
    target_metrics = ['total_cost', 'storage_capacity', 'renewable_integration', 'reliability']
    
    for metric in target_metrics:
        print(f"Training model for {metric}...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y[metric], test_size=0.2, random_state=42
        )
        
        # Train model
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        print(f"  R² Score: {r2:.3f}")
        print(f"  MAE: {mae:.3f}")
        
        models[metric] = model
        predictions[metric] = {
            'y_true': y_test,
            'y_pred': y_pred,
            'r2': r2,
            'mae': mae
        }
    
    # Feature importance analysis
    feature_importance = analyze_feature_importance(models, X.columns)
    
    # SHAP analysis for interpretability
    shap_analysis = perform_shap_analysis(models, X)
    
    return {
        'models': models,
        'predictions': predictions,
        'feature_importance': feature_importance,
        'shap_analysis': shap_analysis
    }

def scenario_optimization_with_ml(ml_models, constraints):
    """Use ML models to optimize scenario parameters"""
    
    from scipy.optimize import differential_evolution
    
    def objective_function(params):
        # Convert params to scenario configuration
        scenario_config = params_to_scenario_config(params)
        
        # Predict outcomes using ML models
        predictions = {}
        for metric, model in ml_models.items():
            pred = model.predict([scenario_config])[0]
            predictions[metric] = pred
        
        # Multi-objective optimization
        # Minimize cost and maximize renewable integration
        cost_weight = 0.6
        renewable_weight = 0.4
        
        normalized_cost = predictions['total_cost'] / 1000  # Normalize to thousands
        normalized_renewable = 1 - (predictions['renewable_integration'] / 100)  # Invert for minimization
        
        objective = cost_weight * normalized_cost + renewable_weight * normalized_renewable
        
        return objective
    
    # Define bounds for optimization variables
    bounds = get_optimization_bounds(constraints)
    
    # Optimize
    result = differential_evolution(objective_function, bounds, maxiter=100)
    
    # Convert result back to scenario configuration
    optimal_scenario = params_to_scenario_config(result.x)
    
    return {
        'optimal_params': result.x,
        'optimal_scenario': optimal_scenario,
        'objective_value': result.fun,
        'optimization_result': result
    }
```

## Integration with External Tools

### API Development

```python
# storage_api.py
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
import uvicorn
import asyncio

app = FastAPI(title="Storage-in-OSeMOSYS API", version="2025.07")

class StorageModelRequest(BaseModel):
    method: str
    config: dict
    input_data: dict

class StorageModelResponse(BaseModel):
    job_id: str
    status: str
    results: dict = None
    error: str = None

# In-memory job storage (use Redis/database in production)
active_jobs = {}

@app.post("/run_model", response_model=StorageModelResponse)
async def run_storage_model_api(request: StorageModelRequest, background_tasks: BackgroundTasks):
    """Run storage model asynchronously"""
    
    job_id = generate_job_id()
    
    # Start background task
    background_tasks.add_task(
        execute_storage_model_task,
        job_id,
        request.method,
        request.config,
        request.input_data
    )
    
    active_jobs[job_id] = {
        'status': 'running',
        'results': None,
        'error': None
    }
    
    return StorageModelResponse(job_id=job_id, status='running')

@app.get("/job_status/{job_id}", response_model=StorageModelResponse)
async def get_job_status(job_id: str):
    """Get status of running job"""
    
    if job_id not in active_jobs:
        return StorageModelResponse(
            job_id=job_id,
            status='not_found',
            error='Job ID not found'
        )
    
    job = active_jobs[job_id]
    return StorageModelResponse(
        job_id=job_id,
        status=job['status'],
        results=job['results'],
        error=job['error']
    )

async def execute_storage_model_task(job_id, method, config, input_data):
    """Execute storage model in background"""
    
    try:
        # Run the actual model
        results = await run_storage_model_async(method, config, input_data)
        
        # Update job status
        active_jobs[job_id] = {
            'status': 'completed',
            'results': results,
            'error': None
        }
        
    except Exception as e:
        active_jobs[job_id] = {
            'status': 'failed',
            'results': None,
            'error': str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### Cloud Integration

```python
# cloud_integration.py
import boto3
import json
from azure.storage.blob import BlobServiceClient
from google.cloud import storage as gcs

class CloudStorageManager:
    """Manage storage model data in cloud platforms"""
    
    def __init__(self, provider='aws'):
        self.provider = provider
        self.setup_cloud_client()
    
    def setup_cloud_client(self):
        if self.provider == 'aws':
            self.client = boto3.client('s3')
            self.bucket = 'storage-osemosys-models'
        elif self.provider == 'azure':
            self.client = BlobServiceClient.from_connection_string(
                os.environ['AZURE_STORAGE_CONNECTION_STRING']
            )
            self.container = 'storage-models'
        elif self.provider == 'gcp':
            self.client = gcs.Client()
            self.bucket = self.client.bucket('storage-osemosys-models')
    
    def upload_model_data(self, local_path, cloud_path):
        """Upload model data to cloud storage"""
        
        if self.provider == 'aws':
            self.client.upload_file(local_path, self.bucket, cloud_path)
        elif self.provider == 'azure':
            blob_client = self.client.get_blob_client(
                container=self.container, blob=cloud_path
            )
            with open(local_path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
        elif self.provider == 'gcp':
            blob = self.bucket.blob(cloud_path)
            blob.upload_from_filename(local_path)
    
    def download_model_data(self, cloud_path, local_path):
        """Download model data from cloud storage"""
        
        if self.provider == 'aws':
            self.client.download_file(self.bucket, cloud_path, local_path)
        elif self.provider == 'azure':
            blob_client = self.client.get_blob_client(
                container=self.container, blob=cloud_path
            )
            with open(local_path, 'wb') as download_file:
                download_file.write(blob_client.download_blob().readall())
        elif self.provider == 'gcp':
            blob = self.bucket.blob(cloud_path)
            blob.download_to_filename(local_path)

def setup_cloud_computing_environment():
    """Set up cloud computing environment for large-scale studies"""
    
    # AWS EC2 setup
    ec2_config = {
        'instance_type': 'c5.4xlarge',  # 16 vCPUs, 32 GB RAM
        'ami_id': 'ami-0c02fb55956c7d316',  # Amazon Linux 2
        'security_group': 'storage-osemosys-sg',
        'key_pair': 'storage-osemosys-key'
    }
    
    # Auto Scaling configuration
    autoscaling_config = {
        'min_size': 1,
        'max_size': 10,
        'desired_capacity': 2,
        'scale_up_threshold': 70,  # CPU utilization %
        'scale_down_threshold': 30
    }
    
    return ec2_config, autoscaling_config
```

This advanced configuration tutorial provides expert-level features for complex energy system modeling scenarios with sophisticated storage representations, uncertainty analysis, and cloud integration capabilities. The framework supports multi-objective optimization, machine learning-enhanced analysis, and scalable cloud deployment for large-scale studies.

Continue exploring the [API Reference](../notes/api_reference.md) for detailed function documentation.
