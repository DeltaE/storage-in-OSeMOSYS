# About Storage Modelling
Storage modeling is complex because storage systems behave differently than generation or demand. __Storages move energy across time, not just produce or consume it__. This means:

```{warning}
This library is under active development and some of the contents are not displayed as a requirement for the publication process of the paper. Complete content will be available after the publication.
```

__🔁 1. Storage shifts energy in time__

Unlike solar panels (generate) or homes (consume), storage stores energy when it’s abundant and releases it when needed. That means:
  - You can't look at one hour in isolation — what happened before matters.
  - The state of charge (SOC) today depends on all previous hours.

    > Analogy: It's like a savings account — what you can spend today depends on how much you saved earlier.

__⏳ 2. Time resolution matters__

Should you model every single hour? Every day? A few representative days? Each choice impacts:

 - Accuracy (high resolution = realistic, but slow to compute)
 - Computational effort (simplified models lose detail)

    > If you model storage with only a few sample days, you risk missing important patterns, like a long wind lull or weekend charging habits.

__🔗 3. Storage needs continuity__

Many simplification techniques (e.g. clustering days) break the continuity of storage:

 - The model might forget how full the battery was yesterday.
 - Artificial resets can distort when charging/discharging actually happens.

This makes it tricky to model seasonal storage or multi-day balancing.

__⚡ 4. Storage interacts with everything__
Storage isn’t just an isolated battery:

 - It interacts with renewables (absorbing variability)
 - It supports grid reliability (fast response)
 - It responds to prices, constraints, and emissions goals

So modeling it well requires integrating with the rest of the energy system.

## state of the art __energy storage algorithms__:

### Niet (Direct Link) — “Continuous Diary”
- __Analogy__: Imagine someone writes in their diary every hour without skipping, and each day picks up exactly where the last one left off. The emotional ups and downs (mood swings) are smooth and continuous over the week.

- __Key idea__: Full hourly resolution; perfect continuity over time.
- __Use case__: Most accurate but data-heavy.

### Welsch (Fixed-Pattern) — “Photocopied Day”
- __Analogy__: This person writes down one typical day of feelings and then photocopies that same page for each day of the week. So Monday, Tuesday, etc., look exactly the same.

- __Key idea__: Same daily pattern repeated; no inter-day variation.
- __Use case__: Fast and simple but ignores variation between days.


### Kotzur (Unverified Cluster) — “Alternating Diaries”
- __Analogy__: This person has two types of days — maybe “busy” and “lazy” days — and alternates between those two. They use pre-written diary templates for each. But they don’t bother connecting one day’s feelings to the next, so it can feel jumpy or inconsistent.

- __Key idea__: Captures daily diversity using clusters, but no continuity.
- __Use case__: Captures more variety than Welsch but lacks smooth transitions.

### Novo (Hourly-Verified) — “Linked Journaling”
- __Analogy__: This person still uses simplified mood templates for different kinds of days, but they always make sure each day starts where the previous one left off. So it feels realistic and connected, even if it's not a full diary.

- __Key idea__: Combines typical days with continuity between hours.
- __Use case__: A practical middle ground between realism and simplicity.

