import math

from granatum_sdk import Granatum, guess_gene_id_type, convert_gene_ids
import zgsea


def main():
    gn = Granatum()

    gene_scores = gn.get_import("gene_scores")
    species = gn.get_arg("species")
    gset_group_id = gn.get_arg("gset_group_id")
    n_repeats = gn.get_arg("n_repeats")
    alterChoice = gn.get_arg("alterChoice")

    if alterChoice=="pos":
        gene_scores = dict(filter(lambda elem: elem[1] >= 0.0, gene_scores.items()))
    elif alterChoice=="neg":
        gene_scores = dict(filter(lambda elem: elem[1] < 0.0, gene_scores.items()))
        gene_scores = { k: abs(v) for k, v in gene_scores.items() }

    gene_ids = gene_scores.keys()
    gene_scores = gene_scores.values()

    gene_id_type = guess_gene_id_type(list(gene_ids)[:5])
    if gene_id_type != 'symbol':
        gene_ids = convert_gene_ids(gene_ids, gene_id_type, 'symbol', species)

    if species == "human":
        pass
    elif species == "mouse":
        gene_ids = zgsea.to_human_homolog(gene_ids, "mouse")
    else:
        raise ValueError()

    result_df = zgsea.gsea(gene_ids, gene_scores, gset_group_id, n_repeats=n_repeats)
    if result_df is None:
        gn.add_markdown('No gene set is enriched with your given genes.')
    else:
        result_df = result_df[["gset_name", "gset_size", "nes", "p_val", "fdr"]]
        gn.add_pandas_df(result_df)
        gn.export(result_df.to_csv(index=False), 'gsea_results.csv', kind='raw', meta=None, raw=True)

    gn.commit()


if __name__ == "__main__":
    main()
