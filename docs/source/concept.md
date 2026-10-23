# Concept

<p class="page-intro">
A battery or a reservoir is only useful because of what happened before: what it can give
tonight depends on how much it stored this afternoon. Energy planning models save time by
simulating a few typical days instead of the whole year, and in doing so they can lose that link
between hours and days. This section explains the problem in plain terms and introduces the
four ways of modelling storage that the study compares.
</p>

<div class="section-cards">
  <a class="section-card section-card--concept" href="notes/about_storage_algorithms.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">Start here</span>
    </span>
    <span class="section-card__title">Why storage is hard to model</span>
    <span class="section-card__text">Storage moves energy across time, needs continuity and interacts with the rest of the system. Explained with everyday analogies.</span>
    <span class="section-card__more">Read the explainer →</span>
  </a>
  <a class="section-card section-card--layers" href="notes/model_specifications.html">
    <span class="section-card__head">
      <span class="section-card__icon" aria-hidden="true"></span>
      <span class="section-card__step">Details</span>
    </span>
    <span class="section-card__title">Model specifications</span>
    <span class="section-card__text">How the models sit on top of OSeMOSYS: storage parameters, constraints and model files.</span>
    <span class="section-card__more">See the specifications →</span>
  </a>
</div>

## How the study is put together

The study runs one small test system through OSeMOSYS with each of the four storage methods and
compares the results with a full-year hourly benchmark. Each block below opens with the details
and the limitations stated in the paper; **Storage method** opens the four formulations side by
side.

```{raw} html
:file: _static/study-workflow.html
```

```{toctree}
:hidden:
:maxdepth: 2

notes/about_storage_algorithms
notes/model_specifications
```
