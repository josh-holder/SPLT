import sys
if __name__ == "__main__":
    seq_file_list = ["sequences/1043seq.txt","sequences/1053seq.txt"]
    sequences = []
    for seq_file in seq_file_list:
        try:
            f = open(seq_file, "r")
        except:
            print("Couldn't open file",seq_file,", does it exist?")
            sys.exit(1)

        line=f.readline()
        f.close()
        if line[0] == "[": line = line[1:]
        if line[-1] == "]": line = line[:-1]
        sequence=(line.rstrip('\n').split(', '))
        sequence=[int(ii) for ii in sequence]
        sequences.append(sequence)
    
    i = 0
    while True:
        splits = []
        for sequence in sequences:
            splits.append(sequence[i])
        
        if len(splits) != len(sequences):
            print("One sequence ended - same until split {}".format(i))
            break

        curr_split = splits[0]
        same = True
        for split in splits:
            if split != curr_split:
                same = False
                break
        
        if not same:
            print("same until split {}".format(i))
            break
        
        print(i)
        i += 1