"""
Gets ORES scores for a set of revisions.

Usage:
    get_scores <ores-url> <context> <model>... [--debug]

Options:
    <ores-url>  The base URL for an ORES instance to use
    <context>   The database name of the wiki (or other context) to score
                within.
    <model>     The name of a model to apply
    --debug     Show debug information
"""
import logging
import sys
import traceback
from itertools import islice

import docopt
import requests

import mysqltsv

logger = logging.getLogger(__name__)
logging.getLogger('requests.packages.urllib3.connectionpool').setLevel(logging.WARNING)

def main():
    args = docopt.docopt(__doc__)

    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )

    ores_url = args['<ores-url>']
    context = args['<context>']
    models = args['<model>']

    revs = mysqltsv.Reader(sys.stdin)

    run(ores_url, context, models, revs)


def run(ores_url, context, models, revs):

    headers = revs.headers + models
    writer = mysqltsv.Writer(sys.stdout, headers=headers)

    batch = list(islice(revs, 50))
    while len(batch) > 0:
        rev_scores = get_scores(ores_url, context, models, batch)

        for rev, scores in zip(batch, rev_scores):
            sys.stderr.write(".")
            sys.stderr.flush()
            writer.write(list(rev.values()) + scores)

        batch = list(islice(revs, 50))


def get_scores(ores_url, context, models, revs):
    response = requests.get("/".join([ores_url, "scores", context]) + "/",
                            params={'models': "|".join(models),
                                    'revids': "|".join(r.rev_id for r in revs)})
    try:
        response_doc = response.json()

        for rev in revs:
            try:
                rev_scores_doc = response_doc[str(rev.rev_id)]
                scores = list(read_scores(rev.rev_id, rev_scores_doc, models))
                yield scores
            except RuntimeError:
                logger.warn("Could not get scores for {0}".format(rev.rev_id))
                logger.warn(traceback.format_exc())
                yield [None for m in models]

    except ValueError:
        logger.error("Couldn't interpret response as a JSON doc.")
        logger.error(response.content[:1000])


def read_scores(rev_id, rev_scores_doc, models):

    for model in models:
        if 'error' in rev_scores_doc[model]:
            logger.warn("Could not get scores for {0}{1}"
                        .format(model, rev_id))
            logger.warn(rev_scores_doc[model]['type'] + ": " +
                        rev_scores_doc[model]['message'])
            yield None
        else:
            yield rev_scores_doc[model]['probability']['true']


if __name__ == "__main__":
    main()
