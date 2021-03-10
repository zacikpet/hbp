from decay_a import nlp_decay_a

with open('decay_a/text.txt') as input_file:
    with open('particles/text.txt', 'w') as output_file:
        for line in input_file:
            doc = nlp_decay_a(line)
            for ent in doc.ents:
                output_file.write(ent.text + '\n')
