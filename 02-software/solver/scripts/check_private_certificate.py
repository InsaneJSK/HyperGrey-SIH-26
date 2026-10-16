"""Private certificate counters are local work, never global proof evidence."""
def check(result):
    s = result['private_dual_certificate']
    assert type(s['enabled']) is bool
    for key in ('attempts', 'accepted'):
        assert type(s[key]) is int and s[key] >= 0
    assert s['accepted'] <= s['attempts']
    assert s['attempts'] <= result['distance_reopt']['calls'] + result['distance_stage']['reopt']['calls']
    if s['enabled']:
        assert result['distance_reopt']['enabled']
    else:
        assert s['attempts'] == s['accepted'] == 0
    return {'all_pass': True, **s, 'scope': __doc__}
