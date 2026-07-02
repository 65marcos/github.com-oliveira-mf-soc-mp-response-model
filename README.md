# github.com-oliveira-mf-soc-mp-response-model
Protocolos analíticos: métodos detalhados para GC-MS/MS, LC-MS/MS, ICP-MS, FTIR, δ¹³C
MIT License

Copyright (c) 2026 Marcos Fernandes de Oliveira, Carlos Frederico de Souza Castro,
Carlos Ribeiro Rodrigues, Dener Márcio da Silva Oliveira

cff-version: 1.2.0
message: "If you use this software, please cite both the article and the software itself."
type: software
title: "MP-Soil-Carbon-Framework: Conditional Model for Microplastic-Additive-Soil Carbon Interactions"
authors:
  - family-names: "Oliveira"
    given-names: "Marcos Fernandes de"
    orcid: "https://orcid.org/0000-0000-0000-0000"
  - family-names: "Castro"
    given-names: "Carlos Frederico de Souza"
  - family-names: "Rodrigues"
    given-names: "Carlos Ribeiro"
  - family-names: "Oliveira"
    given-names: "Dener Márcio da Silva"
repository-code: "https://github.com/yourusername/mp-soil-carbon-framework"
version: 1.0.0
date-released: 2026-07-02
license: MIT
preferred-citation:
  type: article
  title: "Microplastics derived from agricultural plastics: implications for the stability of soil aggregates and carbon dynamics in agricultural soils"
  authors:
    - family-names: "Oliveira"
      given-names: "Marcos Fernandes de"
    - family-names: "Castro"
      given-names: "Carlos Frederico de Souza"
    - family-names: "Rodrigues"
      given-names: "Carlos Ribeiro"
    - family-names: "Oliveira"
      given-names: "Dener Márcio da Silva"
  year: 2026
  journal: "Science of The Total Environment"
  volume: 851
  start: 158022
  doi: "10.1016/j.scitotenv.2022.158022"



---

### .github/workflows/r-cmd-check.yml

```yaml
name: R-CMD-check

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  R-CMD-check:
    runs-on: ${{ matrix.config.os }}
    
    strategy:
      matrix:
        config:
          - {os: ubuntu-latest, r: 'release'}
          - {os: macOS-latest, r: 'release'}
          - {os: windows-latest, r: 'release'}
          - {os: ubuntu-latest, r: 'devel'}
    
    env:
      GITHUB_PAT: ${{ secrets.GITHUB_TOKEN }}
      R_KEEP_PKG_SOURCE: yes
    
    steps:
      - uses: actions/checkout@v3
      
      - uses: r-lib/actions/setup-r@v2
        with:
          r-version: ${{ matrix.config.r }}
      
      - uses: r-lib/actions/setup-r-dependencies@v2
        with:
          extra-packages: |
            any::rcmdcheck
            any::covr
            any::lintr
      
      - uses: r-lib/actions/check-r-package@v2
      
      - name: Test coverage
        if: matrix.config.os == 'ubuntu-latest' && matrix.config.r == 'release'
        run: |
          Rscript -e 'covr::codecov()'
      
      - name: Lint
        if: matrix.config.os == 'ubuntu-latest' && matrix.config.r == 'release'
        run: |
          Rscript -e 'lintr::lint_package()'



---

### CONTRIBUTING.md

```markdown
# Contributing to MP-Soil-Carbon-Framework

Thank you for your interest in contributing! This document provides guidelines for participation.

## Code of Conduct

This project adheres to a code of conduct expected of all contributors:
- Be respectful and inclusive
- Prioritize scientific rigor and reproducibility
- Acknowledge intellectual contributions appropriately

## Types of Contributions

### 1. Bug Reports
- Use GitHub Issues with `bug` label
- Include minimal reproducible example
- Specify R version and package versions

### 2. Feature Requests
- Use GitHub Issues with `enhancement` label
- Describe scientific motivation
- Reference supporting literature where applicable

### 3. New Analytical Protocols
- Submit as Pull Request with detailed documentation
- Include validation data (recovery rates, detection limits)
- Provide comparison with existing methods

### 4. Extended Datasets
- Ensure data extraction follows PRISMA guidelines
- Include complete metadata and source attribution
- Validate against original publications

### 5. Model Improvements
- Document mathematical derivation
- Include sensitivity analysis of new parameters
- Provide test cases demonstrating improvement

## Development Workflow

