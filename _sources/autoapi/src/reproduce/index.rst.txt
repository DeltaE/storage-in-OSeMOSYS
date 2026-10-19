src.reproduce
=============

.. py:module:: src.reproduce

.. autoapi-nested-parse::

   Helpers for reproducing Bruno, Islam & Niet, "Storage in long-term energy planning models with
   temporal aggregation" (Environ. Res. Commun., ERC-105849) with this repository.

   Used by ``reproduce_study.ipynb`` and ``automation.py``. Every model run goes through ``main.py``
   unchanged, so the notebook exercises exactly the code path that produced the published numbers.

   Naming: the formulation called *Novo* in the paper is implemented in ``Model_Cluster``.



Attributes
----------

.. autoapisummary::

   src.reproduce.REPO
   src.reproduce.RESOURCES
   src.reproduce.DEMAND_PROFILE
   src.reproduce.K_VALUES
   src.reproduce.H_VALUES
   src.reproduce.MODELS
   src.reproduce.FORMULATION
   src.reproduce.UNCONSTRAINED_CAP
   src.reproduce.STRESS_CAP
   src.reproduce.RESIDUAL_STORAGE
   src.reproduce.MANUSCRIPT_ENV
   src.reproduce.TABLE4_CASES


Functions
---------

.. autoapisummary::

   src.reproduce.check_environment
   src.reproduce.scenario_name
   src.reproduce.run_case
   src.reproduce.run_grid
   src.reproduce.load_results
   src.reproduce.add_errors
   src.reproduce.table4
   src.reproduce.compare_to_archive
   src.reproduce.clustering
   src.reproduce.seed_robustness
   src.reproduce.run_soc_validation
   src.reproduce.read_storage
   src.reproduce.soc_violations
   src.reproduce.hourly_trajectory
   src.reproduce.rainflow_cycles
   src.reproduce.fidelity_metrics


Module Contents
---------------

.. py:data:: REPO

.. py:data:: RESOURCES

.. py:data:: DEMAND_PROFILE
   :value: 'SpecifiedDemandProfile.csv'


.. py:data:: K_VALUES
   :value: [2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]


.. py:data:: H_VALUES
   :value: [1, 2, 4, 6, 8, 12]


.. py:data:: MODELS
   :value: ['Model_Niet', 'Model_Welsch', 'Model_Kotzur', 'Model_Cluster']


.. py:data:: FORMULATION

.. py:data:: UNCONSTRAINED_CAP
   :value: 1000.0


.. py:data:: STRESS_CAP
   :value: 0.2


.. py:data:: RESIDUAL_STORAGE
   :value: 0.05


.. py:data:: MANUSCRIPT_ENV

.. py:function:: check_environment() -> pandas.DataFrame

   Installed versions against the environment stated in Section 3.4.


.. py:function:: scenario_name(resource: str, k: int, h: int, limited: bool = False, suffix: str = '') -> str

.. py:function:: run_case(resource: str, k: int, h: int, *, cap: float = UNCONSTRAINED_CAP, random_state: int = 0, results_dir: str | pathlib.Path = 'Results', models: list | None = None, limited: bool | None = None, suffix: str = '', timeout: float | None = None, verbose: bool = False) -> pandas.DataFrame

   Run one scenario (all four formulations unless ``models`` is given) via ``main.py``.

   The config file is restored afterwards. Returns the rows appended to Simulation_Results.xlsx.


.. py:function:: run_grid(resources, ks, hs, *, skip_existing: bool = True, **kw) -> pandas.DataFrame

   Run a grid of scenarios; already-completed scenarios are skipped.


.. py:function:: load_results(xlsx: str | pathlib.Path) -> pandas.DataFrame

   Tidy Simulation_Results.xlsx (one row per scenario x formulation, last run kept).


.. py:function:: add_errors(df: pandas.DataFrame) -> pandas.DataFrame

   Cost and storage-capacity error (%) against the k365h1 Novo benchmark of the same resource.

   Errors use unrounded values. (Table 4 in the R2 draft divides by the benchmark rounded to two
   decimals, which shifts some capacity errors by up to ~3 percentage points.)


.. py:data:: TABLE4_CASES

.. py:function:: table4(df: pandas.DataFrame) -> pandas.DataFrame

   Rebuild manuscript Table 4 (h = 1, unconstrained).


.. py:function:: compare_to_archive(new: pandas.DataFrame, archive: pandas.DataFrame, cols=('Total cost', 'Power Capacity', 'Storage Capacity')) -> pandas.DataFrame

   Relative difference between fresh runs and the archived results (same Scenario x Model).


.. py:function:: clustering(resource: str, k: int, random_state: int = 0)

   Representative days and chronological day->representative mapping, as used by main.py.


.. py:function:: seed_robustness(resources=('WND', 'SOL', 'HYD'), ks=K_VALUES, seeds=range(10)) -> pandas.DataFrame

   Compare clusterings for alternative seeds against seed 0.

   day_agreement: share of the 365 days mapped to the same representative day as with seed 0.
   ARI: adjusted Rand index of the day partition (label-permutation invariant).
   same_rep_days: whether the set of representative days is identical.


.. py:function:: run_soc_validation() -> pandas.DataFrame

.. py:function:: read_storage(results_dir: str | pathlib.Path, scenario: str, model: str) -> pandas.Series

   Native or reconstructed storage level written by main.py.

   model: 'Niet', 'Cluster' (Novo), 'Kotzur' (day starts), 'Kotzur_intraday', 'Welsch' (day-type
   starts) or 'Welsch_intraday'.


.. py:function:: soc_violations(soc, upper: float, lower: float = 0.0, tol: float = 1e-09) -> dict

   Count bound violations of a storage trajectory.

   strict: SoC > upper + tol or SoC < lower - tol (physically infeasible states).
   at_or_beyond: SoC >= upper - tol or SoC <= lower + tol (includes states exactly on a bound,
   which are feasible). The R2 draft's '183 h above' for wind equals the at_or_beyond count.


.. py:function:: hourly_trajectory(results_dir, scenario: str, formulation: str, h: int) -> numpy.ndarray

   8760-h storage trajectory used for the fidelity metrics.

   Novo and Kotzur: chronological block series (Kotzur reconstructed), held over each block.
   Welsch: reconstructed series in its native grouped day-type order, as plotted by
   graph_generator.py. Niet: representative blocks held for their year-split duration.


.. py:function:: rainflow_cycles(series) -> float

   Equivalent full cycles by rainflow counting (ASTM E1049-85 three-point method).

   Half cycles count 0.5. Returns the total number of (equivalent full) cycles.


.. py:function:: fidelity_metrics(benchmark, test) -> dict

