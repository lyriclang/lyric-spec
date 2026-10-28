# Conformance suite

Empty in S0. A case is a `.lyrs` program under `cases/<chapter>/` with its expectation in a header
(output, exit code or diagnostic code); every case carries `since: 1.0.0` or later, and every
deviation from Lyric 5 gets a failing and a passing case. The header format and the runner come
with the first milestone that can run a program (S2).
