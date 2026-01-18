# Civil Engineering Context Library
**Last Updated**: 2026-01-17
**Purpose**: Reusable Civil Engineering scenarios for consistent examples across all chapters

---

## 📋 Overview

This library provides **realistic Civil Engineering contexts** for use in curriculum examples. Instead of generic scenarios (chatbots, movie reviews), all chapters should use these CE-specific scenarios to maintain domain focus and build toward the final CE Document Generation System.

**Benefits**:
- ✅ Consistency across all 54 chapters
- ✅ Realistic CE context (students building for their field)
- ✅ Direct transfer to final project (Ch 54)
- ✅ Motivation maintenance (building MY system, not generic tutorial)

---

## 🏗️ Structural Analysis Scenarios

### Scenario 1: Bridge Load Calculation
**Context**: 50m span bridge, 40-tonne design load, steel girder construction

**Specifications**:
- **Location**: Urban highway crossing
- **Span**: 50 meters
- **Design Load**: 40 tonnes (live load) + dead load
- **Material**: High-strength steel (Grade 50)
- **Codes**: AASHTO LRFD Bridge Design, ASCE 7

**Use In Chapters**:
- Ch 7: LLM summarizes bridge analysis reports
- Ch 8: Multi-provider query for load calculations
- Ch 9: Prompt templates for structural analysis questions
- Ch 13-17: RAG system queries bridge design documents
- Ch 54: Generate bridge specifications from requirements

**Example Documents**:
- `bridge_analysis_report.pdf` (30 pages, structural calculations)
- `bridge_load_calcs.xlsx` (spreadsheet with load combinations)
- `bridge_drawings.dwg` (CAD files with annotations)

**Sample Query**:
> "What is the maximum bending moment at mid-span under AASHTO HL-93 loading?"

---

### Scenario 2: Foundation Design
**Context**: High-rise building, 500kN column load, clay soil conditions

**Specifications**:
- **Building**: 12-story office building
- **Column Load**: 500 kN axial load
- **Soil**: Medium clay (cu = 75 kPa, γ = 18 kN/m³)
- **Foundation Type**: Spread footing or pile foundation
- **Codes**: ACI 318 (concrete design), Terzaghi bearing capacity

**Use In Chapters**:
- Ch 7: Summarize geotechnical reports
- Ch 13-17: Semantic search across foundation design documents
- Ch 54: Generate foundation specifications from soil reports

**Example Documents**:
- `geotechnical_report.pdf` (soil boring logs, lab test results)
- `foundation_design_calcs.pdf` (bearing capacity, settlement analysis)
- `foundation_drawings.dwg` (plan and section views)

**Sample Query**:
> "What is the required footing size for a 500kN column load on medium clay with cu = 75 kPa?"

---

### Scenario 3: Retaining Wall Design
**Context**: 6m tall retaining wall, backfill with surcharge load

**Specifications**:
- **Height**: 6 meters
- **Backfill**: Sandy soil (φ = 32°, γ = 19 kN/m³)
- **Surcharge**: 10 kPa uniform load
- **Wall Type**: Cantilever reinforced concrete
- **Codes**: ACI 318, Rankine earth pressure theory

**Use In Chapters**:
- Ch 9: Prompt engineering for earth pressure calculations
- Ch 13-17: Retrieve similar retaining wall designs
- Ch 54: Generate retaining wall specifications

**Example Documents**:
- `retaining_wall_design.pdf` (calculations, stability checks)
- `wall_reinforcement_details.dwg` (reinforcement layout)

**Sample Query**:
> "Calculate the lateral earth pressure on a 6m cantilever wall retaining sandy soil with a 10 kPa surcharge."

---

## 📄 Document Types

### Type 1: Structural Analysis Report
**Format**: PDF, 30-50 pages

**Sections**:
1. **Executive Summary** (1-2 pages)
   - Project overview
   - Key findings
   - Recommendations

2. **Load Analysis** (10-15 pages)
   - Dead loads
   - Live loads
   - Load combinations per ASCE 7

3. **Structural Calculations** (15-20 pages)
   - Member sizing
   - Stress analysis
   - Deflection checks

4. **Code Compliance** (5-10 pages)
   - ASCE 7 compliance verification
   - ACI 318 / AISC 360 checks
   - Safety factors

5. **Appendices**
   - Calculation sheets
   - Reference documents

**Use In Chapters**:
- Ch 7: First LLM call (summarize report)
- Ch 9: Prompt engineering (extract key findings)
- Ch 13: Generate embeddings for semantic search
- Ch 16: Document loaders (parse PDF structure)
- Ch 17: RAG system (query specific sections)
- Ch 54: Full system integration

**Example Filename**: `bridge_structural_analysis_2024.pdf`

---

### Type 2: Geotechnical Investigation Report
**Format**: PDF, 20-40 pages

