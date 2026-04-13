Implement multi-omics and bioinformatics analyses for clinical research including differential expression, pathway analysis, Mendelian randomization, and metabolomics.

User input: $ARGUMENTS

## Instructions

### 1. Analysis Type Selection

| Analysis | Input Data | Key Output |
|----------|-----------|------------|
| **Differential Expression** | RNA-seq count matrix | DE gene list, volcano plot |
| **WGCNA** | Expression matrix (bulk) | Co-expression modules, hub genes |
| **Pathway Enrichment (GSEA/ORA)** | Gene list or ranked list | Enriched GO/KEGG pathways |
| **Mendelian Randomization** | GWAS summary statistics | Causal effect estimate |
| **Polygenic Risk Score** | GWAS + target genotypes | PRS per individual |
| **Metabolomics** | Metabolite intensity matrix | OPLS-DA, biomarker panel |
| **Single-cell RNA-seq** | scRNA-seq count matrix | Cell clusters, markers |

### 2. Input Data Formats

**RNA-seq**:
```
count_matrix: genes x samples (raw counts for DESeq2, TPM/FPKM for WGCNA)
metadata: sample-level annotations (group, batch, covariates)
```

**GWAS summary statistics** (for MR):
```
DataFrame: SNP, beta, se, p_value, effect_allele, other_allele, eaf
```

**Metabolomics**:
```
intensity_matrix: samples x metabolites (log-transformed, normalized)
metadata: sample groups, covariates
```

### 3. Differential Expression Analysis

```python
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

def differential_expression_deseq2_style(count_matrix, metadata, group_col,
                                          case_label, control_label,
                                          alpha=0.05, lfc_threshold=1.0):
    """Differential expression analysis (DESeq2-like approach in Python).
    For production use, consider pydeseq2 or rpy2 with DESeq2.

    Input:
        count_matrix: pd.DataFrame, genes (rows) x samples (columns), raw counts
        metadata: pd.DataFrame with sample info, indexed by sample names
        group_col: column in metadata with group labels
        case_label, control_label: group identifiers
    Output:
        de_results: DataFrame with log2FC, p-value, padj, significance
        volcano_plot: matplotlib Figure
    """
    # Using pydeseq2 (pip install pydeseq2)
    from pydeseq2.dds import DeseqDataSet
    from pydeseq2.ds import DeseqStats

    # Subset to case and control
    samples = metadata[metadata[group_col].isin([case_label, control_label])].index
    counts = count_matrix[samples].T  # samples x genes for pydeseq2
    meta = metadata.loc[samples]

    dds = DeseqDataSet(counts=counts, metadata=meta, design_factors=group_col)
    dds.deseq2()

    stat_res = DeseqStats(dds, contrast=[group_col, case_label, control_label])
    stat_res.summary()
    results = stat_res.results_df

    # Significance annotation
    results['significant'] = (
        (results['padj'] < alpha) & (abs(results['log2FoldChange']) > lfc_threshold)
    )
    results['direction'] = np.where(results['log2FoldChange'] > 0, 'Up', 'Down')

    n_up = ((results['significant']) & (results['direction'] == 'Up')).sum()
    n_down = ((results['significant']) & (results['direction'] == 'Down')).sum()
    print(f"=== Differential Expression Results ===")
    print(f"Total genes tested: {len(results)}")
    print(f"Significant (padj<{alpha}, |log2FC|>{lfc_threshold}): {results['significant'].sum()}")
    print(f"  Upregulated: {n_up}")
    print(f"  Downregulated: {n_down}")

    # Volcano plot
    fig, ax = plt.subplots(figsize=(8, 6))
    non_sig = results[~results['significant']]
    sig_up = results[(results['significant']) & (results['direction'] == 'Up')]
    sig_down = results[(results['significant']) & (results['direction'] == 'Down')]

    ax.scatter(non_sig['log2FoldChange'], -np.log10(non_sig['padj']),
              c='gray', alpha=0.3, s=5)
    ax.scatter(sig_up['log2FoldChange'], -np.log10(sig_up['padj']),
              c='red', alpha=0.5, s=10, label=f'Up ({n_up})')
    ax.scatter(sig_down['log2FoldChange'], -np.log10(sig_down['padj']),
              c='blue', alpha=0.5, s=10, label=f'Down ({n_down})')

    ax.axhline(-np.log10(alpha), color='gray', linestyle='--', alpha=0.5)
    ax.axvline(lfc_threshold, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(-lfc_threshold, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('log2 Fold Change')
    ax.set_ylabel('-log10(adjusted P-value)')
    ax.set_title('Volcano Plot')
    ax.legend()
    plt.tight_layout()

    return results, fig
```

