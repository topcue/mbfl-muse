def rank(top_n):
    with open('../Chart_1/gzoltars/Chart/1/spectra','r') as f:
        data = f.readlines()

        stmt_dict = {}
        for idx, line in enumerate(data):
            stmt_dict[idx+1] = line.strip()
    
    for idx,stmt_rank in enumerate(top_n):
        print(f'Rank {idx+1}: {stmt_dict[stmt_rank]}')

