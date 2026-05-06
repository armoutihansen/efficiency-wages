from __future__ import annotations

from dataclasses import dataclass

from src.replication_paths import OUTPUTS


@dataclass(frozen=True)
class Artifact:
    paper_artifact: str
    source: str
    output: str
    status: str


ARTIFACTS = [
    Artifact("Main Table 2", "src/analysis/tables_main.do", "results/paper/tables/table_2_acceptance.tex", "generated"),
    Artifact("Main Table 3", "src/analysis/tables_main.do", "results/paper/tables/table_3_effort.tex", "generated"),
    Artifact("Main Table 4", "src/analysis/tables_main.do", "results/paper/tables/table_4_wage_offers.tex", "generated"),
    Artifact("Main Figure 2", "src/analysis/figures.py", "results/paper/figures/main_fig_2_chosen_effort.png", "generated"),
    Artifact("Main Figure 3", "src/analysis/figures.py", "results/paper/figures/main_fig_3_wage_comparisons.png", "generated"),
    Artifact("Main Figure 4", "src/analysis/figures.py", "results/paper/figures/main_fig_4_chosen_expected_effort.png", "generated"),
    Artifact("Supplement Table A.1", "src/analysis/tables_appendix.py", "results/appendix/tables/table_a1_summary_statistics.tex", "generated"),
    Artifact("Supplement Table A.2", "src/analysis/tables_appendix.do", "results/appendix/tables/table_a2_effort_ge_prosocial.tex", "generated"),
    Artifact("Supplement Table A.3", "src/analysis/tables_appendix.do", "results/appendix/tables/table_a3_effort_neutral_efficiency.tex", "generated"),
    Artifact("Supplement Table A.4", "src/analysis/tables_appendix.do", "results/appendix/tables/table_a4_acceptance_neutral.tex", "generated"),
    Artifact("Supplement Table A.5", "src/analysis/tables_appendix.do", "results/appendix/tables/table_a5_acceptance_efficiency.tex", "generated"),
    Artifact("Supplement Table A.6", "src/analysis/tables_appendix.do", "results/appendix/tables/table_a6_effort_neutral.tex", "generated"),
    Artifact("Supplement Table A.7", "src/analysis/tables_appendix.do", "results/appendix/tables/table_a7_effort_efficiency.tex", "generated"),
    Artifact("Supplement Table A.8", "src/analysis/tables_appendix.do", "results/appendix/tables/table_a8_wage_offers_neutral.tex", "generated"),
    Artifact("Supplement Table A.9", "src/analysis/tables_appendix.do", "results/appendix/tables/table_a9_wage_offers_efficiency.tex", "generated"),
    Artifact("Supplement Figure A.1", "src/analysis/figures.py", "results/appendix/figures/supp_fig_a1_acceptance_wage.png", "generated"),
    Artifact("Supplement Figure A.2", "src/analysis/figures.py", "results/appendix/figures/supp_fig_a2_chosen_effort_all.png", "generated"),
    Artifact("Supplement Figure A.3", "src/analysis/figures.py", "results/appendix/figures/supp_fig_a3_wage_comparisons_all.png", "generated"),
    Artifact("Supplement Figure A.4", "src/analysis/figures.py", "results/appendix/figures/supp_fig_a4_beliefs_based_profitmax_wage.png", "generated"),
    Artifact("Supplement Figure A.5", "src/analysis/figures.py", "results/appendix/figures/supp_fig_a5_individual_effort_ge.png", "generated"),
    Artifact("Supplement Figure A.6", "src/analysis/figures.py", "results/appendix/figures/supp_fig_a6_individual_effort_prosocial.png", "generated"),
    Artifact("Supplement Figure A.7", "src/analysis/figures.py", "results/appendix/figures/supp_fig_a7_individual_effort_neutral.png", "generated"),
    Artifact("Supplement Figure A.8", "src/analysis/figures.py", "results/appendix/figures/supp_fig_a8_individual_effort_efficiency.png", "generated"),
]


def build() -> str:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Published Artifact Correspondence",
        "",
        "The published article and online supplement are the source of truth. This checklist records which repo entrypoint generates each analysis artifact.",
        "",
        "Publication: https://www.sciencedirect.com/science/article/pii/S0899825624000307?via%3Dihub",
        "",
        "| Artifact | Script source | Generated output | Status |",
        "| --- | --- | --- | --- |",
    ]
    for artifact in ARTIFACTS:
        lines.append(
            f"| {artifact.paper_artifact} | `{artifact.source}` | `{artifact.output}` | {artifact.status} |"
        )
    content = "\n".join(lines) + "\n"
    (OUTPUTS / "correspondence.md").write_text(content)
    return content


if __name__ == "__main__":
    print(build())
