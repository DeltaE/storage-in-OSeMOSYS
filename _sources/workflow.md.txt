# Modelling workflow

<p class="page-intro">
This section covers the path from a fresh copy of the code to solved models. The software is
set up once; a single command then runs the pipeline, which picks representative days, builds an
OSeMOSYS model for each storage formulation, solves them and saves the results. New scenarios
only need changes to one configuration file. On a first run, the cards are best followed in
order.
</p>

<div class="section-cards">
  <a class="section-card section-card--terminal" href="notes/README_ENVIRONMENT.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">01</span>
    </span>
    <span class="section-card__title">Set up the environment</span>
    <span class="section-card__text">Python, the GLPK solver and all packages are installed with one <code>make setup</code>, then checked.</span>
  </a>
  <a class="section-card section-card--play" href="quickstart.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">02</span>
    </span>
    <span class="section-card__title">Quickstart</span>
    <span class="section-card__text">Choosing a scenario, running <code>python workflow/main.py</code> and locating the results, in four short steps.</span>
  </a>
  <a class="section-card section-card--workflow" href="notes/workflow_guide.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">03</span>
    </span>
    <span class="section-card__title">How the pipeline works</span>
    <span class="section-card__text">What <code>workflow/main.py</code> does at each stage, from loading data to clustering, solving and plotting.</span>
  </a>
  <a class="section-card section-card--sliders" href="notes/configuration_guide.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">04</span>
    </span>
    <span class="section-card__title">Configuration</span>
    <span class="section-card__text">Every setting in <code>config.yaml</code>: number of days, hour grouping, storage limits and models to run.</span>
  </a>
</div>

```{toctree}
:hidden:
:caption: Get started
:maxdepth: 2

notes/README_ENVIRONMENT
quickstart
```

```{toctree}
:hidden:
:caption: Pipeline
:maxdepth: 2

notes/workflow_guide
notes/configuration_guide
```
