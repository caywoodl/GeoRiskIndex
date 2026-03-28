# GeoRiskIndex
# Permafrost Carbon Risk & Remobilization Analysis

This repository contains Python workflows for constructing a **geological permafrost carbon risk index** and evaluating the spatial relationship between **high-risk permafrost zones** and **Yedoma deposits** in the **North Slope Borough, Alaska**.

The project integrates permafrost data, soil carbon inventories, and environmental variables to quantify **carbon pool vulnerability** and the **potential for remobilization under future climate conditions**.

---

## Overview

Permafrost carbon release depends on both **environmental vulnerability** and **carbon availability**. This repository provides tools to:

- Build a **multi-factor permafrost carbon risk index**  
- Identify **high-risk zones** where vulnerable conditions and carbon storage overlap  
- Evaluate spatial alignment with **Yedoma (ice-rich permafrost)**  
- Test statistical significance using **spatial permutation methods**

---

## Methods Summary

### 1. Environmental Indices

All variables are normalized (0–1) and combined into sub-indices:

- **Carbon Storage Index**  
  Derived from NCSCDv2 carbon stocks across multiple depths and cryogenic carbon pools  

- **Ground Vulnerability Index**  
  Based on permafrost extent, ground-ice content, and terrain characteristics  

- **Soil Vulnerability Index**  
  Represents soil composition and permafrost-associated soil types  

- **Active Layer Thickness (ALT)**  
  Derived from NASA ABoVE  

- **Soil Moisture Index**  
  Weighted combination of SoilGrids volumetric water content at multiple depths  

---

### 2. Geological Permafrost Carbon Risk Index

A composite index is constructed using weighted spatial overlay:

- Carbon Storage: 0.30  
- Ground Vulnerability: 0.25  
- Soil Vulnerability: 0.20  
- Active Layer Thickness: 0.15  
- Soil Moisture: 0.10  

This index represents areas where **high carbon availability coincides with favorable thaw conditions**, indicating elevated risk of carbon remobilization.

---

### 3. Spatial Overlap & Hypothesis Testing

High-risk areas are compared with mapped **Yedoma deposits**.

A **toroidal shift permutation test** is used to evaluate whether the observed overlap exceeds random expectation while preserving spatial structure.

---

## Study Area

North Slope Borough, Alaska

---

## Data Sources

- **NASA ABoVE** – Active Layer Thickness (ALT)  
- **GTN-P** – Permafrost borehole temperature data  
- **NCSCDv2** – Soil carbon stocks and soil classifications  
- **SoilGrids** – Soil moisture and physical properties  
- **Circum-Arctic Permafrost Map (IPA)** – Ground-ice and permafrost extent  
- **IRYP v2** – Yedoma domain and confidence layers  
- **GRACE / GRACE-FO / GLDAS / SMAP** – Hydrology  
- **OCO-2** – Atmospheric CO₂ fluxes  

---

## Workflow

1. Preprocess and align all datasets to a common projection and resolution  
2. Normalize environmental variables (0–1 scale)  
3. Construct sub-indices (carbon, soil, ground, moisture, ALT)  
4. Build composite geological risk index  
5. Identify high-risk areas  
6. Overlay with Yedoma domain  
7. Perform permutation-based hypothesis testing  

---

## Repository Structure
