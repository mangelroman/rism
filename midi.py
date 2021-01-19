midi_instrument_names = [
    'Acoustic Grand Piano',
    'Bright Acoustic Piano',
    'Electric Grand Piano',
    'Honky-tonk Piano',
    'Electric Piano 1',
    'Electric Piano 2',
    'Harpsichord',
    'Clavi',
    'Celesta',
    'Glockenspiel',
    'Music Box',
    'Vibraphone',
    'Marimba',
    'Xylophone',
    'Tubular Bells',
    'Dulcimer',
    'Drawbar Organ',
    'Percussive Organ',
    'Rock Organ',
    'Church Organ',
    'Reed Organ',
    'Accordion',
    'Harmonica',
    'Tango Accordion',
    'Acoustic Guitar (nylon)',
    'Acoustic Guitar (steel)',
    'Electric Guitar (jazz)',
    'Electric Guitar (clean)',
    'Electric Guitar (muted)',
    'Overdriven Guitar',
    'Distortion Guitar',
    'Guitar harmonics',
    'Acoustic Bass',
    'Electric Bass (finger)',
    'Electric Bass (pick)',
    'Fretless Bass',
    'Slap Bass 1',
    'Slap Bass 2',
    'Synth Bass 1',
    'Synth Bass 2',
    'Violin',
    'Viola',
    'Cello',
    'Contrabass',
    'Tremolo Strings',
    'Pizzicato Strings',
    'Orchestral Harp',
    'Timpani',
    'String Ensemble 1',
    'String Ensemble 2',
    'SynthStrings 1',
    'SynthStrings 2',
    'Choir Aahs',
    'Voice Oohs',
    'Synth Voice',
    'Orchestra Hit',
    'Trumpet',
    'Trombone',
    'Tuba',
    'Muted Trumpet',
    'French Horn',
    'Brass Section',
    'SynthBrass 1',
    'SynthBrass 2',
    'Soprano Sax',
    'Alto Sax',
    'Tenor Sax',
    'Baritone Sax',
    'Oboe',
    'English Horn',
    'Bassoon',
    'Clarinet',
    'Piccolo',
    'Flute',
    'Recorder',
    'Pan Flute',
    'Blown Bottle',
    'Shakuhachi',
    'Whistle',
    'Ocarina',
    'Lead1 (square)',
    'Lead2 (sawtooth)',
    'Lead3 (calliope)',
    'Lead4 (chiff)',
    'Lead5 (charang)',
    'Lead6 (voice)',
    'Lead7 (fifths)',
    'Lead8 (bass + lead)',
    'Pad1 (new age)',
    'Pad2 (warm)',
    'Pad3 (polysynth)',
    'Pad4 (choir)',
    'Pad5 (bowed)',
    'Pad6 (metallic)',
    'Pad7 (halo)',
    'Pad8 (sweep)',
    'FX1 (rain)',
    'FX2 (soundtrack)',
    'FX 3 (crystal)',
    'FX 4 (atmosphere)',
    'FX 5 (brightness)',
    'FX 6 (goblins)',
    'FX 7 (echoes)',
    'FX 8 (sci-fi)',
    'Sitar',
    'Banjo',
    'Shamisen',
    'Koto',
    'Kalimba',
    'Bag pipe',
    'Fiddle',
    'Shanai',
    'Tinkle Bell',
    'Agogo',
    'Steel Drums',
    'Woodblock',
    'Taiko Drum',
    'Melodic Tom',
    'Synth Drum',
    'Reverse Cymbal',
    'Guitar Fret Noise',
    'Breath Noise',
    'Seashore',
    'Bird Tweet',
    'Telephone Ring',
    'Helicopter',
    'Applause',
    'Gunshot',
]

def get_midi_instrument_name(i):
    return midi_instrument_names[i]

def get_midi_instrument(i):
    if i.startswith('pf'):
        # Piano
        return 0
    if i.startswith('cemb') or i.startswith('clav') or i.startswith('hpcd'):
        # Harpsichord
        return 6
    if i.startswith('org'):
        # Church Organ
        return 19
    if i.startswith('guit'):
        # Guitar
        return 24
    if i.startswith('vla'):
        # Viola
        return 41
    if i.startswith('vlc'):
        # Cello
        return 42
    if i.startswith('vlne') or i.startswith('cb'):
        # Contrabass
        return 43
    if i.startswith('vl'):
        # Violin
        return 40
    if i.startswith('arp'):
        # Harp
        return 46
    if i.startswith('Coro'):
        # Choir
        return 52
    if i.startswith('trb'):
        # Trombone
        return 57
    if i.startswith('tr') or i.startswith('clno'):
        # Trumpet
        return 56
    if i.startswith('cor'):
        # Horn
        return 60
    if i.startswith('ob'):
        # Oboe
        return 68
    if i.startswith('cor inglese'):
        # English Horn
        return 69
    if i.startswith('fag') or i.startswith('contra-fag'):
        # Bassoon
        return 70
    if i.startswith('cl'):
        # Clarinet
        return 71
    if i.startswith('fl.picc') or i.startswith('fl picc'):
        # Piccolo
        return 72
    if i.startswith('fl'):
        # Flute
        return 73

    # Everything else defaults to piano
    return 0