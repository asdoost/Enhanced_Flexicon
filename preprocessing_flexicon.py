#!/usr/bin/env python3

import csv
import re

vowels = ['æ','ɒ','o','u','e','i']
consonants = ['b', 'p', 't', 'd', 'c', 'ɟ', '\u02a7', '\u02a4', 'G',
        'ʔ', 'f', 'v', 's', 'z', 'ʃ', 'ʒ', 'χ', 'h', 'm', 'n', 'l', 'r', 'j']

# Modify the list with syntactic categories that you want to remove from the file
unwanted_categories = ['Ab', 'Al', 'Exp', 'Intj', 'N2', 'N3', 'N4', 'No', 'Si']

discrepancies = {'zirbr.nɒ.me': ('zir.bær.nɒ.me', 'CVC.CVC.CV.CV'),
 'fi.to.pe.lɒjnc.ton': ('fi.to.pe.lɒnc.ton', 'CV.CV.CV.CVCC.CVC'),
 'mæʃrb.χɒ.ri': ('mæʃ.rub.χɒ.ri', 'CVC.CVC.CV.CV'),
 'ʔɒb.ʃo.ʃoi': ('ʔɒb.ʃo.ʃi', 'CVC.CV.CV'),
 'bei.ne.ʔos.tɒ.ni': ('bej.ne.ʔos.tɒ.ni', 'CVC.CV.CVC.CV.CV'),
 'be.Gei.ræz': ('be.Gej.ræz', 'CV.CVC.CVC'),
 'bei.ne.bɒn.ci': ('bej.ne.bɒn.ci', 'CVC.CV.CVC.CV'),
'bei.ne.mær.zi': ('bej.ne.mær.zi', 'CVC.CV.CVC.CV'),
'tɒim': ('tɒjm', 'CVCC'),
'tɒi.mer': ('tɒj.mer', 'CVC.CVC'),
'tæ.væG.Gof.nɒ.pæir': ('tæ.væG.Gof.nɒ.pæzir', 'CV.CVC.CVC.CV.CV.CVC'),
'ʤæusr': ('ʤæsur', 'CV.CVC'),
'hæ.GiæGt.ʃe.nɒs': ('hæ.Gi.Gæt.ʃe.nɒs', 'CV.CV.CVC.CV.CVC'),
'χoɒc.ʃu.ʔi': ('χoʃc.ʃu.ʔi', 'CVCC.CV.CV'),
'dæe.pɒ.jɒn': ('dær.pɒ.jɒn', 'CVC.CV.CVC'),
'doer.ʔof.tɒ.de': ('do.re.ʔof.tɒ.de', 'CV.CV.CVC.CV.CV'),
're.per.toɒr': ('re.per.tu.ʔɒr', 'CV.CVC.CV.CVC'),
'si.ne.mɒes.cop': ('si.ne.mɒ.ʔes.cop', 'CV.CV.CV.CVC.CVC'),
'ʃɒh.lu.lue': ('ʃɒh.lu.le', 'CVC.CV.CV'),
'ʃi.ʃie.ʃur': ('ʃi.ʃe.ʃur', 'CV.CV.CVC'),
'ʔæɒ.ceʃ': ('ʔæ.sɒ.ceʃ', 'CV.CV.CVC'),
'Gei.re.ʔen.ɟi.li.si': ('Gej.re.ʔen.ɟi.li.si', 'CVC.CV.CVC.CV.CV.CV'),
'cæm.cɒ.riɒ': ('cæm.cɒ.ri.jɒ', 'CVC.CV.CV.CV'),
'mɒ.li.jɒæt.ɟo.zɒ.ri': ('mɒ.li.jɒt.ɟo.zɒ.ri', 'CV.CV.CVC.CV.CV.CV'),
'mɒos': ('mos', 'CVC'),
'mæz.dæis.nɒ': ('mæz.dæ.jæs.nɒ', 'CVC.CV.CVC.CV'),
'mæz.dæis.nɒ.ji':('mæz.dæ.jæs.nɒ.ji', 'CVC.CV.CVC.CV.CV'),
'hie.roɟ.lif': ('hi.ro.ɟi.lif', 'CV.CV.CV.CVC')}

def preprocessing_flexicon(path='files/raw_flexicon.csv',
                            IPA=True, remove_w=True,
                            unwanted_categories=unwanted_categories,
                            starting_glottal_stop=True):

    # Load the raw_flexicon.csv file
    with open(path, 'r', encoding='utf8') as file:
        data = list(csv.reader(file))
        # Remove the header
        data = data[1:]

    # Change transcribed alphabet to API
    API_list = []
    if IPA:
        from_ = 'jAagq\'SZxykMKIC'
        to = '\u02a4ɒæɟGʔʃʒχjcmci\u02a7'
        w = 'w' if remove_w else ''
        for row in data:
            if row[2] not in unwanted_categories:
                table = row[0].maketrans(from_, to, w)
                row[0] = row[0].translate(table)
                API_list.append(row)

    # Add a glottal stop to the begining of the words starting with vowels
    glottalized_list = []
    if starting_glottal_stop:
        for row in API_list:
            if row[0][0] in vowels or (row[1][0] == 'ع' and not row[0][0].startswith('ʔ')):
                row[0] = 'ʔ' + row[0]
            glottalized_list.append(row)


    cleaned_list = []
    for row in glottalized_list:
        # Syllabify the words
        row[0] = re.sub("(?<!^)([^æɒouei][æɒouei])", ".\\1", row[0])
        # Add the "syllabic structure" column
        syl_structure = ''.join(['C' if i in consonants else 'V' if i in vowels else '.' for i in row[0]])
        row.insert(1, syl_structure)
        # Add the "number of syllables" column
        row.insert(2, syl_structure.count('.') + 1)
        # Remove discrepancies
        if row[0] in discrepancies.keys():
            row[1] = discrepancies[row[0]][1]
            row[0] = discrepancies[row[0]][0]
        cleaned_list.append(row)

    # Define the header
    header = ['Phonological Forms', 'Syllabic Structures',
              'Number of Syllables', 'Written Forms',
              'Syntactic Categories', 'Frequency', 'Stress Patterns']

    # Save the cleaned list as a csv file
    with open('files/enhanced_cleaned_flexicon.csv', 'w', encoding='utf8') as output:
        csvwriter = csv.writer(output)
        csvwriter.writerow(header)
        csvwriter.writerows(cleaned_list)

if __name__=='__main__':
    preprocessing_flexicon()
