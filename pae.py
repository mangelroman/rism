import re

pae_dur_dict = {
    '0' : 4.,
    '1' : 1.,
    '2' : .5,
    '3' : .03125,
    '4' : .25,
    '5' : .015625,
    '6' : .0625,
    '7' : .0078125,
    '8' : .125,
    '9' : 2.,
}

def check_measures(paedata, measure_length):
    last_duration = [0.25]
    index = 0
    measures = paedata.split('/')
    if len(measures) < 3:
        return False

    last_measure = len(measures) - 1
    for i, meas in enumerate(measures):
        length = 0
        for match in re.finditer(r'[0-9.]+|[A-G\-]|i', meas):
            if match[0].startswith('i'):
                length = measure_length
            elif match[0].startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                last_duration = []
                index = 0
                for dur in re.findall(r'\d\.*', match[0]):
                    d = pae_dur_dict[dur[0]]
                    dots = dur.count('.')
                    if dots == 1:
                        d += d / 2
                    elif dots == 2:
                        d += 3 * d / 4
                    last_duration.append(d)
            else:
                length += last_duration[index]
                index = (index + 1) % len(last_duration)
        if i == 0 or i == last_measure:
            if length > measure_length:
                return False
        elif length != measure_length:
            return False
    return True

def remove_grace_notes(paedata):
    last_octave = ''
    last_duration = ''
    grace_last_octave = None
    grace_last_duration = None

    def convert_object(matchobj):
        nonlocal last_octave
        nonlocal last_duration
        nonlocal grace_last_octave
        nonlocal grace_last_duration

        if re.fullmatch(r'[0-9.]+', matchobj[0]):
            grace_last_duration = None
            if matchobj[0] == last_duration:
                return ''
            last_duration = matchobj[0]
            return matchobj[0]
        elif re.fullmatch(r'[,\']{1,4}', matchobj[0]):
            grace_last_octave = None
            if matchobj[0] == last_octave:
                return ''
            last_octave = matchobj[0]
            return matchobj[0]
        elif re.fullmatch(r'[A-G]', matchobj[0]):
            extra = ''
            if grace_last_octave is not None:
                if grace_last_octave != last_octave:
                    extra += grace_last_octave
                    last_octave = grace_last_octave
                grace_last_octave = None
            if grace_last_duration is not None:
                if grace_last_duration != last_duration:
                    extra += grace_last_duration
                    last_duration = grace_last_duration
                grace_last_duration = None
            return extra + matchobj[0]
        elif matchobj[0].find('qq'):
            durations = re.findall(r'[0-9]\.*', matchobj[0])
            octaves = re.findall(r'[,\']{1,4}', matchobj[0])
            if durations and len(durations) > 0:
                grace_last_duration = durations[-1]
            if octaves and len(octaves) > 0:
                grace_last_octave = octaves[-1]
            return ''
        elif matchobj[0].find('q') or matchobj[0].find('g'):
            duration = re.search(r'[0-9]\.*', matchobj[0])
            if duration:
                grace_last_duration = duration[0]
            octave = re.search(r'[,\']{1,4}', matchobj[0])
            if octave:
                grace_last_octave = octave[0]
            return ''
        else:
            raise KeyError

    return re.sub(
        r"[',0-9.]*qq+.+?r|[',0-9.]*[qg][',0-9.xbn]*[A-G]|[A-G]|[0-9.]+|[',]{1,4}",
        convert_object,
        paedata
    )

def remove_invalid_ties(paedata):
    def convert_object(matchobj):
        if matchobj[1] != matchobj[5] or matchobj[1] == '-' or re.search(r"[',]", matchobj[2]) or re.search(r"[',]", matchobj[4]):
            return matchobj[1] + matchobj[2] + matchobj[4] + matchobj[5]
        return matchobj[0]

    return re.sub(r"([A-G\-])([^A-G\-]*)(\+)([^A-G\-]*)([A-G\-])", convert_object, paedata)

