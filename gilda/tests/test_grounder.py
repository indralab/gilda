from gilda.term import Term
from gilda.grounder import Grounder, filter_for_organism
from . import appreq


gr = Grounder()


def test_grounder():
    entries = gr.lookup('kras')
    statuses = [e.status for e in entries]
    assert 'assertion' in statuses
    for entry in entries:
        if entry.status == 'assertion':
            assert entry.id == '6407', entry

    scores = gr.ground('kras')
    assert len(scores) == 1, scores
    assert appreq(scores[0].score, 0.9845), scores
    scores = gr.ground('k-ras')
    assert len(scores) == 1, scores
    assert appreq(scores[0].score, 0.9936), scores
    scores = gr.ground('KRAS')
    assert len(scores) == 1, scores
    assert appreq(scores[0].score, 1.0), scores
    scores = gr.ground('bRaf')
    assert len(scores) == 1, scores
    assert appreq(scores[0].score, 0.9936), scores


def test_grounder_bug():
    # Smoke test to make sure the 'NA' entry in grounding terms doesn't get
    # turned into a None
    gr.ground('Na')


def test_grounder_num_entries():
    entries = gr.lookup('NPM1')
    assert len(entries) == 1, entries
    entries = gr.lookup('H4')
    assert len(entries) == 5, entries


def test_grounder_depluralize():
    entries = gr.lookup('RAFs')
    assert len(entries) == 2, entries
    for entry in entries:
        assert entry.norm_text == 'raf'


def test_disambiguate_adeft():
    matches = gr.ground('IR')
    matches = gr.disambiguate('IR', matches, 'Insulin Receptor (IR)')
    for match in matches:
        assert match.disambiguation is not None
        assert match.disambiguation['type'] == 'adeft'
        assert match.disambiguation['match'] in ('grounded', 'ungrounded')
        assert match.disambiguation['score'] is not None
        if match.term.db == 'HGNC' and match.term.id == '6091':
            assert match.disambiguation['match'] == 'grounded'
            assert match.disambiguation['score'] == 1.0


def test_disambiguate_gilda():
    matches = gr.ground('NDR1')
    matches = gr.disambiguate('NDR1', matches, 'STK38')
    for match in matches:
        assert match.disambiguation['type'] == 'gilda'
        assert match.disambiguation['match'] == 'grounded'
        if match.term.db == 'HGNC' and match.term.id == '17847':
            assert match.disambiguation['score'] > 0.99
        if match.term.db == 'HGNC' and match.term.id == '7679':
            assert match.disambiguation['score'] < 0.01


def test_rank_namespace():
    matches = gr.ground('interferon-gamma')
    assert matches[0].term.db == 'HGNC'


def test_aa_synonym():
    matches = gr.ground('WN')
    assert '141447' not in {m.term.id for m in matches}

    matches = gr.ground('W-N')
    assert '141447' not in {m.term.id for m in matches}


def test_organism_filter():
    t1 = Term('x', None, None, None, None, None, None, '9606')
    t2 = Term('x', None, None, None, None, None, None, '10090')
    t3 = Term('x', None, None, None, None, None, None, None)
    terms = filter_for_organism([t1, t2, t3],
                                organisms=['9606'])
    assert len(terms) == 2, terms
    assert {t.organism for t in terms} == {None, '9606'}
    terms = filter_for_organism([t1, t2, t3],
                                organisms=['10090'])
    assert len(terms) == 2, terms
    assert {t.organism for t in terms} == {None, '10090'}
    terms = filter_for_organism([t1, t2, t3],
                                organisms=['10090', '9606'])
    assert len(terms) == 2, terms
    assert {t.organism for t in terms} == {None, '10090'}
    terms = filter_for_organism([t1, t2, t3],
                                organisms=['9606', '10090'])
    assert len(terms) == 2, terms
    assert {t.organism for t in terms} == {None, '9606'}


def test_organisms():
    matches = gr.ground('Raf1')
    assert len(matches) == 2, len(matches)
    assert {match.term.organism for match in matches}
    print(organisms)
    for match in matches:
        print(match.term)
    assert False