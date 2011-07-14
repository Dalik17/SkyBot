from util import hook
import re
import math
import string

def slowExponent(x):
    return 1.3 * x * (1 - math.atan(x / 6.0) * 2 / math.pi)

def slowPow(x, y):
    return math.pow(x, slowExponent(y))

def caseShifts(s):
    s=re.sub('[^a-zA-Z]', '', s)
    s=re.sub('[A-Z]+', 'U', s)
    s=re.sub('[a-z]+', 'l', s)
    return len(s)-1

def numberShifts(s):
    s=re.sub('[^a-zA-Z0-9]', '', s)
    s=re.sub('[a-zA-Z]+', 'l', s)
    s=re.sub('[0-9]+', 'n', s)
    return len(s)-1

def punish(reasons, damage, reason):
    reasons.append((reason.strip(), damage))
    return damage
@hook.command()
def nickometer(nick):
    ".nickometer <nick> - determine the lameness of a given nick"
    nick = str(nick)
    score = 0L
    reasons = []

    specialCost = [('69', 500),
                   ('dea?th', 500),
                   ('dark', 400),
                   ('n[i1]ght', 300),
                   ('n[i1]te', 500),
                   ('fuck', 500),
                   ('sh[i1]t', 500),
                   ('coo[l1]', 500),
                   ('kew[l1]', 500),
                   ('lame', 500),
                   ('dood', 500),
                   ('dude', 500),
                   ('[l1](oo?|u)[sz]er', 500),
                   ('[l1]eet', 500),
                   ('e[l1]ite', 500),
                   ('[l1]ord', 500),
                   ('pron', 1000),
                   ('warez', 1000),
                   ('xx', 100),
                   ('\\[rkx]0', 1000),
                   ('\\0[rkx]', 1000)]

    letterNumberTranslator = string.maketrans('023457+8', 'ozeasttb')
    for special in specialCost:
        tempNick = nick
        if special[0][0] != '\\':
            tempNick = tempNick.translate(letterNumberTranslator)

        if tempNick and re.search(special[0], tempNick, re.IGNORECASE):
            score += punish(reasons, special[1], 'matched special case /%s/' %
                                                              special[0])

    # I don't really know about either of these next two statements,
    # but they don't seem to do much harm.
    # Allow Perl referencing
    nick=re.sub('^\\\\([A-Za-z])', '\1', nick);

    # C-- ain't so bad either
    nick=re.sub('^C--$', 'C', nick);

    # Punish consecutive non-alphas
    matches=re.findall('[^\w\d]{2,}',nick)
    for match in matches:
        score += punish(reasons, slowPow(10, len(match)),
                                '%s consecutive non-alphas ' % len(match))

    # Remove balanced brackets ...
    while 1:
        nickInitial = nick
        nick=re.sub('^([^()]*)(\()(.*)(\))([^()]*)$', '\1\3\5', nick, 1)
        nick=re.sub('^([^{}]*)(\{)(.*)(\})([^{}]*)$', '\1\3\5', nick, 1)
        nick=re.sub('^([^[\]]*)(\[)(.*)(\])([^[\]]*)$', '\1\3\5', nick, 1)
        if nick == nickInitial:
            break
    # ... and punish for unmatched brackets
    unmatched = re.findall('[][(){}]', nick)
    if len(unmatched) > 0:
        score += punish(reasons, slowPow(10, len(unmatched)),
                              '%s unmatched parentheses' % len(unmatched))

    # Punish k3wlt0k
    k3wlt0k_weights = (5, 5, 2, 5, 2, 3, 1, 2, 2, 2)
    for i in range(len(k3wlt0k_weights)):
        hits=re.findall(`i`, nick)
        if (hits and len(hits)>0):
            score += punish(reasons, k3wlt0k_weights[i] * len(hits) * 30,
                                '%s occurrences of %s ' % (len(hits), i))

    # An alpha caps is not lame in middle or at end, provided the first
    # alpha is caps.
    nickOriginalCase = nick
    match = re.search('^([^A-Za-z]*[A-Z].*[a-z].*?)[-_]?([A-Z])', nick)
    if match:
        nick = ''.join([nick[:match.start(2)],
                           nick[match.start(2)].lower(),
                           nick[match.start(2)+1:]])

    match = re.search('^([^A-Za-z]*)([A-Z])([a-z])', nick)
    if match:
        nick = ''.join([nick[:match.start(2)],
                           nick[match.start(2):match.end(2)].lower(),
                           nick[match.end(2):]])

    # Punish uppercase to lowercase shifts and vice-versa, modulo
    # exceptions above

    # the commented line is the equivalent of the original, but i think
    # they intended my version, otherwise, the first caps alpha will
    # still be punished
    #cshifts = caseShifts(nickOriginalCase);
    cshifts = caseShifts(nick);
    if cshifts > 1 and re.match('.*[A-Z].*', nick):
        score += punish(reasons, slowPow(9, cshifts),
                             '%s case shifts' % cshifts)

    # Punish lame endings
    if re.match('.*[XZ][^a-zA-Z]*$', nickOriginalCase):
        score += punish(reasons, 50, 'the last alphanumeric character was lame')

    # Punish letter to numeric shifts and vice-versa
    nshifts = numberShifts(nick);
    if nshifts > 1:
        score += punish(reasons, slowPow(9, nshifts),
                             '%s letter/number shifts' % nshifts)

    # Punish extraneous caps
    caps = re.findall('[A-Z]', nick)
    if caps and len(caps) > 0:
        score += punish(reasons, slowPow(7, len(caps)),
                             '%s extraneous caps' % len(caps))

    # one trailing underscore is ok. i also added a - for parasite-
    nick = re.sub('[-_]$','',nick)

    # Punish anything that's left
    remains = re.findall('[^a-zA-Z0-9]', nick)
    if remains and len(remains) > 0:
        score += punish(reasons, 50*len(remains) + slowPow(9, len(remains)),
                                 '%s extraneous symbols' % len(remains))

    # Use an appropriate function to map [0, +inf) to [0, 100)
    percentage = 100 * (1 + math.tanh((score - 400.0) / 400.0)) * \
                 (1 - 1 / (1 + score / 5.0)) / 2

    # if it's above 99.9%, show as many digits as is insteresting
    score_string=re.sub('(99\\.9*\\d|\\.\\d).*','\\1',`percentage`)
    return score_string + ": " + ", ".join([k[0] for k in reasons])

# vi: set et sta sw=4 ts=4:
