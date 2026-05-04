# Published Artifact Correspondence

The published article and online supplement are the source of truth. This checklist records which repo entrypoint currently regenerates each item and whether parity has been checked.

Publication: https://www.sciencedirect.com/science/article/pii/S0899825624000307?via%3Dihub

| Artifact | Script source | Generated output | Status |
| --- | --- | --- | --- |
| Main Table 2 | `src/analysis/tables_main.do` | `outputs/tables/main_tables_results.csv` | matched against published notebook output |
| Main Table 3 | `src/analysis/tables_main.do` | `outputs/tables/main_tables_results.csv` | matched against published notebook output |
| Main Table 4 | `src/analysis/tables_main.do` | `outputs/tables/main_tables_results.csv` | numeric check implemented |
| Main Figure 2 | `src/analysis/figures.py` | `outputs/figures/main_fig_2_chosen_effort.png` | regenerated; visual parity check pending |
| Main Figure 3 | `src/analysis/figures.py` | `outputs/figures/main_fig_3_wage_comparisons.png` | regenerated; visual parity check pending |
| Main Figure 4 | `src/analysis/figures.py` | `outputs/figures/main_fig_4_chosen_expected_effort.png` | regenerated; visual parity check pending |
| Supplement Table A.1 | `src/analysis/tables_appendix.py` | `outputs/tables/appendix_table_a1_summary_statistics.csv` | numeric checks implemented |
| Supplement Tables A.2-A.3 | `src/analysis/tables_appendix.do` | `outputs/tables/appendix_tables_results.csv` | numeric checks implemented for representative published coefficients |
| Supplement Tables A.4-A.9 | `src/analysis/tables_appendix.do` | `outputs/tables/appendix_tables_results.csv` | numeric checks implemented for representative published coefficients |
| Supplement Figure A.1 | `src/analysis/figures.py` | `outputs/figures/supp_fig_a1_acceptance_wage.png` | regenerated; visual parity check pending |
| Supplement Figure A.2 | `src/analysis/figures.py` | `outputs/figures/supp_fig_a2_chosen_effort_all.png` | regenerated; visual parity check pending |
| Supplement Figure A.3 | `src/analysis/figures.py` | `outputs/figures/supp_fig_a3_wage_comparisons_all.png` | regenerated; visual parity check pending |
| Supplement Figure A.4 | `src/analysis/figures.py` | `outputs/figures/supp_fig_a4_beliefs_based_profitmax_wage.png` | regenerated; visual parity check pending |
| Supplement Figure A.5 | `src/analysis/figures.py` | `outputs/figures/supp_fig_a5_individual_effort_ge.png` | regenerated; visual parity check pending |
| Supplement Figure A.6 | `src/analysis/figures.py` | `outputs/figures/supp_fig_a6_individual_effort_prosocial.png` | regenerated; visual parity check pending |
| Supplement Figure A.7 | `src/analysis/figures.py` | `outputs/figures/supp_fig_a7_individual_effort_neutral.png` | regenerated; visual parity check pending |
| Supplement Figure A.8 | `src/analysis/figures.py` | `outputs/figures/supp_fig_a8_individual_effort_efficiency.png` | regenerated; visual parity check pending |
