# About Storage Modelling
Storage modeling is complex because storage systems behave differently than generation or demand. __Storages move energy across time, not just produce or consume it__. This means:

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


Quick Summary on Storage Algorithms in Modelling : 
---
| Algorithm | Analogy                        | Continuity | Variety | Simplicity | Use Case                                               |
|-----------|-------------------------------|:----------:|:-------:|:----------:|--------------------------------------------------------|
| Niet      | Full continuous diary          | ✅         | ✅      | ❌         | Most accurate but data-heavy                           |
| Welsch    | Same page copied every day     | ❌         | ❌      | ✅✅        | Fast and simple but ignores variation between days     |
| Kotzur    | Alternating mood templates     | ❌         | ✅      | ✅         | Captures more variety than Welsch but lacks transitions|
| Novo      | Linked mood templates          | ✅         | ✅      | ✅         | Practical middle ground between realism and simplicity |



A detailed comparison:

### 📊 Comparative Table of Storage Modeling Methods

| Feature                              | **Niet**                          | **Welsch**                             | **Kotzur**                       | **Novo**                  |
|--------------------------------------|--------------------------------------------------|---------------------------------------------------------|-----------------------------------------------------------|---------------------------------------------------------|
| Period Linking                              | Direct Link                        | Enhanced Periods (Fixed Pattern)                           | Enhanced Periods (Day Cluster Mapping)                       | Enhanced Periods (Hourly-Verified Clustering)                 |
| **Time Representation**             | Representative periods (e.g. days, weeks)       | Representative **days** (fixed mapping)                | Representative **days** (arbitrary sequence allowed)      | Full **hourly resolution** mapped to rep days          |
| **Chronological Continuity**        | ✅ Maintained between periods                    | ❌ Not maintained (days are independent)               | ✅ Maintained via day-sequence mapping                    | ✅ Maintained at hourly level                          |
| **SoC Linkage Between Periods**     | ✅ Explicit (stepwise linkage)                   | ❌ No linkage; each rep day repeats independently       | ✅ Daily SoC updated using mapped intra-day values        | ✅ Fully verified SoC with hourly mapping              |
| **Intra-Day Resolution**            | Average or period-level                         | Full 24-hour profile (rep day)                         | Full 24-hour profile (rep day)                            | Full 24-hour profile (mapped to full year)            |
| **Reset or Loop Behavior**          | None; sequential linkage                        | Yes; rep day is **repeated** N times                   | Resets daily but allows **arbitrary day ordering**        | No reset; each hour is **mapped and verified**         |
| **Flexibility in Time Sequencing**  | Low (predefined order of rep periods)           | Very low (repeats identical rep day pattern)           | High (any chronological day can map to any rep day)       | Very high (full hourly reconstruction)                 |
| **Computational Cost**              | Low (simple stepwise link across periods)       | Very low (repeats rep day)                             | Medium (needs intra-day dynamics + daily tracking)        | High (full hourly SoC tracking and bounds checking)    |
| **Storage Bounds Verification**     | Implicit per period                             | Start/End of rep day only                              | Only for intra-day cycles; inter-day bounds ignored       | ✅ Enforced at each hour                              |
| **Use Case**                        | Fast approximation with minimal memory effects  | Simple seasonal or weekday/weekend modeling            | Captures non-repetitive variation (e.g. windless days)    | High-fidelity operational modeling (e.g., reliability) |