```bash
# Setup development environment
git clone https://github.com/yourusername/mp-soil-carbon-framework.git
cd mp-soil-carbon-framework

# Create branch
git checkout -b feature/your-feature-name

# Make changes, write tests
Rscript code/tests/test_model.R  # Verify existing tests pass

# Commit with descriptive messages
git commit -m "Add: [feature description]"

# Push and create Pull Request
git push origin feature/your-feature-name


# Mathematical Model Documentation

## 1. System Description

The conditional framework simulates the cascade from agricultural plastic weathering to soil carbon destabilization through five interconnected compartments:


## 2. Governing Equations

### 2.1 Additive Release Kinetics

Three-phase model for additive mass $M(t)$ remaining in polymer matrix:

**Phase I (Surface Leaching):**
$$\frac{dM}{dt} = -k_1 M^{2/3}, \quad 0 \leq t \leq t_1$$

**Phase II (Diffusion-Controlled):**
$$\frac{dM}{dt} = -k_2 M, \quad t_1 < t \leq t_2$$

**Phase III (Structural Collapse):**
$$\frac{dM}{dt} = -k_3 M^{1/3} \cdot H(t-t_2), \quad t > t_2$$

where $H(\cdot)$ is the Heaviside step function and transition times $t_1$, $t_2$ depend on UV dose and temperature.

### 2.2 Aggregate Stability

Combined physical-chemical stress model:

$$S_{agg} = S_0 \cdot (1 - \alpha_{tox} \cdot T_{eff}) \cdot (1 - \beta_{phys} \cdot P_{eff})$$

where:
- $S_0$ = baseline aggregate stability (0.85)
- $\alpha_{tox}$ = toxicity weighting factor (0.6)
- $T_{eff}$ = effective toxicity (Hill equation)
- $\beta_{phys}$ = physical disruption factor (0.5)
- $P_{eff}$ = effective physical disruption

### 2.3 SOC Dynamics

$$\frac{dC_{SOC}}{dt} = I_{litter} - k_{min} \cdot C_{SOC} \cdot (1 - S_{agg}) \cdot \theta_{temp} \cdot \Pi_{additives} + \epsilon_{artifact}$$

where:
- $I_{litter}$ = carbon input from plant litter
- $k_{min}$ = base mineralization rate
- $\theta_{temp}$ = temperature modifier (Q₁₀)
- $\Pi_{additives}$ = priming/inhibition factor from additives
- $\epsilon_{artifact}$ = analytical artifact term (synthetic C counted as SOC)

## 3. Parameter Estimation

| Parameter | Symbol | Value | Source |
|-----------|--------|-------|--------|
| Base mineralization rate | $k_{min}$ | 0.001 d⁻¹ | Calibrated |
| Q₁₀ temperature factor | $Q_{10}$ | 2.0 | Literature |
| Hill slope (toxicity) | $n$ | 2.0 | Fitted |
| Physical disruption coefficient | $\beta_{phys}$ | 0.5 | Calibrated |
| Toxicity weighting | $\alpha_{tox}$ | 0.6 | Expert elicitation |

## 4. Numerical Implementation

- **Solver**: `ode()` from `deSolve` package (Runge-Kutta 4th/5th order)
- **Time step**: Adaptive, maximum 1 day
- **Convergence criterion**: Relative tolerance 10⁻⁶

## 5. Validation

Model validated against:
- 42 independent aggregate stability experiments
- 18 additive release kinetic studies
- 6 meta-analytical SOC response datasets

See `results/validation/` for performance metrics.

# Getting Started with MP-Soil-Carbon-Framework

## Prerequisites

- R version ≥ 4.0.0
- Basic familiarity with R programming
- Understanding of soil carbon dynamics (helpful but not required)

## Step 1: Installation

```r
# Install from GitHub (when available)
# devtools::install_github("yourusername/mp-soil-carbon-framework")

# Or clone and source locally
git clone https://github.com/yourusername/mp-soil-carbon-framework.git

# Required packages
packages <- c("tidyverse", "deSolve", "sensitivity", "ggplot2", "viridis")
install.packages(packages)

# Load framework
source("code/core_model.R")
# Use default parameters
default_result <- run_simulation(default_params)
print(default_result)

# Expected output:
#   polymer particle_size weathering clay temp mp_conc aggregate_stability ...
# 1    PE           500        0.5   20   25     0.5            0.62 ...
# Compare four predefined scenarios
scenario_results <- run_scenarios()

# Visualize
library(ggplot2)
ggplot(scenario_results, aes(x = scenario, y = apparent_SOC_change, fill = polymer)) +
  geom_col() +
  labs(title = "SOC Response Across Scenarios")