### 4. WGCNA (Weighted Gene Co-expression Network Analysis)

```python
def run_wgcna(expression_matrix, metadata, trait_col, soft_power=None):
    """WGCNA-style co-expression analysis.

    Input:
        expression_matrix: pd.DataFrame, samples (rows) x genes (columns),
                          normalized (TPM/FPKM, variance-filtered top 5000 genes)
        metadata: pd.DataFrame with clinical trait
        trait_col: column in metadata for module-trait correlation
    Output:
        modules: dict of module_color -> list of genes
        module_trait_cor: DataFrame of module-trait correlations
    """
    # For full WGCNA, use rpy2 with R's WGCNA package or PyWGCNA
    # Below is a simplified Python approach

    from sklearn.metrics import pairwise_distances
    from scipy.cluster.hierarchy import linkage, fcluster, dendrogram
    from scipy.stats import pearsonr

    # Step 1: Soft-thresholding power selection
    if soft_power is None:
        # Scale-free topology fit
        powers = range(1, 21)
        fit_indices = []
        for p in powers:
            cor_mat = np.corrcoef(expression_matrix.values.T)
            adj = np.abs(cor_mat) ** p
            k = adj.sum(axis=0) - 1
            # Scale-free topology fit (R² of log(k) vs log(p(k)))
            hist, bin_edges = np.histogram(k, bins=30)
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            mask = hist > 0
            if mask.sum() > 2:
                r2 = pearsonr(np.log10(bin_centers[mask] + 1),
                             np.log10(hist[mask] + 1))[0] ** 2
            else:
                r2 = 0
            fit_indices.append(r2)
        soft_power = list(powers)[np.argmax(np.array(fit_indices) > 0.8)]
        print(f"Selected soft power: {soft_power}")

    # Step 2: Adjacency and TOM
    cor_mat = np.corrcoef(expression_matrix.values.T)
    adjacency = np.abs(cor_mat) ** soft_power

    # Simplified TOM (Topological Overlap Matrix)
    # Full TOM is computationally intensive; use approximation
    tom = adjacency  # placeholder; for real analysis use R WGCNA
    dissimilarity = 1 - tom

    # Step 3: Hierarchical clustering
    np.fill_diagonal(dissimilarity, 0)
    condensed = dissimilarity[np.triu_indices_from(dissimilarity, k=1)]
    Z = linkage(condensed, method='average')
    module_labels = fcluster(Z, t=0.85, criterion='distance')

    genes = expression_matrix.columns
    modules = {}
    for label in np.unique(module_labels):
        module_genes = genes[module_labels == label].tolist()
        modules[f'Module_{label}'] = module_genes

    print(f"=== WGCNA Results ===")
    print(f"Number of modules: {len(modules)}")
    for name, gene_list in modules.items():
        print(f"  {name}: {len(gene_list)} genes")

    # Step 4: Module-trait correlation
    trait = metadata[trait_col].values
    module_eigengenes = {}
    correlations = []
    for name, gene_list in modules.items():
        # Module eigengene = 1st PC
        from sklearn.decomposition import PCA
        subset = expression_matrix[gene_list].values
        if subset.shape[1] > 1:
            pca = PCA(n_components=1)
            me = pca.fit_transform(subset).flatten()
        else:
            me = subset.flatten()
        module_eigengenes[name] = me
        r, p = pearsonr(me, trait)
        correlations.append({'module': name, 'n_genes': len(gene_list),
                           'correlation': r, 'p_value': p})

    cor_df = pd.DataFrame(correlations).sort_values('p_value')
    print(f"\nModule-Trait Correlations ({trait_col}):")
    print(cor_df.to_string(index=False))

    return modules, cor_df, module_eigengenes
```