def clean_pae(paedict):
    # Remove RISM-specific symbols from key and keysig
    paedict['@keysig'] = re.sub(r'\[|\]', r'', paedict['@keysig'])
    paedict['@key'] = re.sub(r'\|', r'', paedict['@key'])

    if not re.fullmatch(r'(G-[1-2]|g-2|F-[3-5]|C-[1-5])', paedict['@clef']): # discard invalid clefs
        #print(f"{paedict['@start']}: BADCLEF {paedict['@clef']}")
        return None

    if paedict['@keysig'] != "" and not re.fullmatch(r'(b|x)[A-G]+', paedict['@keysig']): # discard invalid key signatures
        #print(f"{paedict['@start']}: BADKEYSIG {paedict['@keysig']}")
        return None

    if not re.fullmatch(r'(c/?|[0-9]+/[0-9]+)', paedict['@timesig']): # discard invalid time signatures
        #print(f"{paedict['@start']}: BADTIMESIG {paedict['@timesig']}")
        return None

    if paedict['@key'] != "" and not re.fullmatch(r'[A-Ga-g](#|x|b)?', paedict['@key']): # discard invalid keys
        #print(f"{paedict['@start']}: BADKEY {paedict['@key']}")
        return None

    # Canonical time signature
    paedict['@timesig'] = re.sub(r'c/', r'2/2', paedict['@timesig'])
    paedict['@timesig'] = re.sub(r'c', r'4/4', paedict['@timesig'])

    paedata = paedict['@data']

    if re.search(r'\([^\)]{2,}', paedata): # discard irregular groups
        return None

    if re.search(r'\^', paedata): # discard chords
        return None

    if re.search(r'[%@\$]', paedata): # discard changes of clef, key and time signatures
        return None

    def unroller(matchobj):
        output = matchobj[1]
        for i in range(len(matchobj[2])):
            output += matchobj[1]
        return matchobj[1]

    paedata = re.sub(r'!(.*?)!(f+)', unroller, paedata) # Unroll pattern repetitions

    paedata = re.sub(r'://:', r'/', paedata) # remove fancy barlines
    paedata = re.sub(r'://', r'/', paedata) # remove fancy barlines
    paedata = re.sub(r'//:', r'/', paedata) # remove fancy barlines
    paedata = re.sub(r'//', r'/', paedata) # remove double barlines
    paedata = re.sub(r'\(([A-G\-])\)', r'\1', paedata) # remove fermata
    paedata = re.sub(r't', r'', paedata) # remove trills
    paedata = re.sub(r'(=\d*|\(=\)|=\d=)/', r'', paedata) # remove multirest
    if re.search(r'=', paedata): # discard multirest leftovers
        #print(f"Multirest leftover at {paedict['@start']}: {paedict['@data']}")
        return None

    paedata = remove_invalid_ties(paedata)
    paedata = remove_grace_notes(paedata)
    if re.search(r'[qg]', paedata): # discard grace notes leftovers
        #print(f"Grace notes leftover at {paedict['@start']}: {paedict['@data']}")
        return None

    paedata = re.sub(r"[^A-G1-9.xbn/,'+\-{}i]", r'', paedata) # remove unsupported characters
    paedata = re.sub(r"^([^A-G\-/])/", r'/1', paedata) # remove redundant measure at the begining
    paedata = re.sub(r"([^A-G\-/}i])(/?)$", r'\2', paedata) # remove redundant characters at the end
    paedata = re.sub(r"([',]+)([^A-G',]+)([',]+)", r'\2\3', paedata) # remove redundant octaves
    paedata = re.sub(r"([xbn])([^A-Gxbn]*)([xbn])", r'\2\3', paedata) # remove redundant accidentals
    paedata = re.sub(r"([0-9.]+)([^A-G\-0-9\.]+)([0-9.]+)", r'\2\3', paedata) # remove redundant durations
    paedata = re.sub(r"([^0-9.])(\.+)", r'\1', paedata) # remove redundant dots

    num, den = paedict['@timesig'].split('/')
    measure_length = float(num) / float(den)

    if not check_measures(paedata, measure_length):
        return None

    paedict['@data'] = paedata
    return paedict