**Sections**:
1. **Site Description**
   - Location
   - Existing conditions
   - Scope of work

2. **Subsurface Conditions**
   - Soil boring logs
   - Groundwater levels
   - Soil stratigraphy

3. **Laboratory Test Results**
   - Grain size distribution
   - Atterberg limits
   - Shear strength (triaxial, direct shear)
   - Consolidation tests

4. **Engineering Analysis**
   - Bearing capacity
   - Settlement estimates
   - Slope stability

5. **Recommendations**
   - Foundation type
   - Design parameters
   - Construction considerations

**Use In Chapters**:
- Ch 7-9: LLM querying for soil properties
- Ch 13-17: Semantic search across soil data
- Ch 54: Generate foundation specs from geotech reports

**Example Filename**: `geotech_investigation_highrise_2024.pdf`

---

### Type 3: CAD Drawing Annotations
**Format**: DXF/DWG with text annotations

**Content Types**:
- **Dimensions**: Member sizes, spacing, elevations
- **Material Specifications**: Grade 50 steel, 4000 psi concrete
- **Construction Notes**: "Weld per AWS D1.1", "Anchor to existing structure"
- **Reference Callouts**: "See Detail 3/A5.1"

**Use In Chapters**:
- Ch 16: Document loaders (parse CAD text entities)
- Ch 23-30: Agents extract structured data from drawings
- Ch 54: System ingests CAD files for analysis

**Example Filename**: `bridge_structural_drawings_S1.dwg`

---

### Type 4: Building Code Excerpts
**Format**: PDF or plain text

**Codes Included**:
- **ACI 318**: Concrete design
- **AISC 360**: Steel design
- **ASCE 7**: Loads and load combinations
- **IBC**: International Building Code
- **AASHTO LRFD**: Bridge design

**Use In Chapters**:
- Ch 7-9: LLM answers code compliance questions
- Ch 13-17: RAG retrieves relevant code sections
- Ch 54: System ensures code compliance

**Example Filename**: `ACI318-19_Chapter9_Strength_and_Serviceability.pdf`

---

## 🎯 Project Types

### Project 1: Highway Bridge Rehabilitation
**Description**: Upgrade existing 40-year-old bridge to modern load standards

**Requirements**:
- Structural assessment of existing conditions
- Load rating analysis
- Retrofit design for increased capacity
- Temporary traffic management plan

**Deliverables**:
- Structural assessment report
- Load rating calculations
- Retrofit drawings and specifications
- Construction cost estimate

**Use In Chapters**:
- Ch 17: RAG system generates assessment report
- Ch 54: Full document generation from site inspection data

---

### Project 2: High-Rise Building Foundation
**Description**: Design deep foundation for 30-story building on soft clay

**Requirements**:
- Geotechnical investigation review
- Pile capacity calculations
- Settlement analysis
- Pile layout and details

**Deliverables**:
- Foundation design report
- Pile capacity calculations
- Foundation drawings
- Construction specifications

**Use In Chapters**:
- Ch 13-17: RAG queries similar foundation projects
- Ch 54: Generate foundation design from geotech report

---

### Project 3: Retaining Wall for Hillside Development
**Description**: Design cantilever wall to support 6m height difference

**Requirements**:
- Earth pressure calculations
- Stability analysis (overturning, sliding, bearing)
- Reinforced concrete design
- Drainage system design

**Deliverables**:
- Retaining wall design calculations
- Structural drawings
- Material specifications
- Construction sequence

**Use In Chapters**:
- Ch 9: Prompt templates for wall design
- Ch 54: Full wall design automation

---

## 🔧 Material Specifications

### Concrete
**Common Grades**:
- `f'c = 3000 psi` (20.7 MPa) - Residential foundations
- `f'c = 4000 psi` (27.6 MPa) - Commercial structures
- `f'c = 5000 psi` (34.5 MPa) - High-strength applications

**Properties**:
- Density: 150 pcf (23.6 kN/m³)
- Modulus of Elasticity: 57,000√f'c (psi units)
- Poisson's Ratio: 0.15 - 0.20

---

### Steel
**Common Grades**:
- **Rebar**: Grade 60 (fy = 60 ksi)
- **Structural Steel**:
  - A36 (Fy = 36 ksi) - general purpose
  - A572 Grade 50 (Fy = 50 ksi) - high strength
  - A992 (Fy = 50 ksi) - wide flange beams

**Properties**:
- Density: 490 pcf (77 kN/m³)
- Modulus of Elasticity: 29,000 ksi (200 GPa)
- Poisson's Ratio: 0.30

---

### Soil Properties (For Foundation Design)
**Clay**:
- Soft: cu = 12-25 kPa
- Medium: cu = 25-50 kPa
- Stiff: cu = 50-100 kPa
- Very Stiff: cu = 100-200 kPa

**Sand**:
- Loose: φ = 28-30°
- Medium Dense: φ = 30-35°
- Dense: φ = 35-40°