### 5. Pathway Enrichment Analysis (GSEA / ORA)

```python
def gene_set_enrichment(gene_list, ranked_list=None, organism='human',
                        method='ora', gene_sets='KEGG_2021_Human'):
    """Gene Set Enrichment Analysis using gseapy.

    Input:
        gene_list: list of gene symbols (for ORA)
        ranked_list: pd.Series with gene symbols as index, rank metric as values (for GSEA)
        method: 'ora' (Over-Representation Analysis) | 'gsea' (Gene Set Enrichment)
        gene_sets: 'KEGG_2021_Human', 'GO_Biological_Process_2023', etc.
    Output:
        enrichment results DataFrame, enrichment plot
    """
    import gseapy as gp

    if method == 'ora':
        enr = gp.enrich(
            gene_list=gene_list,
            gene_sets=gene_sets,
            organism=organism,
            outdir=None,
            cutoff=0.05,
        )
        results = enr.results
    elif method == 'gsea':
        enr = gp.prerank(
            rnk=ranked_list,
            gene_sets=gene_sets,
            outdir=None,
            min_size=15,
            max_size=500,
            permutation_num=1000,
            seed=42,
        )
        results = enr.res2d

    # Filter significant
    sig = results[results['Adjusted P-value'] < 0.05].head(20)
    print(f"=== Pathway Enrichment ({method.upper()}) ===")
    print(f"Significant pathways (FDR < 0.05): {len(sig)}")

    # Dot plot
    if len(sig) > 0:
        fig, ax = plt.subplots(figsize=(10, max(4, len(sig) * 0.3)))
        sig_sorted = sig.sort_values('Adjusted P-value')
        y_pos = range(len(sig_sorted))

        sizes = sig_sorted['Overlap'].apply(
            lambda x: int(x.split('/')[0]) if isinstance(x, str) else x
        ).values if 'Overlap' in sig_sorted.columns else np.ones(len(sig_sorted)) * 50

        scatter = ax.scatter(
            -np.log10(sig_sorted['Adjusted P-value']),
            y_pos, s=sizes * 3, c=sig_sorted['Adjusted P-value'],
            cmap='RdYlBu', edgecolors='black', linewidths=0.5
        )
        ax.set_yticks(list(y_pos))
        ax.set_yticklabels(sig_sorted['Term'].values)
        ax.set_xlabel('-log10(Adjusted P-value)')
        ax.set_title(f'Top Enriched Pathways ({gene_sets})')
        plt.colorbar(scatter, label='Adjusted P-value')
        plt.tight_layout()
    else:
        fig = None

    return results, fig
```

### 6. Mendelian Randomization

