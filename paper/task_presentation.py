"""Tasks for compiling the paper and presentation(s)."""
import os
import shutil

import crime_patterns.config as config
import pytask
from pytask_latex import compilation_steps as cs

## define paths
src = config.SRC
bld = config.BLD
paper_dir = config.PAPER_DIR
data_raw = src / "data"
data_clean = bld / "python" / "data"
results_dir = bld / "python" / "results"
models_dir = bld / "python" / "models"
plots_dir = bld / "python" / "figures"
tables_dir = bld / "python" / "tables"

documents = ["crime_patterns_pres"]

for document in documents:

    @pytask.mark.depends_on(
        {
            "burglary_incidents": os.path.join(plots_dir, "burglary_incidents.png"),
            "burglary_hotspots": os.path.join(plots_dir, "burglary_hotspots.png"),
            "burglary_clusters": os.path.join(plots_dir, "burglary_clusters.png"),
            "imd_scores_lsoa": os.path.join(plots_dir, "imd_scores_lsoa.png"),
            "imd_scores_ward": os.path.join(plots_dir, "imd_scores_ward.png"),
            "burglary_ward": os.path.join(plots_dir, "burglary_ward.png"),
            "moran_scatter": os.path.join(plots_dir, "moran_scatter.png"),
            "moran_distribution": os.path.join(plots_dir, "moran_distribution.png"),
            "burglary_ward_lag": os.path.join(plots_dir, "burglary_ward_lag.png"),
            "weights_matrix_ward": os.path.join(plots_dir, "weights_matrix_ward.png"),
            "summary_spatial_ols_tex": os.path.join(
                tables_dir,
                "model_spatial_ols_summary.tex",
            ),
            "spat_diag_ols_tex": os.path.join(
                tables_dir,
                "spat_diag_ols_tex.tex",
            ),
            "summary_spatial_ml_lag_tex": os.path.join(
                tables_dir,
                "model_spatial_ml_lag_summary.tex",
            ),
            "summary_spatial_ml_error_tex": os.path.join(
                tables_dir,
                "model_spatial_ml_error_summary.tex",
            ),
            "ml_lag_stats_tex": os.path.join(
                tables_dir,
                "ml_lag_stats.tex",
            ),
            "ml_error_stats_tex": os.path.join(
                tables_dir,
                "ml_error_stats.tex",
            ),
        },
    )
    @pytask.mark.latex(
        script=paper_dir / f"{document}.tex",
        document=bld / "latex" / f"{document}.pdf",
        compilation_steps=cs.latexmk(
            options=("--pdf", "--interaction=nonstopmode", "--synctex=1", "--cd"),
        ),
    )
    @pytask.mark.task(id=document)
    def task_compile_document():
        """Compile the document specified in the latex decorator."""

    kwargs = {
        "depends_on": bld / "latex" / f"{document}.pdf",
        "produces": bld.parent.resolve() / f"{document}.pdf",
    }

    @pytask.mark.task(id=document, kwargs=kwargs)
    def task_copy_to_root(depends_on, produces):
        """Copy a document to the root directory for easier retrieval."""
        shutil.copy(depends_on, produces)