---

## 📊 Load Combinations (ASCE 7)

### Basic Combinations
**LRFD (Load and Resistance Factor Design)**:
1. `1.4D`
2. `1.2D + 1.6L + 0.5(Lr or S or R)`
3. `1.2D + 1.6(Lr or S or R) + (L or 0.5W)`
4. `1.2D + 1.0W + L + 0.5(Lr or S or R)`
5. `1.2D + 1.0E + L + 0.2S`
6. `0.9D + 1.0W`
7. `0.9D + 1.0E`

**Where**:
- `D` = Dead load
- `L` = Live load
- `Lr` = Roof live load
- `S` = Snow load
- `R` = Rain load
- `W` = Wind load
- `E` = Earthquake load

**Use In Chapters**:
- Ch 7-9: LLM calculates governing load combination
- Ch 54: System applies code-compliant load combinations

---

## 💬 Sample Queries by Chapter

### Chapter 7: Your First LLM Call
**Query**: "Summarize the structural analysis report for the 50m bridge project."

**Expected Response**:
> The bridge analysis report evaluates a 50-meter span steel girder bridge under AASHTO HL-93 loading. The maximum bending moment is 3,450 kN-m at mid-span. All members meet AISC 360 design criteria with a safety factor of 1.67. Live load deflection is L/820, well within the L/800 limit. The report recommends Grade 50 steel for primary girders with 4000 psi concrete deck.

---

### Chapter 9: Prompt Engineering
**Prompt Template**:
```
You are a structural engineer analyzing {structure_type} designs.

Review the following calculations and verify compliance with {code_reference}:

{calculation_data}

Provide:
1. Code compliance status (pass/fail)
2. Critical findings
3. Recommendations for design optimization
```

---

### Chapter 13-17: RAG System
**Query**: "Find all bridge projects with span greater than 40m and design load over 35 tonnes."

**Expected Results**:
- Document 1: Highway Bridge A50 (50m, 40T)
- Document 2: Railway Bridge B23 (45m, 60T)
- Document 3: Pedestrian Bridge C12 (42m, 15T - excluded, load too low)

---

## 🔄 Naming Conventions

### Documents
**Pattern**: `{project}_{document_type}_{version}_{date}.ext`

**Examples**:
- `bridge_a50_structural_analysis_v2_2024-03-15.pdf`
- `highrise_foundation_design_v1_2024-01-20.pdf`
- `retaining_wall_calculations_v3_2024-02-10.xlsx`

### Components (From Project Thread)
**Pattern**: `CE{Component Name}`

**Examples**:
- `CEConfigManager` (Ch 6A)
- `CEDocumentSummarizer` (Ch 7)
- `CEPromptTemplateManager` (Ch 9)
- `CERAGPipeline` (Ch 17)

---

## ✅ Usage Guidelines

### For Curriculum Authors

**When Creating Examples**:
1. ✅ Choose scenario from this library
2. ✅ Use consistent naming conventions
3. ✅ Reference actual codes (ACI 318, ASCE 7, etc.)
4. ✅ Include realistic numbers and units
5. ✅ Show complete workflow (not just fragments)

**Don't**:
- ❌ Use generic chatbot examples
- ❌ Use movie/restaurant recommendation examples
- ❌ Make up unrealistic structural scenarios
- ❌ Skip code references

### For Students

**Benefits of CE-Focused Examples**:
- Every example applies directly to your field
- Skills transfer immediately to real projects
- Portfolio of CE-specific code samples
- No "translation" needed from generic to CE

---

## 📚 Reference Documents (Simulated)

These documents exist in the simulated project structure and can be referenced in chapters:

```
curriculum/
  sample_documents/
    bridge/
      bridge_a50_structural_analysis.pdf
      bridge_load_calculations.xlsx
      bridge_drawings_S1.dwg
    foundation/
      geotech_investigation_highrise.pdf
      foundation_design_calculations.pdf
      pile_layout_drawings.dwg
    codes/
      ACI318-19_excerpts.pdf
      ASCE7-22_load_combinations.pdf
      AISC360-16_steel_design.pdf
```

**Note**: Actual files are not included in repository. Students simulate document processing with text representations.

---

## 🚀 Expansion

As curriculum grows, add new scenarios:
- **Water Resources**: Dam design, stormwater management
- **Transportation**: Pavement design, traffic analysis
- **Environmental**: Site remediation, erosion control
- **Construction Management**: Scheduling, cost estimation

Each new scenario should follow the same structure:
1. Context (what is being designed)
2. Specifications (dimensions, loads, materials)
3. Codes (relevant standards)
4. Use in chapters (where it's referenced)
5. Example documents (simulated files)

---

**End of CE Context Library**

**Usage**: Reference this file when creating chapter examples to ensure consistency and CE domain relevance across the entire curriculum.