```python
def mendelian_randomization(exposure_gwas, outcome_gwas, method='ivw',
                            p_threshold=5e-8, r2_threshold=0.001):
    """Two-sample Mendelian Randomization.

    Input:
        exposure_gwas: pd.DataFrame with columns:
            SNP, beta_exp, se_exp, p_exp, effect_allele, other_allele, eaf
        outcome_gwas: pd.DataFrame with columns:
            SNP, beta_out, se_out, p_out, effect_allele, other_allele
        method: 'ivw' | 'egger' | 'weighted_median' | 'all'
    Output:
        MR estimates with CI, heterogeneity test, pleiotropy test
    """
    # Step 1: Select instruments (genome-wide significant, LD-independent)
    instruments = exposure_gwas[exposure_gwas['p_exp'] < p_threshold].copy()
    print(f"Instruments before LD pruning: {len(instruments)}")
    # LD pruning would require reference panel; simplified here

    # Step 2: Harmonize
    merged = instruments.merge(outcome_gwas, on='SNP', suffixes=('_exp', '_out'))
    # Align effect alleles
    flip = merged['effect_allele_exp'] != merged['effect_allele_out']
    merged.loc[flip, 'beta_out'] = -merged.loc[flip, 'beta_out']
    print(f"Harmonized instruments: {len(merged)}")

    beta_exp = merged['beta_exp'].values
    beta_out = merged['beta_out'].values
    se_exp = merged['se_exp'].values
    se_out = merged['se_out'].values

    results = {}

    # IVW (Inverse-Variance Weighted)
    w = 1 / se_out**2
    beta_ivw = np.sum(w * beta_exp * beta_out) / np.sum(w * beta_exp**2)
    se_ivw = np.sqrt(1 / np.sum(w * beta_exp**2))
    p_ivw = 2 * stats.norm.sf(abs(beta_ivw / se_ivw))
    results['IVW'] = {
        'beta': beta_ivw,
        'se': se_ivw,
        'p': p_ivw,
        'ci_lower': beta_ivw - 1.96 * se_ivw,
        'ci_upper': beta_ivw + 1.96 * se_ivw,
        'OR': np.exp(beta_ivw),
        'OR_ci': (np.exp(beta_ivw - 1.96 * se_ivw), np.exp(beta_ivw + 1.96 * se_ivw)),
    }

    # MR-Egger
    from scipy.stats import linregress
    slope, intercept, r, p_egger_slope, se_slope = linregress(beta_exp, beta_out)
    # Egger intercept test for pleiotropy
    se_intercept = se_slope * np.sqrt(np.mean(beta_exp**2))
    p_intercept = 2 * stats.norm.sf(abs(intercept / se_intercept))
    results['MR-Egger'] = {
        'beta': slope,
        'se': se_slope,
        'p': p_egger_slope,
        'intercept': intercept,
        'intercept_p': p_intercept,
        'OR': np.exp(slope),
    }

    # Weighted Median
    def weighted_median_mr(bx, by, sx, sy):
        ratio = by / bx
        weights = 1 / (sy**2 / bx**2)
        weights = weights / weights.sum()
        order = np.argsort(ratio)
        ratio_sorted = ratio[order]
        weights_sorted = weights[order]
        cum_weights = np.cumsum(weights_sorted)
        idx = np.searchsorted(cum_weights, 0.5)
        return ratio_sorted[min(idx, len(ratio_sorted)-1)]

    beta_wm = weighted_median_mr(beta_exp, beta_out, se_exp, se_out)
    # Bootstrap SE
    boot_betas = []
    for i in range(1000):
        idx = np.random.choice(len(beta_exp), len(beta_exp), replace=True)
        b = weighted_median_mr(beta_exp[idx], beta_out[idx], se_exp[idx], se_out[idx])
        boot_betas.append(b)
    se_wm = np.std(boot_betas)
    results['Weighted Median'] = {
        'beta': beta_wm, 'se': se_wm,
        'p': 2 * stats.norm.sf(abs(beta_wm / se_wm)),
        'OR': np.exp(beta_wm),
    }

    # Cochran's Q (heterogeneity)
    q_stat = np.sum(w * (beta_out - beta_ivw * beta_exp)**2)
    q_p = 1 - stats.chi2.cdf(q_stat, len(beta_exp) - 1)

    print("=== Mendelian Randomization Results ===")
    print(f"Number of instruments: {len(merged)}")
    for name, res in results.items():
        print(f"\n{name}:")
        print(f"  Beta: {res['beta']:.4f} (SE: {res['se']:.4f})")
        print(f"  OR: {res['OR']:.4f}")
        print(f"  P-value: {res['p']:.2e}")
        if 'intercept' in res:
            print(f"  Egger intercept: {res['intercept']:.4f} "
                  f"(P={res['intercept_p']:.4f}) "
                  f"{'[pleiotropy detected]' if res['intercept_p'] < 0.05 else '[no pleiotropy]'}")
    print(f"\nHeterogeneity: Q={q_stat:.2f}, P={q_p:.4f}")

    # Scatter plot
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.errorbar(beta_exp, beta_out, xerr=1.96*se_exp, yerr=1.96*se_out,
               fmt='o', color='steelblue', alpha=0.5, markersize=5)
    x_range = np.array([beta_exp.min(), beta_exp.max()])
    ax.plot(x_range, results['IVW']['beta'] * x_range, 'r-', label='IVW')
    ax.plot(x_range, results['MR-Egger']['beta'] * x_range +
            results['MR-Egger']['intercept'], 'g--', label='MR-Egger')
    ax.axhline(0, color='gray', linestyle=':', alpha=0.5)
    ax.axvline(0, color='gray', linestyle=':', alpha=0.5)
    ax.set_xlabel('SNP effect on exposure')
    ax.set_ylabel('SNP effect on outcome')
    ax.set_title('MR Scatter Plot')
    ax.legend()
    plt.tight_layout()

    return results, fig


def metabolomics_opls_da(intensity_matrix, group_labels, n_components=2):
    """OPLS-DA for metabolomics data.

    Input:
        intensity_matrix: pd.DataFrame, samples x metabolites (log-transformed)
        group_labels: array-like, group membership (0/1)
    Output:
        scores plot, VIP scores, significant metabolites
    """
    from sklearn.cross_decomposition import PLSRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.model_selection import cross_val_score

    X = StandardScaler().fit_transform(intensity_matrix.values)
    y = np.array(group_labels)

    # PLS-DA (OPLS-DA requires specialized package; PLS-DA as approximation)
    pls = PLSRegression(n_components=n_components)
    pls.fit(X, y)

    # Cross-validation
    cv_scores = cross_val_score(
        PLSRegression(n_components=n_components), X, y, cv=5, scoring='r2'
    )
    q2 = cv_scores.mean()

    # VIP scores
    t = pls.x_scores_
    w = pls.x_weights_
    q = pls.y_loadings_
    p_features = X.shape[1]
    vip = np.zeros(p_features)
    for i in range(p_features):
        ss = 0
        for j in range(n_components):
            ss += (q[j]**2 * np.dot(t[:, j], t[:, j])) * (w[i, j] / np.linalg.norm(w[:, j]))**2
        vip[i] = np.sqrt(p_features * ss / sum(q[j]**2 * np.dot(t[:, j], t[:, j])
                                                 for j in range(n_components)))

    vip_df = pd.DataFrame({
        'metabolite': intensity_matrix.columns,
        'VIP': vip
    }).sort_values('VIP', ascending=False)

    print(f"=== OPLS-DA / PLS-DA Results ===")
    print(f"Q2 (CV): {q2:.4f}")
    print(f"VIP > 1.0: {(vip > 1.0).sum()} metabolites")
    print(f"\nTop 10 discriminating metabolites:")
    print(vip_df.head(10).to_string(index=False))

    # Scores plot
    fig, ax = plt.subplots(figsize=(7, 6))
    for label in np.unique(y):
        mask = y == label
        ax.scatter(t[mask, 0], t[mask, 1], label=f'Group {label}', alpha=0.7, s=50)
    ax.set_xlabel('Component 1')
    ax.set_ylabel('Component 2')
    ax.set_title(f'PLS-DA Scores Plot (Q2={q2:.3f})')
    ax.legend()
    plt.tight_layout()

    return vip_df, fig
```

### 7. Output Summary by Analysis Type

| Analysis | Primary Output | Visualization | Reporting Guideline |
|----------|---------------|--------------|---------------------|
| DE Analysis | DE gene table, fold changes | Volcano plot, heatmap | MIQE (qPCR), MINSEQE (seq) |
| WGCNA | Module-trait correlations, hub genes | Dendrogram, module-trait heatmap | — |
| Pathway | Enriched terms, FDR-adjusted p | Dot plot, GSEA enrichment plot | — |
| MR | Causal OR/beta, sensitivity analyses | Scatter plot, forest plot | STROBE-MR |
| Metabolomics | Discriminating metabolites, VIP | Scores plot, VIP bar plot | — |
| scRNA-seq | Cell clusters, marker genes | UMAP, dot plot | — |

## Output
- Analysis-specific results table
- Visualization (volcano plot, scores plot, scatter plot, etc.)
- Statistical significance with multiple testing correction
- Pathway/functional interpretation
- Sensitivity analyses where applicable
- Complete executable Python code
- Relevant reporting checklist items
