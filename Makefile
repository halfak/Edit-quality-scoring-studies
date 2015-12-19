datasets/anon_edits.201612_week1.tsv:
	wget http://quarry.wmflabs.org/run/54033/output/0/tsv?download=true -qO- > \
	datasets/anon_edits.201612_week1.tsv

datasets/anon_scores.201612_week1.tsv: datasets/anon_edits.201612_week1.tsv
	cat datasets/anon_edits.201612_week1.tsv | \
	python get_scores.py https://ores.wmflabs.org enwiki damaging goodfaith reverted > \
	datasets/anon_scores.201612_week1.tsv
