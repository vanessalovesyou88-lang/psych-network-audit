# Input contract

Required UTF-8 files: manifest.json and adjacency.csv. Optional: centrality.csv and draft.txt.

manifest: nodes (unique ordered strings), communities (node-to-community strings, at least two groups for BEI), sample_sizes (stage-to-positive-integer mapping), missing_data (description), tolerance (absolute tolerance, 0 to .01; default .001).

adjacency: first row node,A,B,...; subsequent rows node label and weights. Both axes exactly follow manifest.nodes. Use a finite, symmetric weighted adjacency with zero diagonal. Structural tolerance is 1e-8.

centrality: header node,EI,BEI; one unique row per node. Raw signed one-step EI is row sum. Raw signed one-step BEI sums edges to nodes in other communities. All nodes are included. No z scores, normalized or two-step metrics. Export sufficient decimal precision. Without valid communities BEI comparison is skipped explicitly.

draft: plain text. Wording matches are heuristic, including negated statements. Sample sizes are self-reported records, not verified against raw data.

A minimal synthetic network: A-B=.2, A-C=-.1, B-C=.3; communities A/B=X, C=Y. EI=(.1,.5,.2); BEI=(-.1,.3,.2).
